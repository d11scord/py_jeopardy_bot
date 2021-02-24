import asyncio
from enum import Enum

from sqlalchemy import and_
from vk_api.keyboard import VkKeyboard

from app.game.bot.keyboard_generator import generate_answers_keyboard, generate_bot_commands_keyboard
from app.game.bot.utils import (
    find_unfinished_game,
    generate_questions,
    get_question_by_id,
    get_answers_by_question_id,
    format_answers, get_user_scores, get_game_scores,
)
from app.settings import config
from app.vk.accessor import send_message_to_vk, get_conversation_members
from app.vk.utils import bot_call

from app.store.database.models import (
    GameSession,
    SessionScores,
    User,
)


class Commands(Enum):
    global_start = 'Начать'
    start_game = ['Начать игру']
    stop_game = ['Завершить игру']
    game_info = ['Об игре']
    bot_info = ['О боте']
    my_scores = ['Мои очки']


class JeopardyBot:
    def __init__(self):

        self.score = 100  # баллы за правильный ответ
        self.delay = 60  # seconds
        self.max_question = 5

        self.template = \
            """
            Тема: {theme}
            {question}

            a. {}
            b. {}
            c. {}
            d. {}
            """

        # todo: костыль?
        asyncio.get_event_loop().run_until_complete(self.connect())

    @staticmethod
    async def connect():
        from app.store.database.models import db

        await db.set_bind(config['postgres']['database_url'])
        await db.gino.create_all()

    async def create_game(self, peer_id: int) -> GameSession:
        # рандомим вопросы для игры и создаём новую сессию
        questions = await generate_questions(self.max_question)
        # берём айдишники вопросов
        questions = [q.id for q in questions]
        new_game_session = await GameSession.create(
            chat_id=peer_id,
            questions=questions,
            last_question_id=0,
            is_finished=False,
        )
        # создаём юзера, если его нет ...
        users = list()
        response = await get_conversation_members(peer_id)
        print(response)
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

        message = f"Ок, начинаем сессию номер {new_game_session.id}."
        await send_message_to_vk(peer_id, message=message)
        return new_game_session

    async def play_game(self, game: GameSession):
        current_question_idx = game.last_question_id

        await self.ask_question(game.id, current_question_idx)

    async def ask_question(self, game_id: int, question_idx: int):
        game = await GameSession.get(game_id)

        if game.last_question_id == self.max_question:
            await self.stop_game(game)
        else:
            question_id = game.questions[question_idx]
            question = await get_question_by_id(question_id)

            answers = await get_answers_by_question_id(question_id)

            formatted_question = {
                'question': question.title,
                'theme': question.theme,
                'answers': answers,
            }

            message = self.template.format(
                theme=formatted_question['theme'],
                question=formatted_question['question'],
                *format_answers(answers)
            )

            keyboard = generate_answers_keyboard(format_answers(answers))
            await send_message_to_vk(
                game.chat_id, message, keyboard.get_keyboard())

            asyncio.create_task(self.task(game_id, question_idx))  # -------------------------------------------------!

    async def receive_answer(self, chat_id: int, user_id: int, message_text: str):
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

        game = await find_unfinished_game(chat_id)
        if game:
            user = await User.query.where(User.user_id == user_id).gino.first()

            question_id = game.questions[game.last_question_id]
            answers = await get_answers_by_question_id(question_id)
            right_answer = ''
            for answer in answers:
                if answer.is_right:
                    right_answer = answer.title
                    break

            session_scores = await get_user_scores(game.id, user_id)

            if message_text == right_answer:
                update_score = session_scores.score+self.score
                await session_scores.update(score=update_score).apply()
                message = f'Ответ правильный. {user.firstname} {user.lastname} получает {self.score} очков.'
                await send_message_to_vk(chat_id, message)
                await game.update(last_question_id=game.last_question_id+1).apply()
                await self.ask_question(game.id, game.last_question_id)
            else:
                update_score = session_scores.score - self.score
                await session_scores.update(score=update_score).apply()
                message = f'Ответ неправильный. {user.firstname} {user.lastname}, лови минус {self.score} очков.'
                await send_message_to_vk(chat_id, message)
        else:
            message = "Не понял, о чём ты. Давай ещё раз."
            await send_message_to_vk(chat_id, message)

    async def task(self, game_id: int, question_idx: int):
        # время на ответ
        await asyncio.sleep(delay=self.delay)

        game = await GameSession.get(game_id)
        if game.is_finished:
            return
        # если никто не ответил на вопрос
        if game.last_question_id == question_idx:
            # отправляем в беседу правильный ответ
            answers = await get_answers_by_question_id(
                game.questions[question_idx]
            )

            right_answer = ''
            for answer in answers:
                if answer.is_right:
                    right_answer = answer.title
                    break

            message = \
                f'Никто не ответил на вопрос. Правильный ответ:' \
                f'\n{right_answer}'

            await send_message_to_vk(game.chat_id, message)
            await game.update(last_question_id=game.last_question_id+1).apply()
            await self.ask_question(game_id, game.last_question_id)

    async def stop_game(self, game: GameSession):
        # заканчиваем игру
        await game.update(is_finished=True).apply()
        await send_message_to_vk(game.chat_id, message='Игра окончена.')
        await self.game_info(game.chat_id)
        # обновляем глобальные очки пользователей
        session_scores = await get_game_scores(game.id)
        for user_score in session_scores:
            user = await User.get(user_score.user_id)
            new_score = user.score + user_score.score
            await user.update(score=new_score).apply()

    @staticmethod
    async def game_info(chat_id):
        game = await (
            GameSession.query
            .where(GameSession.chat_id == chat_id)
            .order_by(GameSession.id.desc())
            .gino.first()
        )
        if game is None:
            message = 'В этом чате ещё не было игр.'
            await send_message_to_vk(chat_id, message)
            return
        response = await get_conversation_members(chat_id)
        if 'error' in response:
            print(response)
            message = 'Проверьте права бота. У него должна быть роль "Администратор".'
            await send_message_to_vk(chat_id, message)
            return
        members = response['response']['profiles']
        result = f"Игра № {game.id}"
        for member in members:
            session_score = await (
                SessionScores.load()
                .query.where(and_(
                    (SessionScores.session_id == game.id),
                    (SessionScores.user_id == member['id'])
                ))
                .gino.first()
            )
            result += f"\n{member['first_name']} {member['last_name']}: {session_score.score}"
        await send_message_to_vk(chat_id, result)

    async def bot_info(self, chat_id: int, keyboard: VkKeyboard = None):
        bot_name = f"@{config['vk']['bot_name']}"
        message = \
        f"""
        Привет. Я СвояИгра Бот. Умею играть в «Свою Игру».
        Ко мне обращайся только через тэг {bot_name}. Другие сообщения я не читаю.
        Для начала игры добавь меня в беседу, сделай администратором и напиши «{bot_name} {'/'.join(Commands.start_game.value)}».
        Далее правила простые — я задаю вопрос, вы отвечаете. Кто первым правильно ответит на вопрос, получит на свой счёт очки. Если отвечаешь неправильно, очки с твоего счёта списываются. Если за {self.delay} секунд никто не ответит на вопрос, я дам вам правильный ответ и задам следующий. Игра состоит из {self.max_question} вопросов. Победит тот, кто наберёт наибольшее количество очков.
        Для досрочного завершения игры напиши «{bot_name} {'/'.join(Commands.stop_game.value)}». Для получения ифнормации о текущей или последней игре напиши «{bot_name} {'/'.join(Commands.start_game.value)}». Если хочешь посмотреть на промежуточные баллы, пиши «{bot_name} {' ,'.join(Commands.bot_info.value)}» Общее количество твоих баллов — «{bot_name} {'/'.join(Commands.my_scores.value)}».
        """
        await send_message_to_vk(chat_id, message, keyboard)

    @staticmethod
    async def personal_score(peer_id: int, user_id: int):
        user = await User.get(user_id)
        message = f'{user.firstname}, всего у тебя {user.score} очков.'
        await send_message_to_vk(peer_id, message)

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
        user_id = message['from_id']
        chat_id = message['peer_id']

        if message_text in Commands.start_game.value:
            game = await find_unfinished_game(chat_id)
            if not game:
                game = await self.create_game(chat_id)
            await self.play_game(game)
        elif message_text in Commands.stop_game.value:
            game = await find_unfinished_game(chat_id)
            if game:
                await self.stop_game(game)
            else:
                await send_message_to_vk(chat_id, 'Нет незавершённой игры.')
        elif message_text in Commands.game_info.value:
            await self.game_info(chat_id)
        elif message_text in Commands.bot_info.value:
            await self.bot_info(chat_id)
        elif message_text in Commands.my_scores.value:
            await self.personal_score(chat_id, user_id)
        elif message_text == Commands.global_start.value:
            await self.bot_info(
                chat_id,
                generate_bot_commands_keyboard().get_keyboard(),
            )
        elif message['answer'] is not None:
            await self.receive_answer(chat_id, user_id, message['answer'])
        else:
            message = "Не понял, о чём ты. Давай ещё раз."
            await send_message_to_vk(chat_id, message)
