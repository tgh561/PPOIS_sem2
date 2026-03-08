#import os
#from pathlib import Path
#
#ROOT = Path("pizzeria_cli")
#
#
#def create_file(path: Path, content: str = "") -> None:
#    path.parent.mkdir(parents=True, exist_ok=True)
#    if not path.exists():
#        path.write_text(content, encoding="utf-8")
#
#
#def main() -> None:
#    # Директории
#    (ROOT / "src" / "pizzeria").mkdir(parents=True, exist_ok=True)
#    (ROOT / "tests").mkdir(parents=True, exist_ok=True)
#    (ROOT / "docs").mkdir(parents=True, exist_ok=True)
#
#    # Файлы пакета
#    create_file(ROOT / "src" / "pizzeria" / "__init__.py", "")
#    create_file(
#        ROOT / "src" / "pizzeria" / "__main__.py",
#        'from .cli import main\n\nif __name__ == "__main__":\n    main()\n',
#    )
#    create_file(
#        ROOT / "src" / "pizzeria" / "cli.py",
#        '"""Command-line interface for the pizzeria app."""\n\n'
#        'from .storage import load_state, save_state\n\n'
#        'def main() -> None:\n'
#        '    state = load_state()\n'
#        '    # TODO: главный диалоговый цикл\n'
#        '    print("Pizzeria CLI stub. To be implemented.")\n'
#        '    save_state(state)\n',
#    )
#    create_file(
#        ROOT / "src" / "pizzeria" / "models.py",
#        '"""Domain models: Menu, Order, Table, etc."""\n\n',
#    )
#    create_file(
#        ROOT / "src" / "pizzeria" / "services.py",
#        '"""Business logic services: OrderService, KitchenService, etc."""\n\n',
#    )
#    create_file(
#        ROOT / "src" / "pizzeria" / "storage.py",
#        '"""JSON storage for PizzeriaState."""\n\n'
#        'from __future__ import annotations\n\n'
#        'import json\nfrom pathlib import Path\nfrom typing import Any, Dict\n\n'
#        'STATE_FILE = Path("state.json")\n\n'
#        'def load_state() -> Dict[str, Any]:\n'
#        '    if not STATE_FILE.exists():\n'
#        '        # TODO: вернуть состояние по умолчанию\n'
#        '        return {}\n'
#        '    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))\n'
#        '    return data\n\n'
#        'def save_state(state: Dict[str, Any]) -> None:\n'
#        '    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")\n',
#    )
#    create_file(
#        ROOT / "src" / "pizzeria" / "exceptions.py",
#        '"""Custom exceptions for the pizzeria app."""\n\n'
#        'class PizzeriaError(Exception):\n'
#        '    """Base exception for the pizzeria domain."""\n'
#        '    pass\n',
#    )
#
#    # Тесты
#    create_file(ROOT / "tests" / "__init__.py", "")
#    create_file(
#        ROOT / "tests" / "test_basic.py",
#        'def test_dummy() -> None:\n'
#        '    assert True\n',
#    )
#
#    # Документация
#    create_file(
#        ROOT / "docs" / "README.md",
#        "# Pizzeria CLI\n\nЧерновик документации.\n",
#    )
#    create_file(
#        ROOT / "docs" / "CLASS_DIAGRAM.md",
#        "# UML Диаграмма классов\n\n(сюда позже вставишь диаграмму)\n",
#    )
#    create_file(
#        ROOT / "docs" / "STATE_DIAGRAM.md",
#        "# UML Диаграмма состояний заказа\n\n(сюда позже вставишь диаграмму)\n",
#    )
#
#    # Корневые файлы
#    create_file(
#        ROOT / "README.md",
#        "# Pizzeria CLI\n\nУчебный проект: симуляция работы пиццерии через CLI.\n",
#    )
#    create_file(
#        ROOT / "requirements.txt",
#        "# Здесь позже можно указать зависимости для тестов и т.п.\n",
#    )
#    create_file(
#        ROOT / ".gitignore",
#        "__pycache__/\n*.pyc\n.env\n.state.json\n",
#    )
#
#    print(f"Project skeleton created under {ROOT.resolve()}")
#
#
#if __name__ == "__main__":
#    main()
# create_pizzeria_structure.py
# Запусти этот файл в той папке, где хочешь создать проект
# Например: python create_pizzeria_structure.py

