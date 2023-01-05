from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram.utils.exceptions import BadRequest
from aiogram.types.web_app_info import WebAppInfo

from config import CONFIG
from crud import CRUDPizzaMenu, CRUDType, CRUDBasket, CRUDPositionMenu
from crud.sizeCRUD import CRUDSize
from loader import bot

from aiogram.utils.callback_data import CallbackData

from schemas import BasketSchema, BasketInDBSchema
from itertools import zip_longest
MainPage_CB = CallbackData("MainPage", "target", "action", "id", "editId", "newId")


class Main:

    @staticmethod
    async def back_ikb(target: str, action: str = None):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=MainPage_CB.new(target, action, 0, 0, 0))
                ]
            ]
        )

    @staticmethod  # Главное меню
    async def start_ikb() -> InlineKeyboardMarkup:
        """
        Самая стартовая клавиатура  главного меню
        :return:
        """
        data_start = {
            "🍽 Меню": "Catalog",
            "🛒 Корзина": "Basket",
            "📞 Контакты": "Contacts",
            "📝 FAQ": "FAQ",
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=menu,
                                         callback_data=MainPage_CB.new(menu_target, "show", 0, 0, 0)
                                         )
                ] for menu, menu_target in data_start.items()
            ]
        )

    @staticmethod  # Меню с выбором блюд
    async def menu_ikb(target: str, target_back: str) -> InlineKeyboardMarkup:


        """
        Клаиатура меню
        :return:
        """
        data_postion_even = []
        data_postion_not_even = []
        count = 0
        urlkb = InlineKeyboardMarkup(row_width=2)
        for name in await CRUDPositionMenu.get_all():
            if count % 2 == 0:
                data_postion_even.append(name)
                count += 1
            else:
                data_postion_not_even.append(name)
                count += 1

        for i, j in zip_longest(data_postion_even, data_postion_not_even, fillvalue=None):
            if j is None:
                urlkb.add(InlineKeyboardButton(text=i.name, callback_data=MainPage_CB.new("Catalog", "PositionMenu", i.id, 0, 0)),
                          InlineKeyboardButton(text="Назад", callback_data=MainPage_CB.new("MainMenu", 0, 0, 0, 0)))
            else:
                urlkb.add(InlineKeyboardButton(text=i.name, callback_data=MainPage_CB.new("Catalog", "PositionMenu", i.id, 0, 0)),
                          InlineKeyboardButton(text=j.name, callback_data=MainPage_CB.new("Catalog", "PositionMenu", j.id, 0, 0)))

        if len(data_postion_even) == len(data_postion_not_even):
            urlkb.add(InlineKeyboardButton(text='Назад', callback_data=MainPage_CB.new("MainMenu", 0, 0, 0, 0)))
        return urlkb

        # right_ikb = [
        #     InlineKeyboardButton(text=menu_name, callback_data=MainPage_CB.new(target, menu_target, 0, 0))
        #     for menu_name, menu_target in data_menu.items()
        # ]
        #
        # left_ikb = [
        #     InlineKeyboardButton(text=menu_name, callback_data=MainPage_CB.new(target, menu_target, 0, 0))
        #     for menu_name, menu_target in data_menu_two.items()
        # ]
        #
        # return InlineKeyboardMarkup(
        #     inline_keyboard=[
        #         right_ikb,
        #         left_ikb,
        #         [
        #             InlineKeyboardButton(text="◀️ Назад", callback_data=MainPage_CB.new(target_back, 0, 0, 0))
        #         ]
        #     ]
        # )

    @staticmethod  # Выбор действия при нажатии на меню
    async def search_ikb(target_back: str, position_id: int) -> InlineKeyboardMarkup:
        data_search = {
            "Фильтр": "Filter",
            "👀 Показать все": "ShowAll",
            "◀️ Назад": target_back
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=search_name,
                                         callback_data=MainPage_CB.new("DescriptionPizza", search_target, position_id,
                                                                       0, 0)
                                         )
                ] for search_name, search_target in data_search.items()
            ]
        )

    @staticmethod  # Клавиатура для отображения определенного блюда (Происходит Пагинация)
    async def description_pizza_ikb(target_back: str,
                                    pizza_id: int,
                                    parent_id: int,
                                    page: int = 0,
                                    count: int = 1,
                                    nextCount: bool = False) -> InlineKeyboardMarkup:
        pizza_id = await CRUDPizzaMenu.get(pizzaMenu_id=pizza_id, parent_id=parent_id)

        size_id = await CRUDSize.get(size_id=pizza_id.size_id)
        type_id = await CRUDType.get(type_id=pizza_id.type_id)

        prev_page: int = 0
        next_page: int = 0

        pizza_id2 = await CRUDPizzaMenu.get_all(position_id=parent_id)
        orders_count = len(pizza_id2)

        price = float(pizza_id.price)
        count_show = count
        prev_count: int = 0
        next_count: int = 0

        if nextCount:
            if count == 1:
                count_show += 1
                price = float(pizza_id.price) * count_show
                prev_count = count - 1
                next_count = count + 1

            elif count == count - 1:
                count_show -= 1
                prev_count = count - 1
                next_count = 1
            else:
                count_show += 1
                prev_count = count - 1
                next_count = count + 1
                price = float(pizza_id.price) * count_show
        else:
            if page == 0:
                prev_page = orders_count - 1
                next_page = page + 1
            elif page == orders_count - 1:
                prev_page = page - 1
                next_page = 0
            else:
                prev_page = page - 1
                next_page = page + 1

        if orders_count == 1:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=f"Цена: {str(price)}",
                                             callback_data=MainPage_CB.new("", 0, 0, 0, 0)
                                             ),
                        InlineKeyboardButton(text=f"{type_id.name}",
                                             callback_data=MainPage_CB.new("", 0, 0, 0, 0)
                                             ),
                        InlineKeyboardButton(text=f"{size_id.name}",
                                             callback_data=MainPage_CB.new("", 0, 0, 0, 0)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"➖",
                                             callback_data=MainPage_CB.new("DescriptionPizza", "CountPizza", prev_count,
                                                                           pizza_id.id,
                                                                           parent_id)
                                             ),
                        InlineKeyboardButton(text=f"{count_show}",
                                             callback_data=MainPage_CB.new(0, 0, count, pizza_id.id, parent_id)
                                             ),
                        InlineKeyboardButton(text=f"➕",
                                             callback_data=MainPage_CB.new("DescriptionPizza", "CountPizza", prev_count,
                                                                           pizza_id.id,
                                                                           parent_id)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"☰",
                                             callback_data=MainPage_CB.new("DescriptionPizza",
                                                                           "Additionally", pizza_id.id,
                                                                           count_show, parent_id)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"◀️ Назад",
                                             callback_data=MainPage_CB.new("Catalog", target_back, 0, 0)
                                             )
                    ]
                ]
            )
        else:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=f"Цена: {str(price)}",
                                             callback_data=MainPage_CB.new("", 0, 0, 0, 0)
                                             ),
                        InlineKeyboardButton(text=f"{type_id.name}",
                                             callback_data=MainPage_CB.new("", 0, 0, 0, 0)
                                             ),
                        InlineKeyboardButton(text=f"{size_id.name}",
                                             callback_data=MainPage_CB.new("", 0, 0, 0, 0)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"➖",
                                             callback_data=MainPage_CB.new("DescriptionPizza", "CountPizza", prev_count,
                                                                           pizza_id.id,
                                                                           parent_id)
                                             ),
                        InlineKeyboardButton(text=f"{count_show}",
                                             callback_data=MainPage_CB.new(0, 0, count, pizza_id.id, parent_id)
                                             ),
                        InlineKeyboardButton(text=f"➕",
                                             callback_data=MainPage_CB.new("DescriptionPizza", "CountPizza", prev_count,
                                                                           pizza_id.id,
                                                                           parent_id)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"←",
                                             callback_data=MainPage_CB.new("DescriptionPizza",
                                                                           "PaginationPizza", prev_page, parent_id, 0)
                                             ),
                        InlineKeyboardButton(text=f"☰",
                                             callback_data=MainPage_CB.new("DescriptionPizza",
                                                                           "Additionally", pizza_id.id, count_show, parent_id)
                                             ),
                        InlineKeyboardButton(text=f"→",
                                             callback_data=MainPage_CB.new("DescriptionPizza",
                                                                           "PaginationPizza", next_page, parent_id, 0)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"◀️ Назад",
                                             callback_data=MainPage_CB.new("Catalog", target_back, 0, 0, 0)
                                             )
                    ]
                ]
            )

    @staticmethod  # Бургер меню (дополнительно)
    async def additionally_ikb(target_back: str, pizza_id: int, count: int) -> InlineKeyboardMarkup:
        """

        :return:
        """
        data_additionally = {
            "➕ В Корзину": "AddBasket",
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=additionally,
                                                         callback_data=MainPage_CB.new("DescriptionPizza",
                                                                                       additionally_target,
                                                                                       pizza_id,
                                                                                       count, 0
                                                                                       )
                                                         )
                                ] for additionally, additionally_target in data_additionally.items()
                            ] +
                            [
                                [
                                    InlineKeyboardButton(text="◀️ Назад",
                                                         callback_data=MainPage_CB.new("DescriptionPizza", target_back,
                                                                                       pizza_id, 0, 0)
                                                         )
                                ]
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
                                         callback_data=MainPage_CB.new(filter_n_target, 0, 0, 0, 0)
                                         )
                ] for filter_name, filter_n_target in data_filter.items()
            ]
        )

    @staticmethod
    async def basket_ikb():
        """
                Клаиатура в для формы Корзина
                :return:
                """
        data_basket = {
            "📝 Редактировать": {"target": "Basket", "action": "EditBasket"},
            "💵 Оплатить": {"target": "Basket", "action": "PayBasket"},
            "◀️ Назад": {"target": "MainMenu", "action": ""},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=basket,
                                         callback_data=MainPage_CB.new(basket_menu['target'], basket_menu['target'],
                                                                       0, 0)
                                         )
                ] for basket, basket_menu in data_basket.items()
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
                    if data.get("action") == "show":
                        await callback.message.edit_text(text="Меню",
                                                         reply_markup=await Main.menu_ikb(target="Catalog",
                                                                                          target_back="MainMenu"))
                    elif data.get("action") == "PositionMenu":
                        await callback.message.delete()
                        get_id = int(data.get("id"))
                        await callback.message.answer(text="Пицца",
                                                      reply_markup=await Main.search_ikb(target_back="BackPizza",
                                                                                         position_id=get_id))

                elif data.get('target') == "Filter":
                    await callback.message.delete()
                    await callback.message.answer(text="Выберите параметры поиска",
                                                  reply_markup=await Main.filter_ikb(target_back="Pizza"))

                elif data.get('target') == "DescriptionPizza":

                    if data.get('action') == "ShowAll":
                        get_position_id = int(data.get('id'))
                        data_pizzaMenu = await CRUDPizzaMenu.get_all(position_id=get_position_id)
                        await callback.message.delete()
                        # await callback.message.answer_photo(photo=photo.decode('UTF-8'))
                        await callback.message.answer_photo(photo=data_pizzaMenu[0].photo.decode('UTF-8'),
                                                            caption=f"Название: <b>{data_pizzaMenu[0].name}</b>\n\n"
                                                                    f"Описание: <b>{data_pizzaMenu[0].description}</b>",
                                                            reply_markup=await Main.description_pizza_ikb(
                                                                target_back="Pizza",
                                                                pizza_id=int(data_pizzaMenu[0].id, ),
                                                                count=1,
                                                                parent_id=get_position_id
                                                            ),
                                                            parse_mode="HTML")
                    elif data.get("action") == "PaginationPizza":
                        page = int(data.get('id'))
                        get_parent_id = int(data.get('editId'))

                        data_pizzaMenu = await CRUDPizzaMenu.get_all(position_id=get_parent_id)
                        await callback.message.delete()
                        await callback.message.answer_photo(photo=data_pizzaMenu[page].photo.decode('UTF-8'),
                                                            caption=f"Название: <b>{data_pizzaMenu[page].name}</b>\n\n"
                                                                    f"Описание: <b>{data_pizzaMenu[page].description}</b>",
                                                            reply_markup=await Main.description_pizza_ikb(
                                                                target_back="Pizza",
                                                                pizza_id=int(data_pizzaMenu[page].id),
                                                                page=page,
                                                                count=1,
                                                                parent_id=get_parent_id
                                                            ),
                                                            parse_mode="HTML")

                    elif data.get("action") == "Additionally":
                        # Сделать динамически pizza_id

                        current_pizza_id = int(data.get("id"))
                        count_pizza = int(data.get("editId"))
                        parent_pizza = int(data.get("newId"))
                        pizza_id = await CRUDPizzaMenu.get(pizzaMenu_id=current_pizza_id, parent_id=parent_pizza)
                        await callback.message.delete()
                        await callback.message.answer(text=f"Вы выбрали\n"
                                                           f"{pizza_id.name}\n\n"
                                                           f"Количество: {count_pizza}",
                                                      reply_markup=await Main.additionally_ikb(target_back="ShowAll",
                                                                                               pizza_id=pizza_id.id,
                                                                                               count=count_pizza)
                                                      )

                    elif data.get("action") == "CountPizza":

                        page = int(data.get('editId'))
                        parent_id = int(data.get('newId'))
                        if int(data.get('id')) == 0:
                            count = 1
                        else:
                            count = int(data.get('id'))

                        pizza = await CRUDPizzaMenu.get(pizzaMenu_id=page, parent_id=parent_id)
                        await callback.message.delete()
                        await callback.message.answer_photo(photo=pizza.photo.decode('UTF-8'),
                                                            caption=f"Название: <b>{pizza.name}</b>\n\n"
                                                                    f"Описание: <b>{pizza.description}</b>",
                                                            reply_markup=await Main.description_pizza_ikb(
                                                                target_back="Pizza",
                                                                pizza_id=int(pizza.id),
                                                                page=0,
                                                                count=count,
                                                                nextCount=True,
                                                                parent_id=int(parent_id)
                                                            ),
                                                            parse_mode="HTML")

                    elif data.get("action") == "AddBasket":
                        current_pizza_id = int(data.get("id"))
                        count_pizza = int(data.get("editId"))

                        get_product = await CRUDBasket.get(product_id=current_pizza_id)
                        if get_product:
                            get_product.count = count_pizza
                            await CRUDBasket.update(basket=get_product)
                        else:
                            await CRUDBasket.add(basket=BasketSchema(pizza_id=current_pizza_id,
                                                                     count=count_pizza,
                                                                     user_id=int(callback.from_user.id))
                                                 )
                        await callback.message.edit_text("Вы успешно добавили товар в Корзину",
                                                         reply_markup=await Main.back_ikb(target="DescriptionPizza",
                                                                                          action="ShowAll"))

                    elif data.get("action") == "BackPizza":
                        await callback.message.edit_text(text="Меню",
                                                         reply_markup=await Main.menu_ikb(target="Catalog",
                                                                                          target_back="MainMenu"))

                elif data.get("target") == "Basket":
                    get_basket = await CRUDBasket.get_all(user_id=callback.from_user.id)
                    if get_basket:
                        result = "🛒 Список товаров в корзине:\n\n"

                        for value in get_basket:
                            a = dict(value)
                            pizza = await CRUDPizzaMenu.get(pizzaMenu_id=a['pizza_id'])
                            result += f"Название - {pizza.name}\n" \
                                      f"Колличество - {a['count']}\n" \
                                      f"Цена - {float(pizza.price) * float(a['count'])}\n" \
                                      f"{'_' * 25}\n\n"

                        await callback.message.edit_text(text=result,
                                                         reply_markup=await Main.basket_ikb())
                    else:
                        await callback.message.edit_text("У вас в корзине отсутствуют товары",
                                                         reply_markup=await Main.back_ikb(target="MainMenu",
                                                                                          action=str(0)))

                elif data.get("target") == "Contacts":

                    text = f"\n\n" \
                           f"📱 Контактный номер телефона : <code>{CONFIG.SUPPORT.PHONE}</code>\n\n" \
                           f"📧 Email: {CONFIG.SUPPORT.EMAIL}\n\n" \
                           f"📷 Instagram : <a href='www.instagram.com/{CONFIG.SUPPORT.INSTAGRAM}/'>{CONFIG.SUPPORT.INSTAGRAM}</a>\n\n" \
                           f"🎧 Discord :<code>{CONFIG.SUPPORT.DISCORD}</code>\n\n" \
                           f"✈️ Телеграм : <a href='www.t.me/{CONFIG.SUPPORT.TELEGRAM}/'>{CONFIG.SUPPORT.TELEGRAM}</a>"

                    await callback.message.edit_text(text=f"Способ связи: {text}",
                                                     reply_markup=await Main.back_ikb(target="MainMenu",
                                                                                      action=str(0)),
                                                     parse_mode="HTML",
                                                     disable_web_page_preview=True
                                                     )

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
