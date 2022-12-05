from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram.utils.exceptions import BadRequest
from aiogram.types.web_app_info import WebAppInfo

from config import CONFIG
from loader import bot

from aiogram.utils.callback_data import CallbackData

MainPage_CB = CallbackData("MainPage", "target", "id", "editId")


class Main:
    @staticmethod
    async def start_ikb() -> InlineKeyboardMarkup:
        """
        Самая стартовая клавиатура
        :return:
        """
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Каталог",
                                         callback_data=MainPage_CB.new("Catalog", 0, 0)
                                         ),
                    InlineKeyboardButton(text="Корзина",
                                         callback_data=MainPage_CB.new("Basket", 0, 0)
                                         ),
                    InlineKeyboardButton(text="Контакты",
                                         callback_data=MainPage_CB.new("Contacts", 0, 0)
                                         )
                ]
            ]
        )

    @staticmethod
    async def process_profile(callback: CallbackQuery = None, message: Message = None,
                              state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith('MainPage'):
                data = MainPage_CB.parse(callback_data=callback.data)

                if data.get("target") == "MainMenu":
                    await callback.message.edit_text(text="Главная страница",
                                                     reply_markup=await Main.start_ikb())
                elif data.get("target") == "Catalog":
                    pass

                elif data.get("target") == "Basket":
                    pass

                elif data.get("target") == "Contacts":
                    pass


        if message:
            await message.delete()

            try:
                await bot.delete_message(
                    chat_id=message.from_user.id,
                    message_id=message.message_id - 1
                )
            except BadRequest:
                pass

            if state:
                if await state.get_state() == "MainState:SiteState":
                    pass