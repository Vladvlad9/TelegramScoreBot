from itertools import zip_longest

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest

from crud import CRUDType, CRUDPizzaMenu, CRUDPositionMenu
from crud.sizeCRUD import CRUDSize
from loader import bot
from schemas import PizzaMenuSchema
from states.admins.admin import AddMailingFSM

admin_cb = CallbackData("admin", "target", "action", "id", "editId")


class AdminPanel:
    @staticmethod
    async def back_ikb(target: str, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"◀️ Назад", callback_data=admin_cb.new(target, action, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def confirmation_upload_product_ikb(target: str, action: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"✅ Да", callback_data=admin_cb.new(target, action, 0, 0)),
                    InlineKeyboardButton(text=f"❌ Нет", callback_data=admin_cb.new("Upload_product",
                                                                                 "get_product", 0, 0))
                ]
            ]
        )

    @staticmethod
    async def get_size(target: str, action: str):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=size.name,
                                                         callback_data=admin_cb.new("Upload_product",
                                                                                    "getSize", size.id, 0))
                                ] for size in await CRUDSize.get_all()
            ] + [
                [
                    InlineKeyboardButton(text=f"◀️ Назад", callback_data=admin_cb.new(target, action, 0, 0))
                ]
            ]
        )

    @staticmethod
    async def get_type(target: str, action: str):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text=size.name,
                                                         callback_data=admin_cb.new("Upload_product",
                                                                                    "getType", size.id, 0))
                                ] for size in await CRUDType.get_all()
                            ] + [
                                [
                                    InlineKeyboardButton(text=f"◀️ Назад",
                                                         callback_data=admin_cb.new(target, action, 0, 0))
                                ]
                            ]
        )

    @staticmethod
    async def get_name_product():
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
                urlkb.add(InlineKeyboardButton(text=i.name,
                                               callback_data=admin_cb.new("Upload_product", "get_name", i.id, 0)),
                          InlineKeyboardButton(text="Назад", callback_data=admin_cb.new("StartAdmin", 0, 0, 0)))
            else:
                urlkb.add(InlineKeyboardButton(text=i.name,
                                               callback_data=admin_cb.new("Upload_product", "get_name", i.id, 0)),
                          InlineKeyboardButton(text=j.name,
                                               callback_data=admin_cb.new("Upload_product", "get_name", j.id, 0)))

        if len(data_postion_even) == len(data_postion_not_even):
            urlkb.add(InlineKeyboardButton(text='Назад', callback_data=admin_cb.new("StartAdmin", 0, 0, 0)))
        return urlkb

    @staticmethod
    async def upload_product_ikb(state) -> InlineKeyboardMarkup:
        data_state = await state.get_data()

        Image = "Картинка ✅" if "photo" in data_state else "Картинка"
        Title = "Название ✅" if "name" in data_state else "Название"
        Description = "Описание ✅" if "description" in data_state else "Описание"
        Type = "Тип ✅" if "type_id" in data_state else "Тип"
        Size = "Размер ✅" if "size_id" in data_state else "Размер"
        Price = "Цена ✅" if "price" in data_state else "Цена"
        addInDB = "Добавить в БД ➡️" if len(data_state) >= 7 else "Добавить в БД ❌"

        data = {
            f"{Image}": {"target": "Upload_product", "action": "Image", "id": 0, "editId": 0},
            f"{Title}": {"target": "Upload_product", "action": "Title", "id": 0, "editId": 0},
            f"{Description}": {"target": "Upload_product", "action": "Description", "id": 0, "editId": 0},
            f"{Type}": {"target": "Upload_product", "action": "Type", "id": 0, "editId": 0},
            f"{Size}": {"target": "Upload_product", "action": "Size", "id": 0, "editId": 0},
            f"{Price}": {"target": "Upload_product", "action": "Price", "id": 0, "editId": 0},
            f"{addInDB}": {"target": "Upload_product", "action": "Confirmation", "id": 0, "editId": 0},
            "◀️ Назад": {"target": "Upload_product", "action": "Back", "id": 0, "editId": 0}
        }

        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=name,
                                         callback_data=admin_cb.new(name_action["target"],
                                                                    name_action["action"],
                                                                    name_action["id"],
                                                                    name_action["editId"])
                                         )
                ] for name, name_action in data.items()
            ]
        )

    @staticmethod
    async def get_admin_panel() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=f"Загрузить товар",
                                         callback_data=admin_cb.new("Upload_product", "get_name_product", 0, 0)
                                         )
                ],
            ]
        )

    @staticmethod
    async def process(callback: CallbackQuery = None, message: Message = None, state: FSMContext = None) -> None:
        if callback:
            if callback.data.startswith("admin"):
                data = admin_cb.parse(callback_data=callback.data)
                if data.get("target") == "StartAdmin":
                    await state.finish()
                    await callback.message.edit_text(text="Панель администратора",
                                                     reply_markup=await AdminPanel.get_admin_panel()
                                                     )

                elif data.get("target") == "Upload_product":
                    if data.get('action') == "get_name_product":
                        await callback.message.edit_text(text="Выберите продукт который хотети добавить",
                                                         reply_markup=await AdminPanel.get_name_product()
                                                         )
                    elif data.get('action') == "get_name":
                        await state.update_data(parent_id=int(data.get('id')))
                        data_state = await state.get_data()
                        await callback.message.edit_text(text="Что бы Загрузить продукт в Базу Данных "
                                                              "заполните все данные\n\n"
                                                              f"Заполнено полей: {len(data_state) - 1}",
                                                         reply_markup=await AdminPanel.upload_product_ikb(
                                                             state=state
                                                         ))

                    elif data.get('action') == "get_product":
                        data_state = await state.get_data()
                        await callback.message.edit_text(text="Что бы Загрузить продукт в Базу Данных "
                                                              "заполните все данные\n\n"
                                                              f"Заполнено полей: {len(data_state)}",
                                                         reply_markup=await AdminPanel.upload_product_ikb(
                                                             state=state
                                                         ))

                    elif data.get('action') == "Image":
                        await callback.message.edit_text(text="Загрузите картинку",
                                                         reply_markup=await AdminPanel.back_ikb(
                                                             target="Upload_product",
                                                             action="get_product")
                                                         )
                        await AddMailingFSM.Image.set()

                    elif data.get('action') == "Title":
                        await callback.message.edit_text(text="Введите Название продукта",
                                                         reply_markup=await AdminPanel.back_ikb(
                                                             target="Upload_product",
                                                             action="get_product")
                                                         )
                        await AddMailingFSM.Title.set()

                    elif data.get('action') == "Description":
                        await callback.message.edit_text(text="Введите Описание продукта",
                                                         reply_markup=await AdminPanel.back_ikb(
                                                             target="Upload_product",
                                                             action="get_product")
                                                         )
                        await AddMailingFSM.Description.set()

                    elif data.get('action') == "Type":
                        await callback.message.edit_text(text="Выберите тип продукта",
                                                         reply_markup=await AdminPanel.get_type(
                                                             target="Upload_product",
                                                             action="get_product")
                                                         )
                    elif data.get('action') == "getType":
                        await state.update_data(type_id=int(data.get('id')))
                        data_state = await state.get_data()
                        await callback.message.edit_text(text="Тип успешно добавлен\n\n"
                                                              f"У вас заполнено полей {len(data_state)}",
                                                         reply_markup=await AdminPanel.upload_product_ikb(state=state))

                    elif data.get('action') == "Size":
                        await callback.message.edit_text(text="Выберите размер продукта",
                                                         reply_markup=await AdminPanel.get_size(
                                                             target="Upload_product",
                                                             action="get_product")
                                                         )
                    elif data.get('action') == "getSize":
                        await state.update_data(size_id=int(data.get('id')))
                        data_state = await state.get_data()
                        await callback.message.edit_text(text="Размер успешно добавлен\n\n"
                                                              f"У вас заполнено полей {len(data_state)}",
                                                         reply_markup=await AdminPanel.upload_product_ikb(state=state))

                    elif data.get('action') == "Price":
                        await callback.message.edit_text(text="Введите Цену продукта",
                                                         reply_markup=await AdminPanel.back_ikb(
                                                             target="Upload_product",
                                                             action="get_product")
                                                         )
                        await AddMailingFSM.Price.set()

                    elif data.get('action') == "Confirmation":
                        data_state = await state.get_data()
                        if len(data_state) < 6:
                            await callback.message.edit_text(text="У вас заполенены не все поля!",
                                                             reply_markup=await AdminPanel.back_ikb(
                                                                 target="Upload_product",
                                                                 action="get_product")
                                                             )
                        else:
                            menu = await CRUDPizzaMenu.add(pizzaMenu=PizzaMenuSchema(**data_state))
                            await callback.message.edit_text(text="Данные успешно добавлены",
                                                             reply_markup=await AdminPanel.get_admin_panel()
                                                             )
                            await state.finish()

                    elif data.get('action') == "Back":
                        data_state = await state.get_data()
                        if len(data_state) > 1:
                            text = f"У вас заполнено полей {len(data_state)}\n\n"\
                                   f"Если вы покините даную форму все данные потеряются\n"\
                                   f"Желаете выйти?"
                            await callback.message.edit_text(text=text,
                                                             reply_markup=
                                                             await AdminPanel.confirmation_upload_product_ikb(
                                                                 target="StartAdmin",
                                                                 action="")
                                                             )
                        else:
                            await callback.message.edit_text(text=f"Панель администратора",
                                                             reply_markup=await AdminPanel.get_admin_panel()
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
                if await state.get_state() == "AddMailingFSM:Image":
                    if message.content_type == "photo":
                        if message.photo[0].file_size > 3000:
                            await message.answer(text="Картинка превышает 2 мб\n"
                                                      "Попробуйте загрузить еще раз")
                            await AddMailingFSM.Image.set()
                        else:
                            data_state = await state.get_data()
                            if "name" in data_state:
                                get_photo = await bot.get_file(message.photo[len(message.photo) - 1].file_id)
                                await bot.download_file(file_path=get_photo.file_path,
                                                        destination=f'product_pictures/{data_state["name"]}_product.jpg',
                                                        timeout=12,
                                                        chunk_size=1215000)

                                await state.update_data(photo=f'{data_state["name"]}_product')
                                await message.answer(text="Картинка успешно добавлена\n\n"
                                                          f"У вас заполнено полей {len(data_state)}",
                                                     reply_markup=await AdminPanel.upload_product_ikb(state=state))
                            else:
                                await message.answer(text="Заполните сначала название\n\n"
                                                          f"У вас заполнено полей {len(data_state)}",
                                                     reply_markup=await AdminPanel.upload_product_ikb(state=state))
                    else:
                        await message.answer(text="Загрузите картинку")
                        await AddMailingFSM.Image.set()

                elif await state.get_state() == "AddMailingFSM:Title":
                    await state.update_data(name=message.text)
                    data_state = await state.get_data()
                    await message.answer(text="Название успешно добавлено\n\n"
                                              f"У вас заполнено полей {len(data_state)}",
                                         reply_markup=await AdminPanel.upload_product_ikb(state=state))

                elif await state.get_state() == "AddMailingFSM:Description":
                    await state.update_data(description=message.text)
                    data_state = await state.get_data()
                    await message.answer(text="Название успешно добавлено\n\n"
                                              f"У вас заполнено полей {len(data_state)}",
                                         reply_markup=await AdminPanel.upload_product_ikb(state=state))

                elif await state.get_state() == "AddMailingFSM:Price":
                    await state.update_data(price=message.text)
                    data_state = await state.get_data()
                    await message.answer(text="Цена успешна добавлена\n\n"
                                              f"У вас заполнено полей {len(data_state)}",
                                         reply_markup=await AdminPanel.upload_product_ikb(state=state))