import os
from pathlib import Path

# Базовая папка проекта
PROJECT_ROOT = "pizzeria_simulation"

# Структура в виде словаря (очень удобно добавлять/менять)
STRUCTURE = {
    "src": {
        "models": [
            "__init__.py",
            "customer.py",
            "employee.py",
            "kitchen.py",
            "hall.py",
            "counter.py",
            "order.py",
            "pizzeria.py",
        ],
        "services": [
            "__init__.py",
            "order_service.py",
            "delivery_service.py",
            "accounting_service.py",
            "simulation_service.py",
        ],
        "cli": [
            "__init__.py",
            "main_cli.py",
        ],
        "utils": [
            "__init__.py",
            "exceptions.py",
            "storage.py",
        ],
    },
    "tests": [
        "__init__.py",
        "test_models.py",
        "test_services.py",
        "test_cli.py",
    ],
    "docs": [
        "README.md",
        "design.md",
        "api.md",
    ],
    "diagrams": [
        "class_diagram.puml",
        "state_diagram.puml",
    ],
    "data": [
        "state.json",
    ],
    # файлы в корне проекта
    "root_files": [
        "requirements.txt",
        ".gitignore",
        "main.py",
    ]
}


def create_file(path: Path, content: str = ""):
    """Создаёт файл с минимальным содержимым, если его ещё нет"""
    if path.exists():
        print(f"  Уже существует → {path}")
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Создан → {path}")


def build_structure():
    root = Path(PROJECT_ROOT)
    root.mkdir(exist_ok=True)
    print(f"Создаём структуру проекта: {root.resolve()}\n")

    # src и вложенные модули
    src_root = root / "src"
    for module_name, files in STRUCTURE["src"].items():
        module_path = src_root / module_name
        module_path.mkdir(parents=True, exist_ok=True)
        
        for file_name in files:
            file_path = module_path / file_name
            
            if file_name == "__init__.py":
                create_file(file_path, "# Этот пакет доступен для импорта\n")
            else:
                create_file(file_path, f"# {file_name.replace('.py', '').title()} module\n# TODO: implement\n")

    # tests
    tests_root = root / "tests"
    tests_root.mkdir(exist_ok=True)
    for file_name in STRUCTURE["tests"]:
        create_file(tests_root / file_name, f"# Tests for {file_name.replace('test_', '').replace('.py', '')}\n")

    # docs
    docs_root = root / "docs"
    docs_root.mkdir(exist_ok=True)
    for file_name in STRUCTURE["docs"]:
        title = file_name.replace(".md", "").replace("_", " ").title()
        create_file(docs_root / file_name, f"# {title}\n\n")

    # diagrams
    diagrams_root = root / "diagrams"
    diagrams_root.mkdir(exist_ok=True)
    for file_name in STRUCTURE["diagrams"]:
        create_file(diagrams_root / file_name, "@startuml\n\n' TODO: add diagram content\n\n@enduml\n")

    # data
    data_root = root / "data"
    data_root.mkdir(exist_ok=True)
    for file_name in STRUCTURE["data"]:
        create_file(data_root / file_name, "{}\n")

    # корневые файлы
    for file_name in STRUCTURE["root_files"]:
        path = root / file_name
        
        if file_name == "requirements.txt":
            content = """# Минимальные зависимости\npytest>=7.0\nmypy>=1.0\ntyping-extensions>=4.0\n"""
        elif file_name == ".gitignore":
            content = """__pycache__/
*.py[cod]
*$py.class
.env
.venv/
data/state.json
*.log
"""
        elif file_name == "main.py":
            content = """# Точка входа в приложение
from src.cli.main_cli import run_cli


if __name__ == "__main__":
    run_cli()
"""
        else:
            content = ""

        create_file(path, content)


if __name__ == "__main__":
    print("Создание структуры проекта 'pizzeria_simulation'...\n")
    build_structure()
    print("\nГотово! Структура создана.")
    print(f"Перейдите в папку: cd {PROJECT_ROOT}")
    print("Активируйте виртуальное окружение и установите зависимости:")
    print("python -m venv .venv")
    print("source .venv/bin/activate    # Linux/Mac")
    print(".venv\\Scripts\\activate     # Windows")
    print("pip install -r requirements.txt")
