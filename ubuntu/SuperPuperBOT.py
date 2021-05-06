import os
import logging

from aiogram import Bot, Dispatcher, executor, types
import aiohttp

from categories import Categories
import exceptions
import expenses

API_TOKEN = '1700263011:AAEwD5UhlbJjwtH-KNOq76tavJWEHK2xRDo'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(
        "Бот для облікy фінансів\n\n"
        "Додати витрати: 250 таксі\n"
        "За поточний місяць: /month\n"
        "Останні внесені витрати: /expenses\n"
        "Категорії витрат: /categories",
        reply=False)


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_expense(message: types.Message):
    """Видаляє один запис про витрату по її ідентифікатору"""
    row_id = int(message.text[4:])
    expenses.delete_expense(row_id)
    answer_message = "Удалил"
    await message.answer(answer_message)


@dp.message_handler(commands=['categories'])
async def categories_list(message: types.Message):
    """Відправляє список категорій витрат"""
    categories = Categories().get_all_categories()
    answer_message = "Категорiї витрат:\n\n* " +\
            ("\n* ".join([c.name+' ('+", ".join(c.aliases)+')' for c in categories]))
    await message.answer(answer_message)


@dp.message_handler(commands=['today'])
async def today_statistics(message: types.Message):
    """Отправляет сегодняшнюю статистику трат"""
    answer_message = expenses.get_today_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['month'])
async def month_statistics(message: types.Message):
    """Отправляет статистику трат текущего месяца"""
    answer_message = expenses.get_month_statistics()
    await message.answer(answer_message)


@dp.message_handler(commands=['expenses'])
async def list_expenses(message: types.Message):
    """Отправляет последние несколько записей о расходах"""
    last_expenses = expenses.last()
    if not last_expenses:
        await message.answer("Расходы ещё не заведены")
        return

    last_expenses_rows = [
        f"{expense.amount} грн. на {expense.category_name} — нажмiть "
        f"/del{expense.id} для видалення"
        for expense in last_expenses]
    answer_message = "Останні збережені витрати:\n\n* " + "\n\n* "\
            .join(last_expenses_rows)
    await message.answer(answer_message)

@dp.message_handler()
async def add_expense(message: types.Message):
    """Додає новi витрати"""
    try:
        expense = expenses.add_expense(message.text)
    except exceptions.NotCorrectMessage as e:
        await message.answer(str(e))
        return
    answer_message = (
        f"Добавлены траты {expense.amount} грн. на {expense.category_name}.\n\n"
        f"{expenses.get_today_statistics()}")
    await message.answer(answer_message)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)