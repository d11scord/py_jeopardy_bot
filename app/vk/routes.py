from app.vk.views import VkCallbackView


def setup_routes(app):
    app.router.add_view('/confirmation', VkCallbackView)
