from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def generate_bot_commands_keyboard() -> VkKeyboard:
    keyboard_commands = VkKeyboard()
    keyboard_commands.add_callback_button(
        label='Начать игру',
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "text"}
    )
    keyboard_commands.add_callback_button(
        label='Завершить игру',
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "text"}
    )
    keyboard_commands.add_line()
    keyboard_commands.add_callback_button(
        label='Об игре',
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "text"}
    )
    keyboard_commands.add_callback_button(
        label='О боте',
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "text"}
    )
    keyboard_commands.add_line()
    keyboard_commands.add_callback_button(
        label='Мои очки',
        color=VkKeyboardColor.PRIMARY,
        payload={"type": "text"}
    )
    return keyboard_commands


def generate_answers_keyboard(answers: list) -> VkKeyboard:
    chars = ['a', 'b', 'c', 'd']
    keyboard_answers = VkKeyboard(inline=True)
    for char, answer in zip(chars, answers):
        keyboard_answers.add_callback_button(
            label=char,
            color=VkKeyboardColor.PRIMARY,
            payload={"type": "text", "answer": answer}
        )
    return keyboard_answers
