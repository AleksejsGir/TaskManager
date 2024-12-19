import os
import json
from typing import List
from datetime import datetime, timedelta
import pandas as pd

class Task:
    def __init__(self, title: str, description: str, completed: bool = False, created_at: str = None, completed_at: str = None, deadline: str = None):
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.completed_at = completed_at
        self.deadline = deadline

    def mark_completed(self):
        self.completed = True
        self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def set_deadline(self, hours: int):
        deadline_time = datetime.now() + timedelta(hours=hours)
        self.deadline = deadline_time.strftime("%Y-%m-%d %H:%M:%S")

    def remaining_time(self):
        if not self.deadline:
            return "[  ]"
        deadline_time = datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S")
        remaining = deadline_time - datetime.now()
        if remaining.total_seconds() > 0:
            return f"[{str(remaining).split('.')[0]}]"  # формат остатка времени в часах, минутах, секундах
        else:
            return "[Срок истек]"

    def to_dict(self, index: int):
        return {
            " ": index,
            "Статус": "[X]" if self.completed else "[ ]",
            "Время": self.remaining_time() if not self.completed else "",
            "Название задачи": self.title,
            "Описание задачи": self.description,
            "Создано": self.created_at,
            "Завершено": self.completed_at if self.completed else ""
        }


class TaskManager:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.filename = f"{user_name}_tasks.json"
        if os.path.exists(self.filename):
            self.load_from_file()
        else:
            self.tasks: List[Task] = []

    def add_task(self, title: str, description: str):
        task = Task(title, description)
        self.tasks.append(task)
        print("Задача добавлена.")

    def remove_task(self, index: int):
        if not self.tasks:
            print("Список задач пуст. Удаление невозможно.")
            return

        if 0 <= index < len(self.tasks):
            removed_task = self.tasks.pop(index)
            print(f"Задача \"{removed_task.title}\" удалена.")
        else:
            print("Неверный индекс.")

    def view_tasks(self):
        if not self.tasks:
            print("Список задач пуст.")
        else:
            tasks_data = [task.to_dict(i + 1) for i, task in enumerate(self.tasks)]
            df = pd.DataFrame(tasks_data)
            print(df.to_string(index=False, justify='left'))

    def mark_task_completed(self, index: int):
        if not self.tasks:
            print("Список задач пуст. Отметка выполнения невозможна.")
            return

        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_completed()
            print(f"Задача \"{self.tasks[index].title}\" отмечена как выполненная.")
        else:
            print("Неверный индекс.")

    def set_task_deadline(self, index: int, hours: int):
        if not self.tasks:
            print("Список задач пуст. Установка срока невозможна.")
            return

        if 0 <= index < len(self.tasks):
            self.tasks[index].set_deadline(hours)
            print(f"Для задачи \"{self.tasks[index].title}\" установлен срок выполнения.")
        else:
            print("Неверный индекс.")

    def save_to_file(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump([task.__dict__ for task in self.tasks], file, ensure_ascii=False, indent=4)
            print(f"Список задач сохранен в файл \"{self.filename}\".")
        except Exception as e:
            print(f"Ошибка сохранения в файл: {e}")

    def load_from_file(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                tasks_data = json.load(file)
                self.tasks = [Task(**data) for data in tasks_data]
            print(f"Список задач загружен из файла \"{self.filename}\".")
        except FileNotFoundError:
            print(f"Файл \"{self.filename}\" не найден. Будет создан новый файл при сохранении.")
        except json.JSONDecodeError:
            print("Ошибка чтения данных из файла.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке: {e}")


def validate_name(prompt):
    while True:
        name = input(prompt).strip()
        if name.isalpha() and name.isascii():
            return name
        print("Введите корректное имя (только латинские буквы).")


def main():
    print("Добро пожаловать в Task Manager!")
    first_name = validate_name("Введите ваше имя: ")
    last_name = validate_name("Введите вашу фамилию: ")
    user_name = f"{first_name}_{last_name}"

    manager = TaskManager(user_name)

    while True:
        print(f"\nМеню: ({first_name} {last_name})")
        print("1. Просмотреть список задач")
        print("2. Добавить задачу")
        print("3. Удалить задачу")
        print("4. Сохранить задачи в файл")
        print("5. Отметить задачу как выполненную")
        print("6. Установить срок выполнения задачи")
        print("0. Выйти")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            manager.view_tasks()
        elif choice == "2":
            title = input("Введите название задачи: ").strip()
            description = input("Введите описание задачи: ").strip()
            manager.add_task(title, description)
        elif choice == "3":
            manager.view_tasks()
            try:
                index = int(input("Введите номер задачи для удаления: ").strip()) - 1
                manager.remove_task(index)
            except ValueError:
                print("Введите корректный номер.")
        elif choice == "4":
            manager.save_to_file()
        elif choice == "5":
            manager.view_tasks()
            try:
                index = int(input("Введите номер задачи для отметки как выполненной: ").strip()) - 1
                manager.mark_task_completed(index)
            except ValueError:
                print("Введите корректный номер.")
        elif choice == "6":
            manager.view_tasks()
            try:
                index = int(input("Введите номер задачи для установки срока выполнения: ").strip()) - 1
                hours = int(input("Введите срок выполнения в часах: ").strip())
                manager.set_task_deadline(index, hours)
            except ValueError:
                print("Введите корректные данные.")
        elif choice == "0":
            while True:
                save_choice = input("Сохранить изменения перед выходом? Yes(Y)/No(N): ").strip().lower()
                if save_choice in ("y", "yes"):
                    manager.save_to_file()
                    break
                elif save_choice in ("n", "no"):
                    break
                else:
                    print("Нажмите Yes(Y)/No(N).")
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    main()
