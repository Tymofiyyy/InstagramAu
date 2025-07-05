import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from config import Config
from utils import AntiDetection

class InstagramBot:
    def __init__(self, username, password, proxy=None):
        self.username = username
        self.password = password
        self.proxy = proxy
        self.driver = None
        self.logged_in = False
        self.anti_detection = AntiDetection()
        self.setup_logging()
        
    def setup_logging(self):
        """Налаштування логування"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/{self.username}_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(f'InstagramBot_{self.username}')
        
    def setup_driver(self):
        """Налаштування веб-драйвера з обходом детекції"""
        chrome_options = Options()
        
        # Обхід детекції ботів
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins-discovery')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        
        # Мобільна емуляція
        mobile_emulation = {
            "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 3.0},
            "userAgent": Config.USER_AGENTS[random.randint(0, len(Config.USER_AGENTS)-1)]
        }
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Проксі
        if self.proxy:
            chrome_options.add_argument(f'--proxy-server={self.proxy}')
            
        # Headless режим (опційно)
        if Config.HEADLESS:
            chrome_options.add_argument('--headless')
            
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Приховування webdriver
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Встановлення viewport
        self.driver.set_window_size(375, 667)
        
    def human_like_delay(self, min_delay=1, max_delay=3):
        """Затримка з імітацією людської поведінки"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        
    def validate_credentials(self):
        """Перевірка правильності логіна і пароля"""
        if not self.username or not self.password:
            self.logger.error("Логін або пароль не вказані")
            return False
            
        if len(self.username) < 3:
            self.logger.error("Логін занадто короткий")
            return False
            
        if len(self.password) < 6:
            self.logger.error("Пароль занадто короткий")
            return False
            
        # Перевірка на недопустимі символи
        import re
        if not re.match("^[a-zA-Z0-9._]+$", self.username):
            self.logger.error("Логін містить недопустимі символи")
            return False
            
        self.logger.info(f"Логін {self.username} пройшов валідацію")
        return True
        
    def login(self):
        """Універсальний вхід в акаунт (працює з різними версіями сторінки)"""
        try:
            # Перевірка правильності даних
            if not self.validate_credentials():
                return False
                
            self.setup_driver()
            self.driver.get("https://www.instagram.com/accounts/login/")
            self.human_like_delay(3, 5)
            
            # Спочатку визначаємо тип сторінки входу
            page_type = self.detect_login_page_type()
            self.logger.info(f"Виявлено тип сторінки входу: {page_type}")
            
            if page_type == "new_layout":
                return self.login_new_layout()
            elif page_type == "old_layout":
                return self.login_old_layout()
            else:
                # Якщо не вдалося визначити, пробуємо обидва методи
                self.logger.info("Тип сторінки не визначено, пробуємо обидва методи")
                if self.login_new_layout():
                    return True
                return self.login_old_layout()
                
        except Exception as e:
            self.logger.error(f"Помилка при вході: {e}")
            return False
            
    def detect_login_page_type(self):
        """Покращене визначення типу сторінки входу"""
        try:
            # Очікуємо повного завантаження сторінки
            self.human_like_delay(3, 5)
            
            # Сильні індикатори нової версії
            new_layout_strong = [
                "input[name='username']",
                "button[type='submit']"
            ]
            
            # Сильні індикатори старої версії
            old_layout_strong = [
                "input[aria-label*='Phone number, username, or email']",
                "div[role='button'][tabindex='0']"
            ]
            
            # Слабкі індикатори
            new_layout_weak = [
                "form[method='post']",
                "input[autocomplete='username']"
            ]
            
            old_layout_weak = [
                "div[role='button'] div[dir='auto']",
                "input[aria-label*='Username']"
            ]
            
            new_strong_score = 0
            old_strong_score = 0
            new_weak_score = 0
            old_weak_score = 0
            
            # Перевірка сильних індикаторів нової версії
            for selector in new_layout_strong:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if any(el.is_displayed() for el in elements):
                        new_strong_score += 2
                        self.logger.debug(f"Знайдено сильний індикатор нової версії: {selector}")
                except:
                    pass
            
            # Перевірка сильних індикаторів старої версії
            for selector in old_layout_strong:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if any(el.is_displayed() for el in elements):
                        old_strong_score += 2
                        self.logger.debug(f"Знайдено сильний індикатор старої версії: {selector}")
                except:
                    pass
            
            # Перевірка слабких індикаторів нової версії
            for selector in new_layout_weak:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if any(el.is_displayed() for el in elements):
                        new_weak_score += 1
                except:
                    pass
            
            # Перевірка слабких індикаторів старої версії
            for selector in old_layout_weak:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if any(el.is_displayed() for el in elements):
                        old_weak_score += 1
                except:
                    pass
            
            new_total_score = new_strong_score + new_weak_score
            old_total_score = old_strong_score + old_weak_score
            
            self.logger.debug(f"Оцінки: Нова версія - {new_total_score} (сильні: {new_strong_score}, слабкі: {new_weak_score})")
            self.logger.debug(f"Оцінки: Стара версія - {old_total_score} (сильні: {old_strong_score}, слабкі: {old_weak_score})")
            
            # Якщо є сильні індикатори - віддаємо перевагу їм
            if new_strong_score > 0 and old_strong_score == 0:
                return "new_layout"
            elif old_strong_score > 0 and new_strong_score == 0:
                return "old_layout"
            # Якщо обидва мають сильні індикатори або ніхто не має - дивимось загальну оцінку
            elif new_total_score > old_total_score:
                return "new_layout"
            elif old_total_score > new_total_score:
                return "old_layout"
            else:
                # Якщо оцінки рівні - додаткова перевірка по URL та заголовку
                page_source = self.driver.page_source.lower()
                if 'react' in page_source or 'webpack' in page_source:
                    self.logger.debug("Виявлено React/Webpack - ймовірно стара версія")
                    return "old_layout"
                else:
                    self.logger.debug("Не виявлено специфічних ознак - за замовчуванням нова версія")
                    return "new_layout"
                
        except Exception as e:
            self.logger.error(f"Помилка визначення типу сторінки: {e}")
            return "unknown"
            
    def login_new_layout(self):
        """Вхід для нової версії сторінки"""
        try:
            self.logger.info("Використання методу для нової версії сторінки")
            
            # Пошук поля username (нова версія)
            username_selectors = [
                "input[name='username']",
                "input[aria-label*='Phone number, username']",
                "input[placeholder*='Phone number, username']",
                "input[type='text']"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    username_input = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if username_input.is_displayed():
                        self.logger.info(f"Знайдено поле username: {selector}")
                        break
                except:
                    continue
            
            if not username_input:
                self.logger.warning("Не знайдено поле username в новій версії")
                return False
            
            # Пошук поля password (нова версія)
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[aria-label*='Password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if password_input.is_displayed():
                        self.logger.info(f"Знайдено поле password: {selector}")
                        break
                except:
                    continue
            
            if not password_input:
                self.logger.warning("Не знайдено поле password в новій версії")
                return False
            
            # Введення даних
            self.logger.info("Введення username...")
            username_input.clear()
            self.anti_detection.human_typing(username_input, self.username)
            self.human_like_delay(1, 2)
                
            self.logger.info("Введення password...")
            password_input.clear()
            self.anti_detection.human_typing(password_input, self.password)
            self.human_like_delay(1, 2)
            
            # Пошук кнопки входу (нова версія)
            login_selectors = [
                "button[type='submit']",
                "div[role='button'][tabindex='0']",
                "//button[contains(text(), 'Log in')]",
                "//button[contains(text(), 'Log In')]",
                "//div[@role='button' and contains(text(), 'Log')]"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        login_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    if login_button and login_button.is_displayed():
                        self.logger.info(f"Знайдено кнопку входу: {selector}")
                        break
                except:
                    continue
            
            # Спроба входу
            if login_button:
                self.logger.info("Натискання кнопки для входу...")
                login_button.click()
            else:
                self.logger.info("Кнопка входу не знайдена, використовуємо Enter...")
                password_input.send_keys(Keys.RETURN)
            
            return self.wait_for_login_result()
                
        except Exception as e:
            self.logger.error(f"Помилка в новій версії входу: {e}")
            return False
            
    def login_old_layout(self):
        """Покращений вхід для старої версії сторінки"""
        try:
            self.logger.info("Використання покращеного методу для старої версії сторінки")
            
            # Додаткове очікування для старої версії
            self.human_like_delay(2, 4)
            
            # Розширений пошук поля username для старої версії
            username_selectors = [
                "input[aria-label*='Phone number, username, or email']",
                "input[aria-label*='Phone number, username']", 
                "input[aria-label*='Username']",
                "input[placeholder*='Phone number, username, or email']",
                "input[placeholder*='Username']",
                "input[name='username']",
                "input[type='text']:first-of-type",
                "form input[type='text']"
            ]
            
            username_input = None
            for selector in username_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            username_input = element
                            self.logger.info(f"Знайдено поле username: {selector}")
                            break
                    if username_input:
                        break
                except Exception as e:
                    self.logger.debug(f"Селектор {selector} не спрацював: {e}")
                    continue
            
            if not username_input:
                self.logger.warning("Не знайдено поле username в старій версії")
                return False
            
            # Розширений пошук поля password для старої версії
            password_selectors = [
                "input[aria-label*='Password']",
                "input[type='password']",
                "input[name='password']",
                "form input[type='password']"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            password_input = element
                            self.logger.info(f"Знайдено поле password: {selector}")
                            break
                    if password_input:
                        break
                except Exception as e:
                    self.logger.debug(f"Селектор {selector} не спрацював: {e}")
                    continue
            
            if not password_input:
                self.logger.warning("Не знайдено поле password в старій версії")
                return False
            
            # Очищення полів перед введенням
            try:
                username_input.clear()
                password_input.clear()
            except:
                pass
            
            # Введення username з фокусом
            self.logger.info("Введення username (стара версія)...")
            try:
                username_input.click()  # Клік для фокусу
                self.human_like_delay(0.5, 1)
                self.anti_detection.human_typing(username_input, self.username)
            except Exception as e:
                self.logger.warning(f"Помилка при введенні username: {e}")
                username_input.send_keys(self.username)
            
            self.human_like_delay(1, 2)
                
            # Введення password з фокусом
            self.logger.info("Введення password (стара версія)...")
            try:
                password_input.click()  # Клік для фокусу
                self.human_like_delay(0.5, 1)
                self.anti_detection.human_typing(password_input, self.password)
            except Exception as e:
                self.logger.warning(f"Помилка при введенні password: {e}")
                password_input.send_keys(self.password)
            
            self.human_like_delay(1, 2)
            
            # Покращений пошук кнопки входу для старої версії
            login_selectors = [
                # Точні селектори для кнопки "Log in"
                "//div[@role='button' and normalize-space(text())='Log in']",
                "//div[@role='button' and normalize-space(text())='Log In']",
                "//button[normalize-space(text())='Log in']",
                "//button[normalize-space(text())='Log In']",
                
                # Селектори по структурі кнопки
                "div[role='button'][tabindex='0']:has(div[dir='auto'])",
                "button[type='submit']",
                
                # Селектори по позиції (кнопка входу зазвичай після полів)
                "form div[role='button']:last-of-type",
                "div[role='button'][tabindex='0']:last-of-type"
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            element_text = element.get_attribute('textContent') or element.text or ""
                            
                            # Фільтруємо кнопки по довжині тексту та змісту
                            if len(element_text.strip()) < 50:  # Коротший текст
                                if any(keyword in element_text.lower() for keyword in ['log in', 'log', 'sign in', 'enter']):
                                    login_button = element
                                    self.logger.info(f"Знайдено кнопку входу: {selector}, текст: '{element_text.strip()}'")
                                    break
                                elif element_text.strip() == "":  # Кнопка без тексту, але з role='button'
                                    # Додаткова перевірка що це не випадковий елемент
                                    if element.get_attribute('tabindex') == '0':
                                        login_button = element
                                        self.logger.info(f"Знайдено кнопку входу без тексту: {selector}")
                                        break
                    
                    if login_button:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Помилка з селектором {selector}: {e}")
                    continue
            
            # Спроба входу з покращеними методами
            if login_button:
                self.logger.info("Натискання кнопки входу (стара версія)...")
                try:
                    # Спочатку перевіряємо чи кнопка активна
                    if login_button.is_enabled():
                        # Скролимо до кнопки якщо потрібно
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                        self.human_like_delay(0.5, 1)
                        
                        # Пробуємо звичайний клік
                        login_button.click()
                        self.logger.info("Використано звичайний клік")
                    else:
                        self.logger.warning("Кнопка не активна, використовуємо Enter")
                        password_input.send_keys(Keys.RETURN)
                        
                except Exception as e:
                    self.logger.warning(f"Звичайний клік не спрацював: {e}")
                    try:
                        # Пробуємо JavaScript клік
                        self.driver.execute_script("arguments[0].click();", login_button)
                        self.logger.info("Використано JavaScript клік")
                    except Exception as e2:
                        self.logger.warning(f"JavaScript клік не спрацював: {e2}")
                        # Останній варіант - Enter
                        password_input.send_keys(Keys.RETURN)
                        self.logger.info("Використано Enter як останній варіант")
            else:
                self.logger.info("Кнопка входу взагалі не знайдена, використовуємо прямий Enter...")
                password_input.send_keys(Keys.RETURN)
            
            return self.wait_for_login_result()
                
        except Exception as e:
            self.logger.error(f"Помилка в старій версії входу: {e}")
            return False
            
    def wait_for_login_result(self):
        """Очікування результату входу (універсальний метод)"""
        try:
            self.logger.info("Очікування результату входу...")
            
            start_time = time.time()
            timeout = 30
            
            while time.time() - start_time < timeout:
                current_url = self.driver.current_url
                
                # Перевірка на успішний вхід
                if current_url != "https://www.instagram.com/accounts/login/" and "login" not in current_url:
                    self.logger.info(f"URL змінився на: {current_url}")
                    
                    if "challenge" in current_url:
                        self.logger.warning("Потрібно пройти challenge")
                        return False
                    
                    if "two_factor" in current_url or "2fa" in current_url:
                        self.logger.warning("Потрібна двофакторна автентифікація")
                        return False
                        
                    # Успішний вхід
                    self.handle_post_login_dialogs()
                    self.logged_in = True
                    self.logger.info(f"Успішний вхід для {self.username}")
                    return True
                
                # Перевірка на помилки входу
                error_selectors = [
                    "div[role='alert']", 
                    "#slfErrorAlert", 
                    "div[data-testid='login-error']",
                    "p[data-testid='login-error-message']",
                    "div[id*='error']",
                    "span[data-testid='login-error-message']"
                ]
                
                for selector in error_selectors:
                    try:
                        error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for error_el in error_elements:
                            if error_el.is_displayed() and error_el.text.strip():
                                error_text = error_el.text.strip()
                                self.logger.error(f"Помилка входу: {error_text}")
                                return False
                    except:
                        continue
                
                # Перевірка на наявність Home іконки
                home_selectors = [
                    "svg[aria-label='Home']", 
                    "a[href='/']",
                    "div[data-testid='mobile-nav-home']",
                    "a[aria-label='Home']"
                ]
                
                for selector in home_selectors:
                    try:
                        home_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for home_el in home_elements:
                            if home_el.is_displayed():
                                self.logger.info("Знайдено Home елемент - успішний вхід")
                                self.handle_post_login_dialogs()
                                self.logged_in = True
                                self.logger.info(f"Успішний вхід для {self.username}")
                                return True
                    except:
                        continue
                
                time.sleep(1)
            
            # Timeout
            current_url = self.driver.current_url
            self.logger.error(f"Timeout при вході. Фінальний URL: {current_url}")
            
            # Остання спроба перевірки
            if "login" not in current_url:
                self.logger.info("Можливо вхід все ж таки успішний, перевіряємо...")
                home_elements = self.driver.find_elements(By.CSS_SELECTOR, "svg[aria-label='Home'], a[href='/']")
                if home_elements and any(el.is_displayed() for el in home_elements):
                    self.handle_post_login_dialogs()
                    self.logged_in = True
                    self.logger.info(f"Успішний вхід для {self.username} (затримана перевірка)")
                    return True
            
            return False
                
        except Exception as e:
            self.logger.error(f"Помилка при очікуванні результату: {e}")
            return False
            
    def handle_post_login_dialogs(self):
        """Обробка діалогів після входу"""
        dialogs_handled = 0
        max_dialogs = 5
        
        self.logger.info("Початок обробки діалогів після входу...")
        
        while dialogs_handled < max_dialogs:
            self.human_like_delay(1, 2)
            dialog_found = False
            
            # Селектори для закриття діалогів
            close_selectors = [
                "//button[contains(text(), 'Not Now')]",
                "//button[contains(text(), 'Не зараз')]",
                "//button[@aria-label='Close']",
                "svg[aria-label='Close']",
                "//button[contains(text(), 'Skip')]",
                "//button[contains(text(), 'Cancel')]"
            ]
            
            for selector in close_selectors:
                try:
                    if selector.startswith("//"):
                        elements = self.driver.find_elements(By.XPATH, selector)
                    else:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            try:
                                element.click()
                                self.logger.info(f"Закрито діалог: {selector}")
                                dialog_found = True
                                self.human_like_delay(1, 2)
                                break
                            except:
                                continue
                    
                    if dialog_found:
                        break
                        
                except:
                    continue
            
            if dialog_found:
                dialogs_handled += 1
            else:
                break
            
        self.logger.info(f"Обробка діалогів завершена. Закрито {dialogs_handled} діалогів")
        
        # Фінальне закриття через Escape
        try:
            remaining_dialogs = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog']")
            if remaining_dialogs:
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except:
            pass

    def like_recent_posts(self, target_username, count=2):
        """Лайк останніх постів: профіль → пост1 → лайк → назад → пост2 → лайк → назад"""
        try:
            profile_url = f"https://www.instagram.com/{target_username}/"
            self.driver.get(profile_url)
            self.logger.info(f"📍 Перехід на профіль {target_username}")
            self.human_like_delay(3, 5)
            
            # Пошук постів на профілі
            post_selectors = [
                "article a[href*='/p/']",
                "div[style*='padding-bottom'] a[href*='/p/']",
                "a[href*='/p/']"
            ]
            
            posts = []
            for selector in post_selectors:
                try:
                    found_posts = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_posts:
                        posts = found_posts[:count]
                        self.logger.info(f"📸 Знайдено {len(posts)} постів для лайку")
                        break
                except:
                    continue
            
            if not posts:
                self.logger.warning(f"❌ Не знайдено постів у профілі {target_username}")
                return False
            
            # Збереження посилань на пости
            post_links = []
            for post in posts:
                try:
                    href = post.get_attribute('href')
                    if href:
                        post_links.append(href)
                except:
                    continue
            
            if not post_links:
                self.logger.warning("❌ Не вдалося отримати посилання на пости")
                return False
            
            self.logger.info(f"🔗 Отримано {len(post_links)} посилань на пости")
            liked_count = 0
            
            # Лайк кожного поста з поверненням до профілю
            for i, post_url in enumerate(post_links):
                try:
                    self.logger.info(f"📸 Відкриваємо пост {i+1}/{len(post_links)}")
                    
                    # Перехід до поста
                    self.driver.get(post_url)
                    self.human_like_delay(3, 5)
                    
                    # Очікування завантаження поста
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
                        )
                    except:
                        self.logger.warning(f"⚠️ Пост {i+1} не завантажився")
                        continue
                    
                    # Пошук кнопки лайка
                    like_selectors = [
                        "svg[aria-label='Like']",
                        "svg[aria-label='Подобається']", 
                        "button svg[aria-label*='Like']",
                        "span[role='button'] svg[aria-label='Like']"
                    ]
                    
                    like_button = None
                    for selector in like_selectors:
                        try:
                            like_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                            for like_el in like_elements:
                                if like_el.is_displayed():
                                    like_button = like_el
                                    break
                            if like_button:
                                break
                        except:
                            continue
                    
                    if like_button:
                        # Перевірка чи пост вже лайкнутий
                        aria_label = like_button.get_attribute('aria-label') or ""
                        
                        if 'Unlike' in aria_label or 'Не подобається' in aria_label:
                            self.logger.info(f"ℹ️ Пост {i+1} вже лайкнутий, пропускаємо")
                        else:
                            # Спроба лайку
                            try:
                                parent_button = like_button.find_element(By.XPATH, "./ancestor::*[@role='button' or @tabindex='0'][1]")
                                parent_button.click()
                                self.logger.info(f"❤️ Лайк поста {i+1} користувача {target_username}")
                                liked_count += 1
                            except:
                                try:
                                    self.driver.execute_script("arguments[0].click();", like_button)
                                    self.logger.info(f"❤️ Лайк поста {i+1} користувача {target_username} (JS)")
                                    liked_count += 1
                                except:
                                    self.logger.warning(f"❌ Не вдалося поставити лайк на пост {i+1}")
                        
                        # Затримка після лайка
                        self.human_like_delay(2, 4)
                    else:
                        self.logger.warning(f"❌ Не знайдено кнопку лайка для поста {i+1}")
                    
                    # Повернення до профілю (завжди після кожного поста)
                    self.logger.info(f"🔙 Повертаємося до профілю після поста {i+1}")
                    self.driver.get(profile_url)
                    self.human_like_delay(2, 3)
                    
                except Exception as e:
                    self.logger.error(f"❌ Помилка при обробці поста {i+1}: {e}")
                    # При помилці також повертаємося до профілю
                    try:
                        self.driver.get(profile_url)
                        self.human_like_delay(2, 3)
                    except:
                        pass
                    continue
                    
            self.logger.info(f"✅ Завершено лайки постів: {liked_count}/{len(post_links)} успішно")
            return liked_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Критична помилка при лайку постів: {e}")
            return False

    def process_story(self, target_username, messages):
     """Обробка сторіс: прямий перехід на профіль → аватарка → швидкий лайк → швидка відповідь"""
     try:
        # 1. Прямий перехід на профіль цільового користувача
        profile_url = f"https://www.instagram.com/{target_username}/"
        self.driver.get(profile_url)
        self.logger.info(f"📍 Прямий перехід на профіль {target_username}")
        self.human_like_delay(2, 3)

        # 2. Пошук аватара зі сторіс (має border/рамку)
        story_avatar_selectors = [
            "button canvas[style*='border']",  # Кнопка з обведенням
            "div[style*='border'] button",     # Кнопка в обведеному контейнері
            "img[style*='border']",            # Аватар з рамкою
            "button[aria-label*='story']",     # Кнопка з підписом "story"
            "div[role='button'][tabindex='0']" # Альтернативний варіант
        ]
        
        story_avatar = None
        for selector in story_avatar_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        story_avatar = element
                        self.logger.info(f"📱 Знайдено аватар зі сторіс: {selector}")
                        break
                if story_avatar:
                    break
            except Exception as e:
                self.logger.debug(f"Помилка пошуку сторіс через селектор {selector}: {e}")
                continue
        
        if not story_avatar:
            self.logger.info(f"📭 Активних сторіс у {target_username} не знайдено")
            return False
            
        # 3. Відкриття сторіс
        self.logger.info(f"🎬 Відкриття сторіс {target_username}")
        try:
            story_avatar.click()
        except:
            self.driver.execute_script("arguments[0].click();", story_avatar)
        self.human_like_delay(1, 2)  # Зменшено затримку

        # 4. ШВИДКИЙ лайк сторіс (одразу після відкриття)
        story_liked = False
        like_selectors = [
            "svg[aria-label='Like']",
            "svg[aria-label='Подобається']",
            "button[aria-label*='Like']",
            "span[role='button'] svg[aria-label*='Like']"
        ]
        
        for selector in like_selectors:
            try:
                like_button = WebDriverWait(self.driver, 3).until(  # Зменшено час очікування
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if 'Unlike' not in (like_button.get_attribute('aria-label') or ''):
                    like_button.click()
                    story_liked = True
                    self.logger.info("❤️ Поставлено лайк сторіс")
                    break
            except:
                continue

        if not story_liked:
            self.logger.warning("⚠️ Не вдалося поставити лайк сторіс")

        # 5. ШВИДКА відповідь на сторіс (одразу після лайку)
        story_replied = False
        reply_selectors = [
            "textarea[placeholder*='Send message']",
            "textarea[placeholder*='Reply']",
            "div[contenteditable='true'][aria-label*='Message']",
            "textarea[placeholder*='Надіслати повідомлення']"
        ]
        
        for selector in reply_selectors:
            try:
                reply_input = WebDriverWait(self.driver, 3).until(  # Зменшено час очікування
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                message = random.choice(messages)
                reply_input.clear()
                self.anti_detection.human_typing(reply_input, message)
                self.logger.info(f"💬 Введено відповідь: {message}")
                
                # Пошук кнопки Send (знаходиться справа від поля вводу)
                send_button_found = False
                
                # Спочатку шукаємо кнопку відносно поля вводу
                try:
                    # Знаходимо батьківський контейнер поля вводу
                    parent_container = reply_input.find_element(By.XPATH, "./..")
                    
                    # Шукаємо кнопку Send в тому ж контейнері
                    send_selectors_relative = [
                        ".//button[contains(@aria-label, 'Send')]",
                        ".//button[contains(@aria-label, 'Надіслати')]",
                        ".//div[@role='button'][contains(@tabindex, '0')]//svg",
                        ".//button[contains(@type, 'submit')]",
                        ".//button[.//*[name()='svg']]"
                    ]
                    
                    for selector in send_selectors_relative:
                        try:
                            send_button = parent_container.find_element(By.XPATH, selector)
                            if send_button.is_displayed():
                                send_button.click()
                                send_button_found = True
                                self.logger.info("📤 Натиснуто кнопку Send (відносний пошук)")
                                break
                        except:
                            continue
                            
                except Exception as e:
                    self.logger.debug(f"Помилка відносного пошуку: {e}")
                
                # Якщо відносний пошук не спрацював, шукаємо глобально
                if not send_button_found:
                    send_selectors = [
                        "button[aria-label*='Send']",
                        "button[aria-label*='Надіслати']",
                        "div[role='button'][tabindex='0'] svg[aria-label*='Send']",
                        "div[role='button'][tabindex='0'] svg[aria-label*='Надіслати']",
                        "button[type='submit']",
                        "svg[aria-label*='Send']",
                        "svg[aria-label*='Надіслати']",
                        "button:has(svg[aria-label*='Send'])",
                        "button:has(svg[aria-label*='Надіслати'])",
                        # Додаткові селектори для кнопки Send
                        "button svg[viewBox*='24'][fill*='#']",  # Типова іконка відправки
                        "div[role='button'] svg[d*='M1.101']",   # Специфічна іконка Send Instagram
                        "button[style*='cursor: pointer']",      # Активна кнопка
                    ]
                    
                    for send_selector in send_selectors:
                        try:
                            send_button = WebDriverWait(self.driver, 2).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, send_selector))
                            )
                            if send_button.is_displayed():
                                send_button.click()
                                send_button_found = True
                                self.logger.info("📤 Натиснуто кнопку Send (глобальний пошук)")
                                break
                        except:
                            continue
                
                # Якщо кнопка Send не знайдена, шукаємо наступний елемент після поля вводу
                if not send_button_found:
                    try:
                        # Шукаємо наступний сусідній елемент
                        next_sibling = reply_input.find_element(By.XPATH, "./following-sibling::*[1]")
                        if next_sibling.tag_name in ['button', 'div'] and next_sibling.is_displayed():
                            next_sibling.click()
                            send_button_found = True
                            self.logger.info("📤 Натиснуто сусідній елемент (кнопка Send)")
                    except:
                        pass
                
                # Останній варіант - Ctrl+Enter для відправки
                if not send_button_found:
                    reply_input.send_keys(Keys.CONTROL + Keys.RETURN)
                    self.logger.info("📤 Відправлено через Ctrl+Enter")
                
                story_replied = True
                self.logger.info(f"✅ Відправлено відповідь на сторіс: {message}")
                self.human_like_delay(1, 2)  # Коротка затримка після відправки
                break
                
            except Exception as e:
                self.logger.debug(f"Помилка при відправці відповіді через селектор {selector}: {e}")
                continue

        if not story_replied:
            self.logger.warning("⚠️ Не вдалося відправити відповідь на сторіс")

        # 6. Закриття сторіс
        close_selectors = [
            "svg[aria-label='Close']",
            "button[aria-label='Close']",
            "div[role='button'][tabindex='0']"
        ]
        
        for selector in close_selectors:
            try:
                close_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                close_button.click()
                self.logger.info("🚪 Сторіс закрита")
                break
            except:
                continue
        else:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.logger.info("🚪 Сторіс закрита через ESC")

        return story_liked or story_replied

     except Exception as e:
        self.logger.error(f"❌ Помилка при обробці сторіс: {str(e)}")
        return False
    

    def _close_story(self):
        """Універсальне закриття сторіс"""
        try:
            close_methods = [
                lambda: self.driver.find_element(By.CSS_SELECTOR, "svg[aria-label='Close']").click(),
                lambda: self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click(),
                lambda: ActionChains(self.driver).send_keys(Keys.ESCAPE).perform(),
                lambda: ActionChains(self.driver).move_by_offset(50, 50).click().perform()
            ]
            
            for method in close_methods:
                try:
                    method()
                    self.human_like_delay(1, 2)
                    self.logger.info("📱 Сторіс закрита")
                    return True
                except:
                    continue
                    
            self.logger.warning("⚠️ Не вдалося закрити сторіс стандартними методами")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Помилка при закритті сторіс: {e}")
            return False

    def send_direct_message(self, target_username, messages):
        """Fallback: якщо сторіс немає → Direct Messages → Next → повідомлення"""
        try:
            self.logger.info(f"💬 Відправка Direct Message для {target_username}")
            
            # Перехід до Direct Messages
            dm_url = "https://www.instagram.com/direct/new/"
            self.driver.get(dm_url)
            self.human_like_delay(3, 5)
            
            # Якщо direct/new не працює, пробуємо через inbox
            if "direct/new" not in self.driver.current_url:
                self.logger.info("💬 Перехід через inbox")
                dm_url = "https://www.instagram.com/direct/inbox/"
                self.driver.get(dm_url)
                self.human_like_delay(3, 5)
                
                # Пошук кнопки нового повідомлення
                new_message_selectors = [
                    "svg[aria-label='New message']",
                    "button[aria-label='New message']",
                    "//div[contains(text(), 'New message')]"
                ]
                
                for selector in new_message_selectors:
                    try:
                        if selector.startswith("//"):
                            new_message_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                        else:
                            new_message_button = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                            )
                        new_message_button.click()
                        self.human_like_delay(2, 3)
                        break
                    except:
                        continue
            
            # Пошук поля для введення імені користувача
            search_selectors = [
                "input[placeholder*='Search']",
                "input[name='queryBox']",
                "input[aria-label*='Search']",
                "div[contenteditable='true']"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not search_input:
                self.logger.error("❌ Не знайдено поле пошуку користувачів")
                return False
            
            # Введення імені користувача
            self.logger.info(f"🔍 Пошук користувача: {target_username}")
            search_input.clear()
            self.anti_detection.human_typing(search_input, target_username)
            self.human_like_delay(2, 3)
            
            # Пошук користувача в результатах
            user_found = False
            
            # Спочатку точний збіг
            try:
                exact_user = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[text()='{target_username}']"))
                )
                exact_user.click()
                user_found = True
                self.logger.info(f"✅ Знайдено користувача: {target_username}")
            except:
                # Частковий збіг
                try:
                    user_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[role='button'] span")
                    for element in user_elements:
                        if element.text and target_username.lower() in element.text.lower():
                            parent = element.find_element(By.XPATH, "./ancestor::div[@role='button'][1]")
                            parent.click()
                            user_found = True
                            self.logger.info(f"✅ Знайдено користувача: {element.text}")
                            break
                except:
                    pass
            
            if not user_found:
                self.logger.error(f"❌ Користувач {target_username} не знайдений")
                return False
            
            self.human_like_delay(2, 3)
            
            # Натискання "Next"
            try:
                next_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next')]")
                next_button.click()
                self.human_like_delay(2, 3)
            except:
                self.logger.warning("❌ Не знайдено кнопку Next")
                return False
            
            # Пошук поля для повідомлення
            message_selectors = [
                "textarea[placeholder*='Message']",
                "div[contenteditable='true'][aria-label*='Message']",
                "div[contenteditable='true']",
                "textarea[aria-label*='Message']"
            ]
            
            message_input = None
            for selector in message_selectors:
                try:
                    message_input = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not message_input:
                self.logger.error("❌ Не знайдено поле для введення повідомлення")
                return False
            
            # Введення повідомлення
            message = random.choice(messages)
            self.logger.info(f"💬 Введення повідомлення: {message}")
            
            message_input.clear()
            self.anti_detection.human_typing(message_input, message)
            self.human_like_delay(1, 2)
            
            # Відправка повідомлення
            try:
                message_input.send_keys(Keys.RETURN)
                self.logger.info(f"✅ Direct Message відправлено для {target_username}")
                return True
            except:
                try:
                    send_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                    send_button.click()
                    self.logger.info(f"✅ Direct Message відправлено для {target_username}")
                    return True
                except:
                    self.logger.error("❌ Не вдалося відправити повідомлення")
                    return False
                
        except Exception as e:
            self.logger.error(f"❌ Помилка при відправці Direct Message: {e}")
            return False
            
    def run_automation(self, target_username, messages):
        """Запуск автоматизації з оптимізованою логікою"""
        try:
            self.logger.info(f"🚀 Початок автоматизації для {target_username}")
            
            # Вхід в систему
            if not self.login():
                self.logger.error("❌ Помилка входу в систему")
                return False
                    
            success_count = 0
            total_actions = 3
            
            # 1. Лайк постів: профіль → пост1 → лайк → назад → пост2 → лайк → назад
            self.logger.info("📸 === ЕТАП 1: ЛАЙК ПОСТІВ ===")
            try:
                if self.like_recent_posts(target_username, 2):
                    success_count += 1
                    self.logger.info("✅ Лайки постів виконано успішно")
                else:
                    self.logger.warning("❌ Лайки постів не виконано")
            except Exception as e:
                self.logger.error(f"❌ Помилка при лайку постів: {e}")
                
            # Затримка між етапами
            self.logger.info("⏳ Затримка між етапами...")
            self.human_like_delay(15, 25)
            
            # 2. Сторіс: на профілі натиснути аватарку → лайк → відповідь
            self.logger.info("📱 === ЕТАП 2: СТОРІС (ЛАЙК + ВІДПОВІДЬ) ===")
            story_success = False
            try:
                story_success = self.process_story(target_username, messages)
                if story_success:
                    success_count += 1  # Враховуємо тільки як одну успішну дію
                    self.logger.info("✅ Сторіс успішно оброблена")
                else:
                    self.logger.warning("❌ Сторіс не оброблена або не знайдена")
            except Exception as e:
                self.logger.error(f"❌ Помилка при роботі зі сторіс: {e}")
                
            # 3. Fallback: якщо сторіс не спрацювала → Direct Messages
            if not story_success:
                self.logger.info("💬 === ЕТАП 3: FALLBACK - DIRECT MESSAGE ===")
                self.human_like_delay(10, 15)
                
                try:
                    if self.send_direct_message(target_username, messages):
                        success_count += 1
                        self.logger.info("✅ Direct Message відправлено успішно")
                    else:
                        self.logger.warning("❌ Direct Message не відправлено")
                except Exception as e:
                    self.logger.error(f"❌ Помилка при відправці Direct Message: {e}")
            
            # Підсумок роботи
            success_rate = (success_count / total_actions) * 100
            
            self.logger.info("=" * 50)
            self.logger.info("📊 === ПІДСУМОК АВТОМАТИЗАЦІЇ ===")
            
            if success_count == total_actions:
                self.logger.info(f"🎉 Автоматизація повністю завершена: {success_count}/{total_actions} дій виконано ({success_rate:.1f}%)")
            elif success_count > 0:
                self.logger.info(f"⚠️ Автоматизація частково завершена: {success_count}/{total_actions} дій виконано ({success_rate:.1f}%)")
            else:
                self.logger.error(f"❌ Автоматизація не виконана: {success_count}/{total_actions} дій виконано ({success_rate:.1f}%)")
            
            # Детальна статистика
            actions_status = {
                "📸 Лайк постів": "✅" if success_count >= 1 else "❌",
                "📱 Сторіс": "✅" if story_success else "❌",
                "💬 Повідомлення": "✅" if not story_success and success_count >= 2 else "❌"
            }
            
            self.logger.info("📋 Детальна статистика:")
            for action, status in actions_status.items():
                self.logger.info(f"  {status} {action}")
            
            self.logger.info("=" * 50)
            
            return success_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Критична помилка при автоматизації: {e}")
            return False
        finally:
            # Завершальні дії
            try:
                self.logger.info("🔚 Завершення сесії...")
                self.human_like_delay(2, 5)
            except:
                pass
            
    def close(self):
        """Закриття бота"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    def __del__(self):
        self.close()


# Приклад використання
if __name__ == "__main__":
    # Налаштування для роботи
    USERNAME = "your_username"
    PASSWORD = "your_password"
    TARGET_USER = "target_username"
    MESSAGES = [
        "Привіт! Як справи? 😊",
        "Гарний пост! 👍",
        "Дякую за цікавий контент! 🙏",
        "Супер фото! 📸",
        "Вітаю! 🎉",
        "Класно! 🔥",
        "Дуже круто! ⭐",
        "Чудово! 💫"
    ]
    
    # Створення та запуск бота
    bot = InstagramBot(USERNAME, PASSWORD)
    
    try:
        print("🚀 Запуск Instagram Bot з оптимізованою логікою")
        print("=" * 50)
        print("📋 План дій:")
        print("1. 📸 Лайк постів: профіль → пост1 → лайк → назад → пост2 → лайк → назад")
        print("2. 📱 Сторіс: на профілі натиснути аватарку → лайк → відповідь")
        print("3. 💬 Fallback: якщо сторіс немає → Direct Messages → Next → повідомлення")
        print("=" * 50)
        
        success = bot.run_automation(TARGET_USER, MESSAGES)
        
        print("=" * 50)
        if success:
            print("🎉 Автоматизація завершена успішно!")
        else:
            print("❌ Автоматизація не була виконана повністю")
        print("=" * 50)
            
    except KeyboardInterrupt:
        print("\n⚠️ Автоматизацію перервано користувачем")
        
    except Exception as e:
        print(f"❌ Помилка при запуску бота: {e}")
        
    finally:
        bot.close()
        print("🔚 Бот закрито")