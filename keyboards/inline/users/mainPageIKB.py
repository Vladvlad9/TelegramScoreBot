from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram.utils.exceptions import BadRequest
from aiogram.types.web_app_info import WebAppInfo

from config import CONFIG
from crud import CRUDPizzaMenu, CRUDType
from crud.sizeCRUD import CRUDSize
from loader import bot

from aiogram.utils.callback_data import CallbackData

MainPage_CB = CallbackData("MainPage", "target", "id", "editId")


class Main:

    @staticmethod  # Главное меню
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

    @staticmethod  # Меню с выбором блюд
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

    @staticmethod  # Выбор действия при нажатии на меню
    async def search_ikb(target_back: str) -> InlineKeyboardMarkup:
        data_search = {
            "Фильтр": "Filter",
            "👀 Показать все": "ShowAll",
            "◀️ Назад": target_back
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=search_name,
                                         callback_data=MainPage_CB.new(search_target, 0, 0)
                                         )
                ] for search_name, search_target in data_search.items()
            ]
        )

    @staticmethod  # Клавиатура для отображения определенного блюда (Происходит Пагинация)
    async def description_pizza_ikb(target_back: str, pizza_id: int, page: int = 0, count: int = 1) -> InlineKeyboardMarkup:
        pizza_id = await CRUDPizzaMenu.get(pizzaMenu_id=pizza_id)

        size_id = await CRUDSize.get(size_id=pizza_id.size_id)
        type_id = await CRUDType.get(type_id=pizza_id.type_id)

        prev_page: int
        next_page: int

        pizza_id2 = await CRUDPizzaMenu.get_all()
        orders_count = len(pizza_id2)

        if page == 0:
            prev_page = orders_count - 1
            next_page = page + 1
        elif page == orders_count - 1:
            prev_page = page - 1
            next_page = 0
        else:
            prev_page = page - 1
            next_page = page + 1

        price = 0
        count_show = 1
        if count == 1:
            price = pizza_id.price
            prev_count = count - 1
            next_count = count + 1
        elif count == count - 1:
            count_show -= 1
            prev_count = count - 1
            next_count = 1
        else:
            price = float(pizza_id.price) + float(pizza_id.price)
            count_show += 1
            prev_count = count - 1
            next_count = count + 1

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"Цена: {str(price)}",
                                         callback_data=MainPage_CB.new("", 0, 0)
                                         ),
                    InlineKeyboardButton(text=f"{type_id.name}",
                                         callback_data=MainPage_CB.new("", 0, 0)
                                         ),
                    InlineKeyboardButton(text=f"{size_id.name}",
                                         callback_data=MainPage_CB.new("", 0, 0)
                                         )
                ],
                [
                    InlineKeyboardButton(text=f"➖",
                                         callback_data=MainPage_CB.new("CountPizza", prev_count, 0)
                                         ),
                    InlineKeyboardButton(text=f"{count_show}",
                                         callback_data=MainPage_CB.new(count, pizza_id.id, 0)
                                         ),
                    InlineKeyboardButton(text=f"➕",
                                         callback_data=MainPage_CB.new("CountPizza", next_count, 0)
                                         )
                ],
                [
                    InlineKeyboardButton(text=f"←",
                                         callback_data=MainPage_CB.new("PaginationPizza", prev_page, 0)
                                         ),
                    InlineKeyboardButton(text=f"☰",
                                         callback_data=MainPage_CB.new("Additionally", pizza_id.id, 0)
                                         ),
                    InlineKeyboardButton(text=f"→",
                                         callback_data=MainPage_CB.new("PaginationPizza", next_page, 0)
                                         )
                ],
                [
                    InlineKeyboardButton(text=f"◀️ Назад",
                                         callback_data=MainPage_CB.new(target_back, 0, 0)
                                         )
                ]
            ]
        )

    @staticmethod  # Бургер меню (дополнительно)
    async def additionally_ikb(target_back: str, pizza_id) -> InlineKeyboardMarkup:
        """

        :return:
        """
        data_additionally = {
            "Количество": "Amount",
            "➕ В Корзину": "Basket",
            "◀️ Назад": target_back
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=additionally,
                                         callback_data=MainPage_CB.new(additionally_target, 0, 0)
                                         )
                ] for additionally, additionally_target in data_additionally.items()
            ]
        )

    @staticmethod  # Фильтрация Пиццы
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
                    await callback.message.delete()
                    await callback.message.answer(text="Пицца",
                                                  reply_markup=await Main.search_ikb(target_back="Catalog"))

                elif data.get('target') == "Filter":
                    await callback.message.delete()
                    await callback.message.answer(text="Выберите параметры поиска",
                                                  reply_markup=await Main.filter_ikb(target_back="Pizza"))

                elif data.get('target') == "ShowAll":
                    data_pizzaMenu = await CRUDPizzaMenu.get_all()
                    await callback.message.delete()
                    await callback.message.answer_photo(photo=data_pizzaMenu[0].photo.decode('UTF-8'),
                                                        caption=f"Название: <b>{data_pizzaMenu[0].name}</b>\n\n"
                                                                f"Описание: <b>{data_pizzaMenu[0].description}</b>",
                                                        reply_markup=await Main.description_pizza_ikb(target_back="Pizza",
                                                                                                      pizza_id=int(data_pizzaMenu[0].id)),
                                                        parse_mode="HTML")

                elif data.get("target") == "Additionally":
                    # Сделать динамически pizza_id
                    current_pizza_id = int(data.get("id"))
                    pizza_id = await CRUDPizzaMenu.get(pizzaMenu_id=current_pizza_id)
                    await callback.message.delete()
                    await callback.message.answer(text=f"Вы выбрали\n"
                                                       f"{pizza_id.name}",
                                                  reply_markup=await Main.additionally_ikb(target_back="ShowAll",
                                                                                           pizza_id=pizza_id.id))

                elif data.get("target") == "PaginationPizza":
                    page = int(data.get('id'))
                    data_pizzaMenu = await CRUDPizzaMenu.get_all()
                    await callback.message.delete()
                    await callback.message.answer_photo(photo=data_pizzaMenu[page].photo.decode('UTF-8'),
                                                        caption=f"Название: <b>{data_pizzaMenu[page].name}</b>\n\n"
                                                                f"Описание: <b>{data_pizzaMenu[page].description}</b>",
                                                        reply_markup=await Main.description_pizza_ikb(
                                                            target_back="Pizza",
                                                            pizza_id=int(data_pizzaMenu[page].id),
                                                        page=page),
                                                        parse_mode="HTML")

                elif data.get("target") == "CountPizza":
                    page = int(data.get('id'))
                    count = int(data.get('id'))

                    data_pizzaMenu = await CRUDPizzaMenu.get_all()
                    await callback.message.delete()
                    await callback.message.answer_photo(photo=data_pizzaMenu[page].photo.decode('UTF-8'),
                                                        caption=f"Название: <b>{data_pizzaMenu[page].name}</b>\n\n"
                                                                f"Описание: <b>{data_pizzaMenu[page].description}</b>",
                                                        reply_markup=await Main.description_pizza_ikb(
                                                            target_back="Pizza",
                                                            pizza_id=int(data_pizzaMenu[page].id),
                                                            page=page,
                                                            count=count),
                                                        parse_mode="HTML")

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