from aiohttp import web


class VkCallbackView(web.View):
    async def post(self):
        if self.request.get('type') == 'confirmation':
            print('confirmation')
            return self.request.app['config']['vk']['confirmation-token']

        elif self.request.get('type') == 'message_new':
            print('message')
            await self.request.app["vk"].send_message(self.request)
            return 'ok'
