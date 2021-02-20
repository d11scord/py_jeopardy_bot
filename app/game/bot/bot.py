import asyncio
from enum import Enum
from pprint import pprint
from typing import Optional

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

        self.max_question = 5
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

    async def start_game(self, message) -> GameSession:
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
        question_ids = game.questions

        questions = list()

        for q_id in question_ids:
            question = await Question.get(q_id)
            question = QuestionSchema().dump(question)
            answers = await Answer.load().query.where(Answer.question_id == q_id).gino.all()
            answers = AnswerCreateSchema(many=True).dump(answers)
            questions.append({
                'question': question['title'],
                'theme': question['theme'],
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
        message = dict()
        message.update({'peer_id': game.chat_id})
        for question in questions:
            answers = [a['title'] for a in question['answers']]
            message_text = template.format(
                theme=question['theme'],
                question=question['question'],
                *answers,
            )
            message.update({'text': message_text})
            await send_message_to_vk(event=message)
            # здесь ждём минуту/ответа

    def stop_game(self):
        pass

    def game_info(self):
        pass

    def bot_info(self):
        pass

    async def check_message(self, message: dict) -> None:
        print('check_message from bot')

        message_text = message['text'][len(bot_call) + 1:]
        chat_id = message['peer_id']
        if message_text == Commands.start_game.value:
            game = await self.find_unfinished_game(chat_id)
            if game:
                await self.play_game(game)

            else:
                game = await self.start_game(message)
                await self.play_game(game)
        elif message_text == Commands.stop_game.value:
            self.stop_game()
        elif message_text == Commands.game_info.value:
            self.game_info()
        elif message_text == Commands.bot_info.value:
            self.bot_info()
        elif message_text in ('a', 'b', 'c', 'd'):
            pass
        else:
            message['text'] = "йА тебя не панимаю"
            await send_message_to_vk(message)
