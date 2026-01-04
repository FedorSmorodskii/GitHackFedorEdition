"""
Главный скрипт для автоматизированных коммитов на GitHub
Заполняет график contributions через коммиты с разными датами
"""
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
import git_operations


def load_config(config_path: str = "config.json") -> dict:
    """
    Загружает конфигурацию из JSON файла
    
    Args:
        config_path: Путь к файлу конфигурации
        
    Returns:
        Словарь с конфигурацией
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл конфигурации {config_path} не найден!")
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка при чтении конфигурации: {e}")
        return {}


def parse_date(date_str: str) -> datetime:
    """
    Парсит дату из строки формата YYYY-MM-DD
    
    Args:
        date_str: Строка с датой
        
    Returns:
        Объект datetime
    """
    return datetime.strptime(date_str, "%Y-%m-%d")


def generate_activity_pattern(pattern_type: str, day: datetime) -> int:
    """
    Генерирует количество коммитов для дня на основе паттерна
    
    Args:
        pattern_type: Тип паттерна ('random', 'weekday', 'consistent')
        day: Дата дня
        
    Returns:
        Количество коммитов для дня
    """
    if pattern_type == "random":
        return random.randint(1, 10)
    elif pattern_type == "weekday":
        # Больше активности в будние дни
        if day.weekday() < 5:  # Понедельник-Пятница
            return random.randint(3, 10)
        else:  # Выходные
            return random.randint(1, 5)
    elif pattern_type == "consistent":
        return random.randint(2, 5)
    else:
        return random.randint(1, 5)


def fill_contributions_graph(config: dict, token: str = None):
    """
    Заполняет график contributions коммитами за указанный период
    
    Args:
        config: Конфигурация из config.json
        token: GitHub токен для push
    """
    fill_config = config.get("fill_contributions", {})
    
    if not fill_config.get("enabled", False):
        print("Заполнение графика contributions отключено в конфигурации")
        return
    
    repo_path = config.get("repository_path", ".")
    
    # Проверяем, что путь существует и это git репозиторий
    if not os.path.exists(repo_path):
        print(f"Путь к репозиторию не существует: {repo_path}")
        return
    
    if not os.path.exists(os.path.join(repo_path, ".git")):
        print(f"Указанный путь не является git репозиторием: {repo_path}")
        return
    
    # Парсим даты
    try:
        start_date = parse_date(fill_config.get("start_date", "2024-01-01"))
        end_date = parse_date(fill_config.get("end_date", datetime.now().strftime("%Y-%m-%d")))
    except ValueError as e:
        print(f"Ошибка при парсинге дат: {e}")
        return
    
    min_commits = fill_config.get("min_commits_per_day", 1)
    max_commits = fill_config.get("max_commits_per_day", 10)
    pattern = fill_config.get("activity_pattern", "random")
    weekend_activity = fill_config.get("weekend_activity", True)
    commit_messages = config.get("commit_messages", ["Update"])
    auto_push = config.get("auto_push", True)
    
    print(f"Начинаю заполнение графика contributions...")
    print(f"Период: {start_date.date()} - {end_date.date()}")
    print(f"Режим: {pattern}, Коммитов в день: {min_commits}-{max_commits}")
    
    current_date = start_date
    total_commits = 0
    days_processed = 0
    
    while current_date <= end_date:
        # Пропускаем выходные, если отключена активность в выходные
        if not weekend_activity and current_date.weekday() >= 5:
            current_date += timedelta(days=1)
            continue
        
        # Определяем количество коммитов для дня
        commits_count = generate_activity_pattern(pattern, current_date)
        commits_count = max(min_commits, min(commits_count, max_commits))
        
        # Создаем коммиты для этого дня
        for i in range(commits_count):
            # Генерируем случайное время в течение дня
            hour = random.randint(9, 20)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            
            commit_date = current_date.replace(hour=hour, minute=minute, second=second)
            
            # Выбираем случайное сообщение коммита
            message = random.choice(commit_messages) if commit_messages else "Update"
            
            # Создаем коммит с указанной датой
            if git_operations.make_commit(repo_path, message, commit_date):
                total_commits += 1
                print(f"✓ Коммит создан: {commit_date.strftime('%Y-%m-%d %H:%M:%S')} - {message}")
            else:
                print(f"✗ Не удалось создать коммит для {commit_date.strftime('%Y-%m-%d')}")
        
        days_processed += 1
        current_date += timedelta(days=1)
        
        # Показываем прогресс каждые 30 дней
        if days_processed % 30 == 0:
            print(f"Обработано дней: {days_processed}, Создано коммитов: {total_commits}")
    
    print(f"\nЗаполнение завершено!")
    print(f"Всего обработано дней: {days_processed}")
    print(f"Всего создано коммитов: {total_commits}")
    
    # Отправляем изменения на GitHub
    if auto_push and token:
        print("\nОтправляю изменения на GitHub...")
        if git_operations.push_changes(repo_path, token):
            print("✓ Изменения успешно отправлены на GitHub")
            print("График contributions должен обновиться в течение нескольких минут")
        else:
            print("✗ Не удалось отправить изменения на GitHub")
            print("Вы можете сделать push вручную: git push origin <branch>")
    elif auto_push and not token:
        print("\n⚠ GitHub токен не указан. Изменения не отправлены.")
        print("Укажите GITHUB_TOKEN в .env файле или отправьте изменения вручную")


def main():
    """Главная функция"""
    # Загружаем переменные окружения
    load_dotenv()
    
    # Загружаем конфигурацию
    config = load_config()
    
    if not config:
        print("Не удалось загрузить конфигурацию. Проверьте файл config.json")
        return
    
    # Получаем токен из переменных окружения
    token = os.getenv("GITHUB_TOKEN")
    
    if not token:
        print("⚠ Предупреждение: GITHUB_TOKEN не найден в .env файле")
        print("Создайте .env файл на основе .env.example")
        print("Push на GitHub будет недоступен без токена")
    
    # Проверяем настройки репозитория
    repo_path = config.get("repository_path", ".")
    if repo_path == ".":
        repo_path = os.getcwd()
    
    print("=" * 60)
    print("GitHub Auto Commit Tool")
    print("=" * 60)
    print(f"Репозиторий: {repo_path}")
    
    # Показываем информацию о репозитории
    repo_info = git_operations.get_repo_info(repo_path)
    if repo_info:
        print(f"Ветка: {repo_info.get('active_branch', 'unknown')}")
        if repo_info.get('remote_url'):
            print(f"Remote: {repo_info['remote_url']}")
    
    print("=" * 60)
    
    # Заполняем график contributions
    fill_contributions_graph(config, token)
    
    print("\n" + "=" * 60)
    print("Работа завершена!")
    print("=" * 60)


if __name__ == "__main__":
    main()

