from typing import List, Union

from sqlalchemy import and_, func

from app.store.database.models import (
    Answer,
    Question,
    GameSession,
    SessionScores,
)


async def find_unfinished_game(chat_id: int) -> Union[GameSession, None]:
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


async def generate_questions(count: int) -> List[Question]:
    return await Question.query.order_by(func.random()).limit(count).gino.all()


async def get_question_by_id(question_id: int) -> Question:
    return await Question.get(question_id)


async def get_answers_by_question_id(question_id: int) -> List[Answer]:
    return await Answer.load().query.where(Answer.question_id == question_id).gino.all()


async def get_user_scores(game_id: int, user_id: int) -> SessionScores:
    conditions = list()

    conditions.append(SessionScores.session_id == game_id)
    conditions.append(SessionScores.user_id == user_id)

    session_scores = await (
        SessionScores.load()
        .query.where(and_(*conditions))
        .gino.first()
    )
    return session_scores


async def get_game_scores(game_id: int) -> List[SessionScores]:
    session_scores = await (
        SessionScores.load()
        .query.where(SessionScores.session_id == game_id)
        .gino.all()
    )
    return session_scores


def format_answers(answers: List[Answer]) -> List[str]:
    formatted_answers = [a.title for a in answers]
    return formatted_answers
