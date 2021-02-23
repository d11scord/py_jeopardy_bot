import aiohttp
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from app.settings import config


token = config["vk"]["access_token"]
v = config["vk"]["v"]
group_id = config["vk"]["group_id"]


vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(
    vk_session, group_id=group_id,
)


async def send_message_to_vk(
    peer_id: int,
    message: str,
    keyboard: VkKeyboard = None,
):
    vk.messages.send(
        random_id=get_random_id(),
        peer_id=peer_id,
        message=message,
        keyboard=keyboard,
    )
    # async with aiohttp.ClientSession() as session:
    #     async with session.get(
    #         url=f"https://api.vk.com/method/"
    #             f"messages.send?"
    #             f"peer_id={peer_id}&"
    #             f"message={message}&"
    #             f"access_token={token}&"
    #             f"v={v}&"
    #             f"group_id={group_id}",
    #     ) as resp:
    #         response = await resp.json()
    # return response


async def get_conversation_members(peer_id: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"https://api.vk.com/method/"
                f"messages.getConversationMembers?"
                f"peer_id={peer_id}&"
                f"access_token={token}&"
                f"v={v}&"
                f"group_id={group_id}",
        ) as resp:
            response = await resp.json()
    return response
