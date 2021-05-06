"""Робота з категоріями витрат"""
from typing import Dict, List, NamedTuple

import db


class Category(NamedTuple):
    """Cтруктура категорії"""
    codename: str
    name: str
    is_base_expense: bool
    aliases: List[str]


class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Повертає довідник категорій витрат з БД"""
        categories = db.fetchall(
           "category", "codename name is_base_expense aliases".split()
        )
        categories = self._fill_aliases(categories)
        return categories

    def _fill_aliases(self, categories: List[Dict]) -> List[Category]:
        """Заповнює по кожній категорії aliases, тобто можливі
         назви цієї категорії, які можемо писати в тексті повідомлення.
         Наприклад, категорія «кафе» може бути написана як cafe,
         ресторан і тд."""
        categories_result = []
        for index, category in enumerate(categories):
            aliases = category["aliases"].split(",")
            aliases = list(filter(None, map(str.strip, aliases)))
            aliases.append(category["codename"])
            aliases.append(category["name"])
            categories_result.append(Category(
                codename=category['codename'],
                name=category['name'],
                is_base_expense=category['is_base_expense'],
                aliases=aliases
            ))
        return categories_result

    def get_all_categories(self) -> List[Dict]:
        """Повертає довідник категорій."""
        return self._categories

    def get_category(self, category_name: str) -> Category:
        """Повертає категорію по одному з її алиасов."""
        finded = None
        other_category = None
        for category in self._categories:
            if category.codename == "other":
                other_category = category
            for alias in category.aliases:
                if category_name in alias:
                    finded = category
        if not finded:
            finded = other_category
        return finded