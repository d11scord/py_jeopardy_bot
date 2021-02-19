import aiohttp
from vk_api import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

from app.settings import config


token = config["vk"]["access-token"]
v = config["vk"]["v"]
group_id = config["vk"]["group-id"]


def create_vk_connection() -> VkBotLongPoll:
    vk_session = vk_api.VkApi(token=token)
    _ = vk_session.get_api()
    longpoll = VkBotLongPoll(
        vk_session, group_id=group_id,
    )
    return longpoll


async def send_message_to_vk(event):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f"https://api.vk.com/method/"
                f"messages.send?"
                f"peer_id={event['peer_id']}&"
                f"message={event['text']}&"
                f"access_token={token}&"
                f"v={v}&"
                f"group_id={group_id}",
        ) as resp:
            response = await resp.json()
    return response
