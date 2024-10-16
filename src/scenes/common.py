from __future__ import annotations

from typing import TypedDict

from aiogram import F, html
from aiogram.filters import Command
from aiogram.fsm.scene import After, Scene, on
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

BUTTON_CANCEL = KeyboardButton(text="❌ Cancel")
BUTTON_BACK = KeyboardButton(text="🔙 Back")


class FSMData(TypedDict, total=False):
    name: str
    language: str


class CancellableScene(Scene):
    """
    Handles cancel and back buttons,
    can be used as a base class for other scenes that needs to support cancel and back buttons.
    """

    @on.message(F.text.casefold() == BUTTON_CANCEL.text.casefold(), after=After.exit())
    async def handle_cancel(self, message: Message):  # noqa: D102
        await message.answer("Cancelled.", reply_markup=ReplyKeyboardRemove())

    @on.message(F.text.casefold() == BUTTON_BACK.text.casefold(), after=After.back())
    async def handle_back(self, message: Message):  # noqa: D102
        await message.answer("Back.")


class LanguageScene(CancellableScene, state="language"):
    """
    Scene is used to ask user what language he prefers.
    """

    @on.message.enter()
    async def on_enter(self, message: Message):  # noqa: D102
        await message.answer(
            "What language do you prefer?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[BUTTON_BACK, BUTTON_CANCEL]],
                resize_keyboard=True,
            ),
        )

    @on.message(F.text.casefold() == "python", after=After.exit())
    async def process_python(self, message: Message):  # noqa: D102
        await message.answer(
            "Python, you say? That's the language that makes my circuits light up! 😉",
        )
        await self.input_language(message)

    @on.message(after=After.exit())
    async def input_language(self, message: Message):  # noqa: D102
        data: FSMData = await self.wizard.get_data() # type: ignore  # noqa: PGH003
        await self.show_results(message, language=message.text, **data) # type: ignore  # noqa: PGH003

    async def show_results(self, message: Message, name: str, language: str) -> None:  # noqa: D102
        await message.answer(
            text=f"I'll keep in mind that, {html.quote(name)}, you like to write bots with {html.quote(language)}.",
            reply_markup=ReplyKeyboardRemove(),
        )


class LikeBotsScene(CancellableScene, state="like_bots"):
    """
    Scene is used to ask user if he likes to write bots.
    """

    @on.message.enter()
    async def on_enter(self, message: Message):  # noqa: D102
        await message.answer(
            "Did you like to write bots?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Yes"), KeyboardButton(text="No")],
                    [BUTTON_BACK, BUTTON_CANCEL],
                ],
                resize_keyboard=True,
            ),
        )

    @on.message(F.text.casefold() == "yes", after=After.goto(LanguageScene))
    async def process_like_write_bots(self, message: Message):  # noqa: D102
        await message.reply("Cool! I'm too!")

    @on.message(F.text.casefold() == "no", after=After.exit())
    async def process_dont_like_write_bots(self, message: Message):  # noqa: D102
        await message.answer(
            "Not bad not terrible.\nSee you soon.",
            reply_markup=ReplyKeyboardRemove(),
        )

    @on.message()
    async def input_like_bots(self, message: Message):  # noqa: D102
        await message.answer("I don't understand you :(")


class NameScene(CancellableScene, state="name"):
    """
    Scene is used to ask user's name.
    """

    @on.message.enter()  # Marker for handler that should be called when a user enters the scene.
    async def on_enter(self, message: Message):  # noqa: D102
        await message.answer(
            "Hi there! What's your name?",
            reply_markup=ReplyKeyboardMarkup(keyboard=[[BUTTON_CANCEL]], resize_keyboard=True),
        )

    @on.callback_query.enter()  # different types of updates that start the scene also supported.
    async def on_enter_callback(self, callback_query: CallbackQuery):  # noqa: D102
        await callback_query.answer()
        await self.on_enter(callback_query.message)

    @on.message.leave()  # Marker for handler that should be called when a user leaves the scene.
    async def on_leave(self, message: Message):  # noqa: D102
        data: FSMData = await self.wizard.get_data() # type: ignore  # noqa: PGH003
        name = data.get("name", "Anonymous")
        await message.answer(f"Nice to meet you, {html.quote(name)}!")

    @on.message(after=After.goto(LikeBotsScene))
    async def input_name(self, message: Message):  # noqa: D102
        await self.wizard.update_data(name=message.text)


class DefaultScene(
    Scene,
    reset_data_on_enter=True,  # Reset state data
    reset_history_on_enter=True,  # Reset history
    callback_query_without_state=True,  # Handle callback queries even if user in any scene
):
    """
    Default scene for the bot.

    This scene is used to handle all messages that are not handled by other scenes.
    """

    start_demo = on.message(F.text.casefold() == "demo", after=After.goto(NameScene))

    @on.message(Command("demo"))
    async def demo(self, message: Message):  # noqa: D102
        await message.answer(
            "Demo started",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[[InlineKeyboardButton(text="Go to form", callback_data="start")]],
            ),
        )

    @on.callback_query(F.data == "start", after=After.goto(NameScene))
    async def demo_callback(self, callback_query: CallbackQuery):  # noqa: D102
        await callback_query.answer(cache_time=0)
        await callback_query.message.delete_reply_markup() # type: ignore  # noqa: PGH003

    @on.message.enter()  # Mark that this handler should be called when a user enters the scene.
    @on.message()
    async def default_handler(self, message: Message):  # noqa: D102
        await message.answer(
            "Start demo?\nYou can also start demo via command /demo",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Demo")]],
                resize_keyboard=True,
            ),
        )
