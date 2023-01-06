from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram import types
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
    async def back_ikb(target: str, menu_id: int = 0, parent_id: int = 0, action: str = None):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="◀️ Назад", callback_data=MainPage_CB.new(target, action, parent_id,
                                                                                        menu_id, 1)
                                         )
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
    async def menu_ikb() -> InlineKeyboardMarkup:


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
        pizza_id = await CRUDPizzaMenu.get(menu_id=pizza_id, parent_id=parent_id)

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
                                             callback_data=MainPage_CB.new("DescriptionPizza", "CountPizza", next_count,
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
                                             callback_data=MainPage_CB.new("Catalog", "BackCatalog", 0, 0, 0)
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
                                             callback_data=MainPage_CB.new("DescriptionPizza", "CountPizza", next_count,
                                                                           pizza_id.id,
                                                                           parent_id)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"←",
                                             callback_data=MainPage_CB.new("DescriptionPizza",
                                                                           "PaginationPizza", prev_page, parent_id, parent_id)
                                             ),
                        InlineKeyboardButton(text=f"☰",
                                             callback_data=MainPage_CB.new("DescriptionPizza",
                                                                           "Additionally", pizza_id.id, count_show, parent_id)
                                             ),
                        InlineKeyboardButton(text=f"→",
                                             callback_data=MainPage_CB.new("DescriptionPizza",
                                                                           "PaginationPizza", next_page, parent_id, parent_id)
                                             )
                    ],
                    [
                        InlineKeyboardButton(text=f"◀️ Назад",
                                             callback_data=MainPage_CB.new("Catalog", "BackCatalog", 0, 0, 0)
                                             )
                    ]
                ]
            )

    @staticmethod  # Бургер меню (дополнительно)
    async def additionally_ikb(target_back: str, pizza_id: int, count: int, parent_id: int) -> InlineKeyboardMarkup:
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
                                                                                       count, parent_id
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
                                         callback_data=MainPage_CB.new(basket_menu['target'], basket_menu['action'],
                                                                       0, 0, 0)
                                         )
                ] for basket, basket_menu in data_basket.items()
            ]
        )

    @staticmethod
    async def editBasket():
        get_products = await CRUDBasket.get_all()
        urlkb = InlineKeyboardMarkup(row_width=3)
        for i in get_products:
            product = await CRUDPizzaMenu.get(menu_id=i.menu_id, parent_id=i.parent_id)
            urlkb.add(
                InlineKeyboardButton(text=product.name, callback_data=MainPage_CB.new("", "", i.id, i.parent_id, 0)),
                InlineKeyboardButton(text=f"✏ Кол.- {str(i.count)} ️",
                                     callback_data=MainPage_CB.new("Basket", "EditCountPosition", i.id, i.parent_id, 0)),
                InlineKeyboardButton(text="❌ Удалить ",
                                     callback_data=MainPage_CB.new("Basket", "DeletePosition", i.id, i.parent_id, 0)))
        urlkb.add(InlineKeyboardButton(text="◀️ Назад",
                                       callback_data=MainPage_CB.new("Basket", "show", 0, 0, 0)))
        return urlkb

    @staticmethod
    async def addBasket_ikb(menu_id: int = None, parent_id: int = None):
        """
                        Клаиатура когда пользователь добавил товар в корзину
                        :return:
                        """
        data_basket = {
            "Главное меню": {"target": "MainMenu", "action": ""},
            "🛒 Корзина": {"target": "Basket", "action": "show"},
            "◀️ Назад": {"target": "DescriptionPizza", "action": "ShowAll"},
        }
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=basket,
                                         callback_data=MainPage_CB.new(basket_menu['target'], basket_menu['action'],
                                                                       parent_id, menu_id, 0)
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
                                                         reply_markup=await Main.menu_ikb())
                    elif data.get("action") == "PositionMenu":
                        await callback.message.delete()
                        get_id = int(data.get("id"))
                        get_position = await CRUDPositionMenu.get(position_menu_id=get_id)
                        await callback.message.answer(text=get_position.name,
                                                      reply_markup=await Main.search_ikb(target_back="BackPizza",
                                                                                         position_id=get_id))

                    elif data.get("action") == "BackCatalog":
                        await callback.message.delete()
                        await callback.message.answer(text="Меню",
                                                      reply_markup=await Main.menu_ikb()
                                                      )

                elif data.get('target') == "Filter":
                    await callback.message.delete()
                    await callback.message.answer(text="Выберите параметры поиска",
                                                  reply_markup=await Main.filter_ikb(target_back="Pizza"))

                elif data.get('target') == "DescriptionPizza":

                    if data.get('action') == "ShowAll":
                        try:
                            get_position_id = int(data.get('id'))
                            data_pizzaMenu = await CRUDPizzaMenu.get_all(position_id=get_position_id)
                            if data_pizzaMenu:
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
                            else:
                                await callback.message.edit_text(text="Блюда временно отсутствуют",
                                                                 reply_markup=await Main.menu_ikb())
                        except Exception as e:
                            print(e)
                            await callback.message.edit_text(text="Главная страница",
                                                             reply_markup=await Main.start_ikb()
                                                             )

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
                        count_id = int(data.get("editId"))
                        parent_id = int(data.get("newId"))
                        pizza_id = await CRUDPizzaMenu.get(menu_id=current_pizza_id, parent_id=parent_id)
                        await callback.message.delete()
                        await callback.message.answer(text=f"Вы выбрали\n"
                                                           f"{pizza_id.name}\n\n"
                                                           f"Количество: {count_id}",
                                                      reply_markup=await Main.additionally_ikb(target_back="ShowAll",
                                                                                               pizza_id=pizza_id.id,
                                                                                               count=count_id,
                                                                                               parent_id=parent_id)
                                                      )

                    elif data.get("action") == "CountPizza":

                        page = int(data.get('editId'))
                        parent_id = int(data.get('newId'))
                        if int(data.get('id')) == 0:
                            count = 1
                        else:
                            count = int(data.get('id'))

                        pizza = await CRUDPizzaMenu.get(menu_id=page, parent_id=parent_id)
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
                        current_menu_id = int(data.get("id"))
                        count_product = int(data.get("editId"))
                        parent_id = int(data.get("newId"))

                        get_product = await CRUDBasket.get(parent_id=parent_id, menu_id=current_menu_id)
                        if get_product:
                            get_product.count = count_product
                            await CRUDBasket.update(basket=get_product)
                        else:
                            await CRUDBasket.add(basket=BasketSchema(menu_id=current_menu_id,
                                                                     parent_id=parent_id,
                                                                     count=count_product,
                                                                     user_id=int(callback.from_user.id))
                                                 )
                        await callback.message.edit_text("Вы успешно добавили товар в Корзину",
                                                         reply_markup=await Main.addBasket_ikb(menu_id=current_menu_id,
                                                                                               parent_id=parent_id)
                                                         )

                    elif data.get("action") == "BackPizza":
                        await callback.message.edit_text(text="Меню",
                                                         reply_markup=await Main.menu_ikb())

                elif data.get("target") == "Basket":
                    if data.get("action") == "show":
                        get_basket = await CRUDBasket.get_all(user_id=callback.from_user.id)
                        if get_basket:
                            result = "🛒 Список товаров в корзине:\n\n"
                            pay = 0

                            for value in get_basket:
                                pizza = await CRUDPizzaMenu.get(menu_id=value.menu_id, parent_id=value.parent_id)
                                result += f"Название - {pizza.name}\n" \
                                          f"Колличество - {value.count}\n" \
                                          f"Цена - {float(pizza.price) * float(value.count)}\n" \
                                          f"{'_' * 25}\n\n"
                                pay += float(pizza.price) * float(value.count)

                            await callback.message.edit_text(text=f"{result}\n\n Общая стоимость - {pay}р.",
                                                             reply_markup=await Main.basket_ikb())
                        else:
                            await callback.message.edit_text("У вас в корзине отсутствуют товары",
                                                             reply_markup=await Main.back_ikb(target="MainMenu",
                                                                                              action=str(0),
                                                                                              parent_id=0,
                                                                                              menu_id=0)
                                                             )

                    elif data.get('action') == "EditBasket":
                        await callback.message.edit_text(text="Форма редактирования",
                                                         reply_markup=await Main.editBasket())

                    elif data.get('action') == "EditCountPosition":
                        get_menu = int(data.get('id'))
                        get_parent = int(data.get('editId'))

                    elif data.get('action') == "DeletePosition":
                        position_id = int(data.get('id'))
                        get_parent = int(data.get('editId'))

                        product = await CRUDBasket.get(position_id=position_id)
                        get_menu = await CRUDPizzaMenu.get(menu_id=product.menu_id, parent_id=product.parent_id)
                        await CRUDBasket.delete(basket_id=product.id)
                        await callback.message.edit_text(text=f"{get_menu.name} - успешно удален",
                                                         reply_markup=await Main.editBasket())

                    elif data.get('action') == "PayBasket":
                        basket_user = await CRUDBasket.get_all(user_id=callback.from_user.id)
                        name_product = ""
                        price_product = 0
                        for basket in basket_user:
                            get_product = await CRUDPizzaMenu.get(menu_id=basket.menu_id, parent_id=basket.parent_id)
                            name_product += f"{get_product.name}\n"
                            price_product += float(get_product.price) * basket.count
                        rus_rub = float(26.22)

                        amount = price_product * rus_rub * 1000
                        a = (amount / rus_rub)

                        price = types.LabeledPrice(label='Оплата товара!', amount=int(a))
                        await callback.message.delete()
                        await bot.send_invoice(chat_id=callback.message.chat.id,
                                               title=f"Оплата товара \n{name_product}\n",
                                               description=f"Оплатить товары\n{name_product}",
                                               provider_token=CONFIG.PAYTOKEN,
                                               currency='RUB',
                                               is_flexible=False,
                                               prices=[price],
                                               start_parameter='time-machine-example',
                                               payload='some-invoice-payload-for-our-internal-use'
                                               )

                elif data.get("target") == "Contacts":

                    text = f"\n\n" \
                           f"📱 Контактный номер телефона : <code>{CONFIG.SUPPORT.PHONE}</code>\n\n" \
                           f"📧 Email: {CONFIG.SUPPORT.EMAIL}\n\n" \
                           f"📷 Instagram : <a href='www.instagram.com/{CONFIG.SUPPORT.INSTAGRAM}/'>{CONFIG.SUPPORT.INSTAGRAM}</a>\n\n" \
                           f"🎧 Discord :<code>{CONFIG.SUPPORT.DISCORD}</code>\n\n" \
                           f"✈️ Телеграм : <a href='www.t.me/{CONFIG.SUPPORT.TELEGRAM}/'>{CONFIG.SUPPORT.TELEGRAM}</a>"

                    await callback.message.edit_text(text=f"Способ связи: {text}",
                                                     reply_markup=await Main.back_ikb(target="MainMenu",
                                                                                      action=str(0),
                                                                                      parent_id=0,
                                                                                      menu_id=0),
                                                     parse_mode="HTML",
                                                     disable_web_page_preview=True
                                                     )

                elif data.get('target') == "FAQ":
                    if data.get('action') == "show":
                        text = "1.<b>Что бы воспользоваться тестовой карточко введите</b>\n" \
                               "Номер - 111 1111 111 1026\n" \
                               "Дата  - 12/22\n" \
                               "CVC   - 000"
                        await callback.message.edit_text(text=text,
                                                         reply_markup=await Main.back_ikb(target="MainMenu",
                                                                                          action="show"),
                                                         parse_mode="HTML"
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
