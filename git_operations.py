"""
Модуль для работы с Git операциями
"""
import os
import random
import subprocess
from datetime import datetime
from pathlib import Path
from git import Repo
from git.exc import GitCommandError


def create_random_file(repo_path: str) -> str:
    """
    Создает случайный файл для коммита
    
    Args:
        repo_path: Путь к репозиторию
        
    Returns:
        Путь к созданному файлу
    """
    repo_path_obj = Path(repo_path)
    
    # Создаем директорию для файлов активности, если её нет
    activity_dir = repo_path_obj / "activity"
    activity_dir.mkdir(exist_ok=True)
    
    # Генерируем случайное имя файла
    file_name = f"activity_{random.randint(1000, 9999)}.txt"
    file_path = activity_dir / file_name
    
    # Создаем файл с случайным содержимым
    content = f"Activity file created at {datetime.now().isoformat()}\n"
    content += f"Random data: {random.randint(100000, 999999)}\n"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(file_path)


def make_commit(repo_path: str, message: str = None, date: datetime = None) -> bool:
    """
    Создает коммит в репозитории
    
    Args:
        repo_path: Путь к репозиторию
        message: Сообщение коммита (если None, будет сгенерировано)
        date: Дата коммита (если None, используется текущая дата)
        
    Returns:
        True если коммит успешно создан, False иначе
    """
    try:
        repo = Repo(repo_path)
        
        # Создаем файл для коммита
        file_path = create_random_file(repo_path)
        relative_path = os.path.relpath(file_path, repo_path)
        
        # Добавляем файл в индекс
        repo.index.add([relative_path])
        
        # Генерируем сообщение коммита, если не указано
        if not message:
            messages = [
                "Update activity",
                "Add activity file",
                "Update documentation",
                "Fix minor issues",
                "Code improvements"
            ]
            message = random.choice(messages)
        
        # Создаем коммит с указанной датой
        if date:
            # Используем переменные окружения для установки даты коммита
            date_str = date.strftime('%Y-%m-%d %H:%M:%S')
            env = os.environ.copy()
            env['GIT_AUTHOR_DATE'] = date_str
            env['GIT_COMMITTER_DATE'] = date_str
            
            # Создаем коммит через git команду с переменными окружения
            # GitPython не поддерживает прямой параметр для даты, используем env
            result = subprocess.run(
                ['git', 'commit', '-m', message, '--date', date_str],
                cwd=repo_path,
                env=env,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise GitCommandError('commit', result.stderr)
        else:
            repo.index.commit(message)
        
        return True
        
    except GitCommandError as e:
        print(f"Ошибка при создании коммита: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False


def push_changes(repo_path: str, token: str = None) -> bool:
    """
    Отправляет изменения на GitHub
    
    Args:
        repo_path: Путь к репозиторию
        token: GitHub токен (опционально, можно использовать из .env)
        
    Returns:
        True если push успешен, False иначе
    """
    try:
        repo = Repo(repo_path)
        
        # Получаем remote (обычно 'origin')
        origin = repo.remote('origin')
        
        # Если есть токен, настраиваем URL с токеном
        if token:
            url = origin.url
            # Если URL не содержит токен, добавляем его
            if '@' not in url or 'x-access-token' not in url:
                # Извлекаем путь из URL
                if url.startswith('https://'):
                    # Формат: https://github.com/user/repo.git
                    url_parts = url.replace('https://', '').replace('.git', '')
                    new_url = f"https://x-access-token:{token}@github.com/{url_parts.split('/', 1)[1]}.git"
                    origin.set_url(new_url)
        
        # Получаем текущую ветку
        current_branch = repo.active_branch.name
        
        # Push изменений
        origin.push(current_branch, force=False)
        
        print(f"Изменения успешно отправлены на GitHub (ветка: {current_branch})")
        return True
        
    except GitCommandError as e:
        print(f"Ошибка при отправке изменений: {e}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка при push: {e}")
        return False


def get_repo_info(repo_path: str) -> dict:
    """
    Получает информацию о репозитории
    
    Args:
        repo_path: Путь к репозиторию
        
    Returns:
        Словарь с информацией о репозитории
    """
    try:
        repo = Repo(repo_path)
        return {
            'is_dirty': repo.is_dirty(),
            'untracked_files': repo.untracked_files,
            'active_branch': repo.active_branch.name,
            'remote_url': repo.remote('origin').url if repo.remotes else None
        }
    except Exception as e:
        print(f"Ошибка при получении информации о репозитории: {e}")
        return {}

