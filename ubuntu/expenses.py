""" Робота з витратами - їх додавання, видалення, статистики"""
import datetime
import re
from typing import List, NamedTuple, Optional

import pytz

import db
import exceptions
from categories import Categories


class Message(NamedTuple):
    """Структура распаршенного повідомлення про новий витраті"""
    amount: int
    category_text: str


class Expense(NamedTuple):
    """Структура доданого в БД нового витрати"""
    id: Optional[int]
    amount: int
    category_name: str


def add_expense(raw_message: str) -> Expense:
    """Додає нове повідомлення.
     Приймає на вхід текст повідомлення, що прийшов в бот."""
    parsed_message = _parse_message(raw_message)
    category = Categories().get_category(
        parsed_message.category_text)
    inserted_row_id = db.insert("expense", {
        "amount": parsed_message.amount,
        "created": _get_now_formatted(),
        "category_codename": category.codename,
        "raw_text": raw_message
    })
    return Expense(id=None,
                   amount=parsed_message.amount,
                   category_name=category.name)


def get_today_statistics() -> str:
    """Повертає рядком статистику витрат за сьогодні"""
    cursor = db.get_cursor()
    cursor.execute("select sum(amount)"
                   "from expense where date(created)=date('now', 'localtime')")
    result = cursor.fetchone()
    if not result[0]:
        return "Сегодня ещё нет расходов"
    all_today_expenses = result[0]
    cursor.execute("select sum(amount) "
                   "from expense where date(created)=date('now', 'localtime') "
                   "and category_codename in (select codename "
                   "from category where is_base_expense=true)")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Витрати сьогодні:\n"
            f"всього — {all_today_expenses} грн.\n"
            f"базові — {base_today_expenses} грн. из {_get_budget_limit()} грн.\n\n"
            f"За цей місяць: /month")


def get_month_statistics() -> str:
    """Повертає рядком статистику витрат за поточний місяць"""
    now = _get_now_datetime()
    first_day_of_month = f'{now.year:04d}-{now.month:02d}-01'
    cursor = db.get_cursor()
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}'")
    result = cursor.fetchone()
    if not result[0]:
        return "У цьому місяці ще немає витрат"
    all_today_expenses = result[0]
    cursor.execute(f"select sum(amount) "
                   f"from expense where date(created) >= '{first_day_of_month}' "
                   f"and category_codename in (select codename "
                   f"from category where is_base_expense=true)")
    result = cursor.fetchone()
    base_today_expenses = result[0] if result[0] else 0
    return (f"Витрати в поточному місяці:\n"
            f"всього — {all_today_expenses} грн.\n"
            f"базові — {base_today_expenses} грн. из "
            f"{now.day * _get_budget_limit()} грн.")


def last() -> List[Expense]:
    """Повертає останні кілька витрат"""
    cursor = db.get_cursor()
    cursor.execute(
        "select e.id, e.amount, c.name "
        "from expense e left join category c "
        "on c.codename=e.category_codename "
        "order by created desc limit 10")
    rows = cursor.fetchall()
    last_expenses = [Expense(id=row[0], amount=row[1], category_name=row[2]) for row in rows]
    return last_expenses


def delete_expense(row_id: int) -> None:
    """Видаляє повідомлення за його ідентифікатором"""
    db.delete("expense", row_id)


def _parse_message(raw_message: str) -> Message:
    """Парсить текст прийшов повідомлення про новий витраті."""
    regexp_result = re.match(r"([\d ]+) (.*)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessage(
            "Не можу зрозуміти повідомлення. Напишіть повідомлення в форматі, "
             "наприклад:\n1500 метро")

    amount = regexp_result.group(1).replace(" ", "")
    category_text = regexp_result.group(2).strip().lower()
    return Message(amount=amount, category_text=category_text)


def _get_now_formatted() -> str:
    """Повертає сьогоднішню дату рядком"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Повертає сьогоднішній datetime з урахуванням часової зони."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now


def _get_budget_limit() -> int:
    """Повертає денний ліміт витрат для основних базових витрат"""
    return db.fetchall("budget", ["daily_limit"])[0]["daily_limit"]