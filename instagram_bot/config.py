import os
import json
from pathlib import Path

class Config:
    """Конфігурація бота"""
    
    # Основні налаштування
    HEADLESS = False  # Запуск в headless режимі
    TIMEOUT = 10  # Таймаут для операцій
    
    # Затримки (в секундах)
    MIN_DELAY = 1
    MAX_DELAY = 3
    HUMAN_DELAY_MIN = 0.1
    HUMAN_DELAY_MAX = 0.3
    
    # Кількість дій
    MAX_LIKES_PER_SESSION = 50
    MAX_COMMENTS_PER_SESSION = 10
    MAX_FOLLOWS_PER_SESSION = 20
    
    # Шляхи до файлів
    BASE_DIR = Path(__file__).parent
    LOGS_DIR = BASE_DIR / "logs"
    SESSIONS_DIR = BASE_DIR / "sessions"
    TEMP_DIR = BASE_DIR / "temp"
    DATA_DIR = BASE_DIR / "data"
    
    # Створення директорій
    for directory in [LOGS_DIR, SESSIONS_DIR, TEMP_DIR, DATA_DIR]:
        directory.mkdir(exist_ok=True)
    
    # User Agents для мобільних пристроїв
    USER_AGENTS = [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; SM-N975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.210 Mobile Safari/537.36"
    ]
    
    # Проксі серверв
    PROXY_SERVERS = [
        # Додайте ваші проксі сервери тут
        # Формат: "ip:port:username:password"
        # Приклад: "192.168.1.1:8080:user:pass"
    ]
    
    # Налаштування капчі
    CAPTCHA_SOLVER = {
        "service": "2captcha",  # 2captcha, anticaptcha, deathbycaptcha
        "api_key": "",  # Ваш API ключ
        "timeout": 120
    }
    
    # Налаштування для обходу детекції
    ANTI_DETECTION = {
        "mouse_movements": True,
        "random_scrolling": True,
        "typing_delays": True,
        "human_pauses": True,
        "viewport_changes": True
    }
    
    # Селектори для Instagram (оновлені для 2025)
    SELECTORS = {
        "login": {
            "username": [
                "input[name='username']",
                "input[aria-label*='username']",
                "input[placeholder*='username']",
                "input[autocomplete='username']"
            ],
            "password": [
                "input[name='password']",
                "input[type='password']",
                "input[aria-label*='password']",
                "input[autocomplete='current-password']"
            ],
            "submit": [
                "button[type='submit']",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Log In')]",
                "//button[contains(text(), 'Увійти')]",
                "//div[@role='button' and contains(text(), 'Log')]",
                "//button[contains(@class, 'login') or contains(@class, 'Login')]"
            ]
        },
        "posts": {
            "container": [
                "article div div div div a",
                "div[role='button'] img[src*='instagram']",
                "article a[href*='/p/']",
                "div[style*='padding-bottom'] a"
            ],
            "like_button": [
                "svg[aria-label='Like']",
                "svg[aria-label='Подобається']",
                "button svg[aria-label*='Like']",
                "div[role='button'] svg[aria-label*='Like']"
            ],
            "unlike_button": [
                "svg[aria-label='Unlike']",
                "svg[aria-label='Не подобається']",
                "button svg[aria-label*='Unlike']"
            ],
            "comment_button": [
                "svg[aria-label='Comment']",
                "svg[aria-label='Коментувати']",
                "button svg[aria-label*='Comment']"
            ],
            "share_button": [
                "svg[aria-label='Share']",
                "svg[aria-label='Поділитися']",
                "button svg[aria-label*='Share']"
            ]
        },
        "stories": {
            "container": [
                "div[role='menu']",
                "div[style*='scroll'] div[role='button']",
                "section div[role='button']"
            ],
            "story_item": [
                "div[role='menu'] div div div",
                "div[style*='border-radius'] img",
                "canvas[style*='border-radius']"
            ],
            "username": [
                "span",
                "div span",
                "button span"
            ],
            "like_button": [
                "svg[aria-label='Like']",
                "svg[aria-label='Подобається']",
                "button[aria-label*='Like']"
            ],
            "reply_input": [
                "textarea[placeholder*='Send message']",
                "textarea[placeholder*='Reply']",
                "textarea[placeholder*='Відповісти']",
                "div[contenteditable='true']"
            ],
            "send_button": [
                "button[type='submit']",
                "//button[contains(text(), 'Send')]",
                "//div[@role='button' and contains(text(), 'Send')]"
            ]
        },
        "profile": {
            "followers": [
                "a[href*='/followers/'] span",
                "//a[contains(@href, 'followers')]//span"
            ],
            "following": [
                "a[href*='/following/'] span",
                "//a[contains(@href, 'following')]//span"
            ],
            "posts_count": [
                "span",
                "div span:first-child"
            ]
        },
        "dialogs": {
            "not_now": [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Не зараз')]",
                "//div[@role='button' and contains(text(), 'Not Now')]"
            ],
            "save_info": [
                "//button[contains(text(), 'Save Info')]",
                "//button[contains(text(), 'Зберегти')]"
            ],
            "turn_on_notifications": [
                "//button[contains(text(), 'Turn on Notifications')]",
                "//button[contains(text(), 'Увімкнути сповіщення')]"
            ],
            "close": [
                "svg[aria-label='Close']",
                "svg[aria-label='Закрити']",
                "button[aria-label='Close']",
                "//button[@aria-label='Close']"
            ]
        },
        "captcha": [
            "div[role='dialog'] img",
            ".captcha-image",
            "img[alt*='captcha']",
            "img[src*='captcha']",
            "img[src*='challenge']"
        ]
    }
    
    # Повідомлення для відповідей на сторіс
    DEFAULT_STORY_REPLIES = [
        "😍",
        "🔥",
        "❤️",
        "Nice!",
        "Cool!",
        "Awesome!",
        "Great!",
        "Love it!",
        "Amazing!",
        "Perfect!"
    ]
    
    # Налаштування бази даних
    DATABASE = {
        "type": "sqlite",
        "path": str(DATA_DIR / "instagram_bot.db"),
        "backup_frequency": 24  # годин
    }
    
    # Налаштування сесій
    SAVE_SESSIONS = False  # Не зберігати сесії для безпеки
    ALWAYS_FRESH_LOGIN = True  # Завжди входити заново
    CLOSE_ALL_DIALOGS = True  # Закривати всі діалоги після входу
    
    # Налаштування для відладки
    DEBUG_MODE = True  # Детальне логування
    SCREENSHOTS_ON_ERROR = True  # Скріншоти при помилках
    SLOW_MODE = True  # Повільний режим для складних випадків
    SECURITY = {
        "max_actions_per_hour": 30,
        "max_actions_per_day": 200,
        "cooldown_after_limit": 3600,  # секунд
        "randomize_actions": True
    }
    
    # Налаштування логування
    LOGGING = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file_rotation": True,
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }
    
    # Налаштування GUI
    GUI = {
        "theme": "dark",
        "window_size": "800x600",
        "resizable": True,
        "auto_save": True,
        "language": "uk"  # українська мова
    }
    
    # Налаштування для мобільної емуляції
    MOBILE_DEVICES = {
        "iPhone_12": {
            "width": 390,
            "height": 844,
            "pixel_ratio": 3.0,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1"
        },
        "iPhone_13": {
            "width": 390,
            "height": 844,
            "pixel_ratio": 3.0,
            "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
        },
        "Samsung_Galaxy_S21": {
            "width": 384,
            "height": 854,
            "pixel_ratio": 2.75,
            "user_agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
        },
        "Google_Pixel_5": {
            "width": 393,
            "height": 851,
            "pixel_ratio": 2.75,
            "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"
        }
    }
    
    @classmethod
    def load_config(cls, config_file=None):
        """Завантаження конфігурації з файлу"""
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    
                # Оновлення налаштувань
                for key, value in config_data.items():
                    if hasattr(cls, key):
                        setattr(cls, key, value)
                        
            except Exception as e:
                print(f"Помилка при завантаженні конфігурації: {e}")
                
    @classmethod
    def save_config(cls, config_file=None):
        """Збереження конфігурації в файл"""
        if not config_file:
            config_file = cls.DATA_DIR / "config.json"
            
        try:
            config_data = {
                "HEADLESS": cls.HEADLESS,
                "TIMEOUT": cls.TIMEOUT,
                "MIN_DELAY": cls.MIN_DELAY,
                "MAX_DELAY": cls.MAX_DELAY,
                "MAX_LIKES_PER_SESSION": cls.MAX_LIKES_PER_SESSION,
                "MAX_COMMENTS_PER_SESSION": cls.MAX_COMMENTS_PER_SESSION,
                "MAX_FOLLOWS_PER_SESSION": cls.MAX_FOLLOWS_PER_SESSION,
                "CAPTCHA_SOLVER": cls.CAPTCHA_SOLVER,
                "ANTI_DETECTION": cls.ANTI_DETECTION,
                "SECURITY": cls.SECURITY,
                "GUI": cls.GUI
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Помилка при збереженні конфігурації: {e}")
            
    @classmethod
    def get_random_user_agent(cls):
        """Отримання випадкового User Agent"""
        import random
        return random.choice(cls.USER_AGENTS)
        
    @classmethod
    def get_random_device(cls):
        """Отримання випадкового мобільного пристрою"""
        import random
        device_name = random.choice(list(cls.MOBILE_DEVICES.keys()))
        return cls.MOBILE_DEVICES[device_name]
        
    @classmethod
    def get_proxy(cls):
        """Отримання проксі сервера"""
        import random
        if cls.PROXY_SERVERS:
            return random.choice(cls.PROXY_SERVERS)
        return None