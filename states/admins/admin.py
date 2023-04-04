from aiogram.dispatcher.filters.state import StatesGroup, State


class AddMailingFSM(StatesGroup):
    Image = State()
    Title = State()
    Description = State()
    Type = State()
    Size = State()
    Price = State()

    Image_Approved = State()
    Title_Approved = State()
    Description_Approved = State()
    Type_Approved = State()
    Size_Approved = State()
    Price_Approved = State()


