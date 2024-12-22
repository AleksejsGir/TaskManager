import os
import json
from typing import List
from datetime import datetime, timedelta
from tabulate import
from tabulate import tabulate

class Task:
    def __init__(self, title: str, description: str, completed: bool = False, created_at: str = None, completed_at: str = None, deadline: str = None):
        self.title = title
        self.description = description
        self.completed = completed
        self.created_at = created_at if created_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.completed_at = completed_at
        self.deadline = deadline

    # помечаем задачу "выполнена" и записываем время завершения
    def mark_completed(self):
        self.completed = True
        self.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # помечаем задачу "не выполнена" и убираем время завершения и срок выполнения
    def mark_incomplete(self):
        self.completed = False
        self.completed_at = None
        self.deadline = None

    # устанавливаем срок выполнения задачи, обрабатываем исключения
    def set_deadline(self, deadline: str):
        if self.completed:
            print("Задача уже выполнена. Установка срока невозможна.")
            return False
        try:
            deadline_time = datetime.strptime(deadline, "%H:%M %d.%m.%Y")
            self.deadline = deadline_time.strftime("%Y-%m-%d %H:%M:%S")
            return True
        except ValueError:
            print("Некорректный формат даты. Используйте формат 'ЧЧ:ММ ДД.ММ.ГГГГ'.")
            return False

    # рассчитываем оставшееся время до срока выполнения
    def remaining_time(self):
        if not self.deadline:
            return "[ ]"  # если срок не установлен
        if self.completed:
            return "[ ]"  # если задача завершена
        deadline_time = datetime.strptime(self.deadline, "%Y-%m-%d %H:%M:%S")
        remaining = deadline_time - datetime.now()
        if remaining.total_seconds() > 0:
            days = remaining.days
            if days >= 1:
                return f"Более {days} дней"     # если срок выполнения более 1 дня то округляем до дней
            else:       # если меньше 1 дня,то начинается обратный отсчет в формате Час:Мин:Сек
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                return f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            return "[Срок истек]"   # неопределенность в случае, если установленный срок закончился, но статус не изменен

    def to_dict(self, index: int):
        return {
            "#": index,
            "Статус": "[X]" if self.completed else "[ ]",
            "Время": self.remaining_time(),
            "Название задачи": self.title,
            "Описание задачи": self.description,
            "Создано": self.created_at,
            "Завершено": self.completed_at if self.completed else ""
        }

# Класс TaskManager отвечает за управление задачами пользователя
class TaskManager:
    def __init__(self, user_name: str):
        self.user_name = user_name
        self.filename = f"{user_name.replace(' ', '_')}_tasks.json"
        self.last_saved = False
        if os.path.exists(self.filename):
            self.load_from_file()
        else:
            self.tasks: List[Task] = []

    def add_task(self, title: str, description: str):
        task = Task(title, description)
        self.tasks.append(task)
        self.last_saved = False
        print("Задача добавлена.")

    # Удаление задачи с обработкой ошибок
    # Начало изменений для SCRUM-10
    def remove_task(self, index: int):
        try:
            if not self.tasks:
                print("Список задач пуст. Удаление невозможно.")
                return

            if 0 <= index < len(self.tasks):
                removed_task = self.tasks.pop(index)
                self.last_saved = False
                print(f"Задача \"{removed_task.title}\" удалена.")
            else:
                print("Неверный индекс.")
        except IndexError:
            print("Ошибка: индекс вне диапазона.")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
    # Конец изменений для SCRUM-10

    def view_tasks(self):
        if not self.tasks:
            print("Список задач пуст.")
        else:
            tasks_data = [task.to_dict(i + 1) for i, task in enumerate(self.tasks)]
            print(tabulate(tasks_data, headers="keys", tablefmt="grid"))

    # Начало изменений для SCRUM-10
    def change_task_status(self, index: int):
        try:
            if not self.tasks:
                print("Список задач пуст. Изменение статуса невозможно.")
                return

            if 0 <= index < len(self.tasks):
                task = self.tasks[index]
                if task.completed:
                    task.mark_incomplete()
                    print(f"Статус задачи \"{task.title}\" изменен на невыполненный.")
                else:
                    task.mark_completed()
                    print(f"Задача \"{task.title}\" отмечена как выполненная.")
                self.last_saved = False
            else:
                print("Неверный индекс.")
        except ValueError:
            print("Введите корректный номер.")
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
    # Конец изменений для SCRUM-10

    # Начало изменений для SCRUM-10
    def set_task_deadline(self, index: int, deadline: str):
        try:
            if not self.tasks:
                print("Список задач пуст. Установка срока невозможна.")
                return

            if 0 <= index < len(self.tasks):
                if not self.tasks[index].set_deadline(deadline):
                    return
                self.last_saved = False
                print(f"Для задачи \"{self.tasks[index].title}\" установлен срок выполнения.")
            else:
                print("Неверный индекс.")
        except Exception as e:
            print(f"Ошибка при установке срока: {e}")
    # Конец изменений для SCRUM-10

    # Начало изменений для SCRUM-10
    def save_to_file(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump([task.__dict__ for task in self.tasks], file, ensure_ascii=False, indent=4)
            self.last_saved = True
            print(f"Список задач сохранен в файл \"{self.filename}\".")
        except PermissionError:
            print(f"Нет доступа для записи в файл \"{self.filename}\".")
        except Exception as e:
            print(f"Ошибка сохранения в файл: {e}")
    # Конец изменений для SCRUM-10

    def load_from_file(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                tasks_data = json.load(file)
                self.tasks = [Task(**data) for data in tasks_data]
            self.last_saved = True
            print(f"Список задач загружен из файла \"{self.filename}\".")
        except FileNotFoundError:
            print(f"Файл \"{self.filename}\" не найден. Будет создан новый файл при сохранении.")
        except json.JSONDecodeError:
            print("Ошибка чтения данных из файла.")
        except Exception as e:
            print(f"Произошла ошибка при загрузке: {e}")

# Остальные методы и классы остаются без изменений.
