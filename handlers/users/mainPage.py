from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.exceptions import BadRequest
from aiogram.types import ContentType

from crud import CRUDBasket
from crud.menuCRUD import CRUDPizzaMenu
from keyboards.inline.users.mainPageIKB import MainPage_CB, Main
from loader import dp, bot
from schemas import PizzaMenuSchema
from states.users import MainState



class FSMAdmin(StatesGroup):
    photo = State()
    name = State()
    description = State()
    price = State()
    type_id = State()
    size_id = State()


@dp.message_handler(commands=['Загрузить'], state=None)
async def cm_start(message: types.Message):
    await FSMAdmin.photo.set()
    await message.reply('Загрузить фото')


@dp.message_handler(content_types=['photo'], state=FSMAdmin.photo)
async def load_photo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = bytes(message.photo[0].file_id.encode("utf-8"))
    await FSMAdmin.next()
    await message.reply("Введи Название")


@dp.message_handler(state=FSMAdmin.name)
async def load_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMAdmin.next()
    await message.reply("Введи описание")


@dp.message_handler(state=FSMAdmin.description)
async def load_description(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await FSMAdmin.next()
    await message.reply("Введи Цену")


@dp.message_handler(state=FSMAdmin.price)
async def load_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = message.text

    asd = await state.get_data()
    asd['type_id'] = 1
    asd['size_id'] = 1
    asd['parent_id'] = 2

    a = await CRUDPizzaMenu.add(pizzaMenu=PizzaMenuSchema(**asd))
    await state.finish()


@dp.message_handler(commands=["start"])
async def registration_start(message: types.Message):
    await message.delete()
    await message.answer(text="Главная страница",
                         reply_markup=await Main.start_ikb())


@dp.callback_query_handler(MainPage_CB.filter())
@dp.callback_query_handler(MainPage_CB.filter(), state=MainState.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await Main.process_profile(callback=callback, state=state)


@dp.message_handler(state=MainState.all_states, content_types=["text", "contact"])
async def process_message(message: types.Message, state: FSMContext = None):
    await Main.process_profile(message=message, state=state)


@dp.pre_checkout_query_handler(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query_id=pre_checkout_query.id,
                                        ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    try:
        await CRUDBasket.delete(user_id=message.from_user.id)
        await message.delete()
        await message.answer(text=f"Оплата прошла успешна успешно!\n",
                             reply_markup=await Main.start_ikb())
    except Exception as e:
        print(e)
        await message.answer(text=f"Оплата прошла успешна успешно!\n",
                             reply_markup=await Main.start_ikb())
