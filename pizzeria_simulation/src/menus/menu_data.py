"""Меню пиццерии с категориями."""
from dataclasses import dataclass


@dataclass
class PizzaRecipe:
    """Рецепт пиццы."""
    name: str
    description: str
    ingredients: list[str]
    base_id: int = 1
    toppings: list[int] | None = None


# Рецепты пицц
PIZZA_RECIPES: dict[int, PizzaRecipe] = {
    1: PizzaRecipe(
        name="Маргарита",
        description="Классическая итальянская пицца",
        ingredients=["Томатный соус", "Моцарелла", "Базилик", "Оливковое масло"],
        base_id=1,
        toppings=[3, 6]
    ),
    2: PizzaRecipe(
        name="Пепперони",
        description="Острая пицца с пепперони",
        ingredients=["Томатный соус", "Моцарелла", "Пепперони"],
        base_id=1,
        toppings=[1, 3, 6]
    ),
    3: PizzaRecipe(
        name="Гавайская",
        description="С ананасами и ветчиной",
        ingredients=["Томатный соус", "Моцарелла", "Ветчина", "Ананасы"],
        base_id=1,
        toppings=[2, 3, 6]
    ),
    4: PizzaRecipe(
        name="Четыре сыра",
        description="Для любителей сыра",
        ingredients=["Моцарелла", "Пармезан", "Горгонзола", "Чеддер"],
        base_id=1,
        toppings=[3]
    ),
    5: PizzaRecipe(
        name="Мясная",
        description="Для настоящих мужчин",
        ingredients=["Томатный соус", "Моцарелла", "Пепперони", "Ветчина", "Бекон", "Колбаски"],
        base_id=1,
        toppings=[1, 2]
    ),
    6: PizzaRecipe(
        name="Вегетарианская",
        description="С овощами и грибами",
        ingredients=["Томатный соус", "Моцарелла", "Грибы", "Перец", "Лук", "Маслины"],
        base_id=1,
        toppings=[4, 5, 6]
    ),
    7: PizzaRecipe(
        name="Дьябло",
        description="Очень острая пицца",
        ingredients=["Томатный соус", "Моцарелла", "Пепперони", "Халапеньо", "Чили"],
        base_id=1,
        toppings=[1, 3, 6]
    ),
    8: PizzaRecipe(
        name="Карбонара",
        description="В стиле пасты карбонара",
        ingredients=["Сливочный соус", "Моцарелла", "Бекон", "Яйцо", "Пармезан"],
        base_id=1,
        toppings=[3]
    ),
}

# Напитки
DRINKS: dict[int, dict[str, str | float]] = {
    101: {"name": "Кола 0.5л", "price": 2.0, "description": "Coca-Cola классическая"},
    102: {"name": "Кола 1л", "price": 3.5, "description": "Coca-Cola классическая"},
    103: {"name": "Спрайт 0.5л", "price": 2.0, "description": "Sprite лимон-лайм"},
    104: {"name": "Фанта 0.5л", "price": 2.0, "description": "Fanta апельсиновая"},
    105: {"name": "Вода 0.5л", "price": 1.5, "description": "Минеральная вода без газа"},
    106: {"name": "Сок апельсиновый", "price": 3.0, "description": "Свежевыжатый 0.3л"},
    107: {"name": "Кофе эспрессо", "price": 2.5, "description": "Классический эспрессо"},
    108: {"name": "Капучино", "price": 3.5, "description": "Кофе с молоком 0.3л"},
    109: {"name": "Латте", "price": 3.5, "description": "Кофе с молоком 0.4л"},
    110: {"name": "Чай чёрный", "price": 2.0, "description": "Крепкий чёрный чай"},
    111: {"name": "Чай зелёный", "price": 2.0, "description": "Зелёный чай с жасмином"},
    112: {"name": "Лимонад домашний", "price": 3.0, "description": "Домашний лимонад 0.5л"},
}

