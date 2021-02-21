import asyncio
from enum import Enum

from sqlalchemy import func, and_

from app.game.answer.schemas import AnswerCreateSchema
from app.game.question.schemas import QuestionGetSchema, QuestionSchema
from app.settings import config
from app.vk.accessor import send_message_to_vk, get_conversation_members
from app.vk.utils import bot_call

from app.store.database.models import (
    GameSession,
    SessionScores,
    User,
    Question,
    Answer,
)


class Commands(Enum):
    start_game = 'начать игру'
    stop_game = 'остановить игру'
    game_info = 'информация об игре'
    bot_info = 'список команд'


class JeopardyBot:
    def __init__(self):

        self.delay = 10  # seconds
        self.max_question = 3
        # todo: костыль?
        asyncio.get_event_loop().run_until_complete(self.connect())

    @staticmethod
    async def find_unfinished_game(chat_id):
        conditions = list()

        conditions.append(GameSession.chat_id == chat_id)
        conditions.append(GameSession.is_finished == False)

        game = await (
            GameSession.query
            .where(and_(*conditions))
            .gino.first()
        )
        if game:
            return game
        return None

    @staticmethod
    async def connect():
        from app.store.database.models import db

        await db.set_bind(config['postgres']['database_url'])
        await db.gino.create_all()

    async def create_game(self, message) -> GameSession:
        # рандомим вопросы для игры и создаём новую сессию
        questions = await (
            Question.query
            .order_by(func.random())
            .limit(self.max_question)
            .gino.all()
        )
        # берём айдишники вопросов
        questions = QuestionGetSchema(many=True).dump(questions)
        questions = [q['id'] for q in questions]
        new_game_session = await GameSession.create(
            chat_id=message["peer_id"],
            questions=questions,
            last_question_id=0,
            is_finished=False,
        )

        # создаём юзера, если его нет ...
        users = list()
        response = await get_conversation_members(message)
        members = response['response']['profiles']

        for member in members:
            user = await User.query.where(User.user_id == member['id']).gino.first()
            if not user:
                user = await User.create(
                    user_id=member['id'],
                    firstname=member['first_name'],
                    lastname=member['last_name'],
                    score=0,
                )
            users.append(user)

        # ... и добавляем всех участников беседы в игровую сессию
        for user in users:
            await SessionScores.create(
                session_id=new_game_session.id,
                user_id=user.user_id,
                score=0,
            )

        message['text'] = f"Ок, начинаем сессию номер {new_game_session.id}."
        await send_message_to_vk(event=message)

        return new_game_session

    async def play_game(self, game: GameSession):
        current_question_idx = game.last_question_id

        await self.ask_question(game.id, current_question_idx)

    async def ask_question(self, game_id: int, question_idx: int):
        game = await GameSession.get(game_id)
        message = {
            'peer_id': game.chat_id,
        }

        if game.last_question_id == self.max_question:
            await game.update(is_finished=True).apply()
            message['text'] = 'Игра окончена.'
            await send_message_to_vk(event=message)
            await self.game_info()

        else:
            question = dict()
            question_id = game.questions[question_idx]
            qstn = await Question.get(question_id)
            qstn = QuestionSchema().dump(qstn)
            answers = await (
                Answer.load()
                .query.where(Answer.question_id == question_id)
                .gino.all()
            )
            answers = AnswerCreateSchema(many=True).dump(answers)

            question.update({
                'question': qstn['title'],
                'theme': qstn['theme'],
                'answers': answers,
            })

            template = \
                """
                Тема: {theme}
                {question}
    
                a. {}
                b. {}
                c. {}
                d. {}
                """

            message.update({
                'text': template.format(
                    theme=question['theme'],
                    question=question['question'],
                    *answers,
                )
            })
            await send_message_to_vk(event=message)

            asyncio.create_task(self.task(game_id, question_idx))  # -------------------------------------------------!

    async def receive_answer(self, chat_id: int, message_text: str):
        """
        если есть игра:
            если ответ правильный:
                начислить очки
                ask_question(ид_сессии, номер следующего вопроса)
            иначе:
                снять очки
        иначе:
            отвечаем на глупость
        """
        # todo: check duplicates
        message = dict()
        message['peer_id'] = chat_id

        game = await self.find_unfinished_game(chat_id)
        if game:
            question_id = game.questions[game.last_question_id]
            answers = await (
                Answer.load()
                .query.where(Answer.question_id == question_id)
                .gino.all()
            )
            answers = AnswerCreateSchema(many=True).dump(answers)
            right_answer = ''
            for answer in answers:
                if answer['is_right']:
                    right_answer = answer['title']
                    break

            if message_text == right_answer:
                # todo
                # session_scores = await (
                #     SessionScores.load()
                #     .query.where(Answer.question_id == question_id)
                #     .gino.all()
                # )
                message['text'] = 'Ответ правильный.'
                await send_message_to_vk(event=message)

                await game.update(last_question_id=game.last_question_id+1).apply()
                await self.ask_question(game.id, game.last_question_id)
            else:
                message['text'] = 'Ответ неправильный.'
                await send_message_to_vk(event=message)
        else:
            message['text'] = "Не понял, о чём ты. Давай ещё раз"
            await send_message_to_vk(message)

    async def task(self, game_id: int, question_idx: int):
        await asyncio.sleep(delay=self.delay)

        game = await GameSession.get(game_id)
        if game.last_question_id == question_idx:
            # отправляем в беседу правильный ответ
            answers = await (
                Answer.load()
                .query.where(Answer.question_id == game.questions[question_idx])
                .gino.all()
            )
            answers = AnswerCreateSchema(many=True).dump(answers)
            right_answer = ''
            for answer in answers:
                if answer['is_right']:
                    right_answer = answer['title']
                    break
            message = dict()
            message['peer_id'] = game.chat_id
            message['text'] = \
                f'Никто не ответил на вопрос. Правильный ответ:' \
                f'\n{right_answer}'
            await send_message_to_vk(event=message)

            await game.update(last_question_id=game.last_question_id + 1).apply()
            await self.ask_question(game_id, game.last_question_id)

    async def stop_game(self):
        pass

    async def game_info(self):
        pass

    async def bot_info(self):
        pass

    async def check_message(self, message: dict) -> None:
        """
        Алгоритм работы бота:

        Есть методы play_game, ask_question, receive_answer. play_game отвечает только за старт игры.
        Тут задаём первый вопрос (или не первый, если игра продолжается).

        Вопросы все задаются через метод ask_question. В этот метод передается id игры и индекс вопроса.
        Вопрос с вариантами ответа отсылается через vk accessor и заводится таска.
        В этой таске ждём минуту для ответа и тут есть два варианта:
        - Если last_question_id в сессии равен номеру вопроса этой таски, это значит,
          что на вопрос не был дан ответ и, следовательно, следующий вопрос не был задан.
          Поэтому last_question_id не обновился. В этом случае в беседу высылается правильный ответ и
          вызывается ask_question, который задаст следующий вопрос.
        - Второй вариант это когда номера вопросов не совпадают.
          Это значит, что уже был задан следующий вопрос и функция завершает работу.

        Теперь метод receive_answer. Он получает id игры и ответ на вопрос.
        Проверяет ответ на правильность и начисляет/снимает очки.
        Если был получен правильный ответ, вызывается ask_question для следующего вопроса.
        Если это был последний вопрос, отсылается сообщение о завершении игры и is_finished ставится в True.
        """
        print('check_message from bot')

        message_text = message['text'][len(bot_call) + 1:]
        chat_id = message['peer_id']
        if message_text == Commands.start_game.value:
            game = await self.find_unfinished_game(chat_id)
            if not game:
                game = await self.create_game(message)
            await self.play_game(game)
        elif message_text == Commands.stop_game.value:
            await self.stop_game()
        elif message_text == Commands.game_info.value:
            await self.game_info()
        elif message_text == Commands.bot_info.value:
            await self.bot_info()
        else:
            await self.receive_answer(chat_id, message_text)
