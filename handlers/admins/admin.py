from aiogram import types
from aiogram.dispatcher import FSMContext

from filters import IsAdmin
from keyboards.inline.admin.admin import admin_cb, AdminPanel
from loader import dp
from states.admins.admin import AddMailingFSM


@dp.message_handler(IsAdmin(), commands=["admin"])
async def sing_in_admin_menu(message: types.Message):
    await message.delete()
    await message.answer(
        text=f"<b>{message.from_user.full_name}</b>, вы вошли в админ панель.",
        reply_markup=await AdminPanel.get_admin_panel()
    )


@dp.callback_query_handler(admin_cb.filter())
@dp.callback_query_handler(IsAdmin(), admin_cb.filter(), state=AddMailingFSM.all_states)
async def process_callback(callback: types.CallbackQuery, state: FSMContext = None):
    await AdminPanel.process(callback=callback, state=state)


@dp.message_handler(IsAdmin(), state=AddMailingFSM.all_states, content_types=["text", "photo"])
async def process_message(message: types.Message, state: FSMContext):
    await AdminPanel.process(message=message, state=state)