# Другие блюда
OTHER_ITEMS: dict[int, dict[str, str | float]] = {
    201: {"name": "Салат Цезарь", "price": 7.0, "description": "С курицей и пармезаном"},
    202: {"name": "Салат Греческий", "price": 6.5, "description": "Свежие овощи и фета"},
    203: {"name": "Картофель фри", "price": 3.5, "description": "Хрустящий картофель"},
    204: {"name": "Наггетсы", "price": 5.0, "description": "Куриные наггетсы 6 шт"},
    205: {"name": "Крылышки BBQ", "price": 6.0, "description": "Острые крылышки 8 шт"},
    206: {"name": "Тирамису", "price": 4.5, "description": "Классический десерт"},
    207: {"name": "Чизкейк", "price": 4.0, "description": "Нью-Йорк стиль"},
    208: {"name": "Джелато", "price": 3.0, "description": "Итальянское мороженое"},
}


def get_pizza_recipe(pizza_id: int) -> PizzaRecipe | None:
    """Получить рецепт пиццы по ID."""
    return PIZZA_RECIPES.get(pizza_id)


def get_pizza_description(pizza_id: int) -> str:
    """Получить описание пиццы."""
    recipe = get_pizza_recipe(pizza_id)
    if not recipe:
        return "Пицца не найдена"
    
    ingredients = ", ".join(recipe.ingredients)
    return f"{recipe.name}: {recipe.description}\nСостав: {ingredients}"


def create_menu_items() -> list:
    """Создаёт все позиции меню."""
    from src.models import MenuItem
    
    items: list[MenuItem] = []
    
    # Пиццы
    for pizza_id, recipe in PIZZA_RECIPES.items():
        price = 8.5 + (pizza_id * 0.5)
        items.append(MenuItem(
            id=pizza_id,
            name=recipe.name,
            price=round(price, 1),
            is_available=True,
            category="pizza"
        ))
    
    # Напитки
    for drink_id, drink in DRINKS.items():
        items.append(MenuItem(
            id=drink_id,
            name=str(drink["name"]),
            price=float(drink["price"]),
            is_available=True,
            category="drink"
        ))
    
    # Другие блюда
    for other_id, other in OTHER_ITEMS.items():
        items.append(MenuItem(
            id=other_id,
            name=str(other["name"]),
            price=float(other["price"]),
            is_available=True,
            category="other"
        ))
    
    return items


def print_grouped_menu(items: list) -> None:
    """Выводит меню, сгруппированное по категориям."""
    pizzas = [i for i in items if i.category == "pizza"]
    drinks = [i for i in items if i.category == "drink"]
    others = [i for i in items if i.category == "other"]
    
    print("\n" + "=" * 50)
    print("ПИЦЦЫ")
    print("=" * 50)
    for item in pizzas:
        status = "[+]" if item.is_available else "[x]"
        print(f"{item.id:2}. {item.name:<20} {item.price:>6.1f}р {status}")
    
    print("\n" + "=" * 50)
    print("НАПИТКИ")
    print("=" * 50)
    for item in drinks:
        status = "[+]" if item.is_available else "[x]"
        print(f"{item.id:2}. {item.name:<20} {item.price:>6.1f}р {status}")
    
    print("\n" + "=" * 50)
    print("ДРУГИЕ БЛЮДА")
    print("=" * 50)
    for item in others:
        status = "[+]" if item.is_available else "[x]"
        print(f"{item.id:2}. {item.name:<20} {item.price:>6.1f}р {status}")
    
    print("=" * 50)


def show_pizza_details(pizza_id: int) -> str:
    """Показывает детали пиццы."""
    recipe = get_pizza_recipe(pizza_id)
    if not recipe:
        return f"Пицца #{pizza_id} не найдена"
    
    lines = [
        f"\nПицца: {recipe.name}",
        f"Описание: {recipe.description}",
        f"\nСостав:",
    ]
    for ingredient in recipe.ingredients:
        lines.append(f"   - {ingredient}")
    
    return "\n".join(lines)
