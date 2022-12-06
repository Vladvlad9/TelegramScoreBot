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
        Самая стартовая клавиатура  главного меню
        :return:
        """
        data_start = {
            "🍽 Меню": "Catalog",
            "🧺 Корзина": "Basket",
            "📞 Контакты": "Contacts",
            "📝 FAQ": "FAQ",
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=menu,
                                         callback_data=MainPage_CB.new(menu_target, 0, 0)
                                         )
                ]for menu, menu_target in data_start.items()
            ]
        )

    @staticmethod
    async def menu_ikb(target_back: str) -> InlineKeyboardMarkup:
        """
        Клаиатура меню
        :return:
        """
        data_menu = {
            "🍕 Пицца": "Pizza",
            "🍔 Бургеры": "Burgers",
            "🥗 Салаты": "Salads",
        }

        data_menu_two = {
            "🍲 Гарячие блюда": "HotDishes",
            "🧃 Напитки": "Beverages",
            "🍨 Десерты": "Desserts"
        }

        right_ikb = [
            InlineKeyboardButton(text=menu_name, callback_data=MainPage_CB.new(menu_target, 0, 0))
            for menu_name, menu_target in data_menu.items()
        ]

        left_ikb = [
            InlineKeyboardButton(text=menu_name, callback_data=MainPage_CB.new(menu_target, 0, 0))
            for menu_name, menu_target in data_menu_two.items()
        ]

        return InlineKeyboardMarkup(
            inline_keyboard=[
                right_ikb,
                left_ikb,
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=MainPage_CB.new(target_back, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def search_ikb(target_back: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="Фильтр",
                                         callback_data=MainPage_CB.new("Filter", 0, 0)
                                         )
                ],
                [
                    InlineKeyboardButton(text="👀 Показать все",
                                         callback_data=MainPage_CB.new("ShowAll", 0, 0)
                                         )
                ],
                [
                    InlineKeyboardButton(text="◀️ Назад",
                                         callback_data=MainPage_CB.new(target_back, 0, 0)
                                         )
                ]
            ]
        )

    @staticmethod
    async def filter_ikb(target_back: str) -> InlineKeyboardMarkup:
        data_filter = {
            "Тип пиццы": "FilterType",
            "Стоимость": "FilterPrice",
            "Размер": "FilterSize",
            "🔍 Найти": "FilterSearch",
            "◀️ Назад": target_back
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=filter_name,
                                         callback_data=MainPage_CB.new(filter_n_target, 0, 0)
                                         )
                ] for filter_name, filter_n_target in data_filter.items()
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
                    await callback.message.edit_text(text="Меню",
                                                     reply_markup=await Main.menu_ikb(target_back="MainMenu"))

                elif data.get('target') == "Pizza":
                    await callback.message.edit_text(text="Пицца",
                                                     reply_markup=await Main.search_ikb(target_back="Catalog"))

                elif data.get('target') == "Filter":
                    await callback.message.edit_text(text="Выберите параметры поиска",
                                                     reply_markup=await Main.filter_ikb(target_back="Pizza"))

                elif data.get("target") == "Basket":

                    await bot.send_poll(chat_id=callback.message.chat.id, question="выбор", options=[
                        'asd',
                        'asd2',
                        'asd3',
                    ],
                                        is_anonymous=True,
                                        allows_multiple_answers=True,
                                        explanation='asddasdasdasdas')

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