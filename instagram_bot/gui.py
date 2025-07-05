import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import json
import os
from datetime import datetime
import logging
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from instagram_bot import InstagramBot
from config import Config
from utils import DatabaseManager, MessageManager, SecurityManager

class ModernStyle:
    """Сучасний стиль для інтерфейсу"""
    
    # Темна тема
    DARK_THEME = {
        'bg': '#1a1a1a',
        'fg': '#ffffff',
        'select_bg': '#3d3d3d',
        'select_fg': '#ffffff',
        'entry_bg': '#2d2d2d',
        'entry_fg': '#ffffff',
        'button_bg': '#4a4a4a',
        'button_fg': '#ffffff',
        'button_active': '#5a5a5a',
        'accent': '#00d4aa',
        'success': '#00ff88',
        'warning': '#ffaa00',
        'error': '#ff4444',
        'info': '#44aaff'
    }
    
    # Світла тема
    LIGHT_THEME = {
        'bg': '#ffffff',
        'fg': '#000000',
        'select_bg': '#0078d4',
        'select_fg': '#ffffff',
        'entry_bg': '#f0f0f0',
        'entry_fg': '#000000',
        'button_bg': '#e0e0e0',
        'button_fg': '#000000',
        'button_active': '#d0d0d0',
        'accent': '#0078d4',
        'success': '#00aa00',
        'warning': '#ff8800',
        'error': '#cc0000',
        'info': '#0066cc'
    }
    
    @classmethod
    def get_theme(cls, theme_name='dark'):
        return cls.DARK_THEME if theme_name == 'dark' else cls.LIGHT_THEME

class InstagramBotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Instagram Bot - Мобільна автоматизація")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # Налаштування теми
        self.theme = ModernStyle.get_theme(Config.GUI.get('theme', 'dark'))
        self.setup_style()
        
        # Менеджери
        self.db = DatabaseManager()
        self.message_manager = MessageManager()
        self.security_manager = SecurityManager()
        
        # Змінні
        self.bots = {}
        self.running_bots = set()
        self.accounts = []
        self.current_account = None
        
        # Створення інтерфейсу
        self.create_widgets()
        self.load_accounts()
        
        # Налаштування логування
        self.setup_logging()
        
        # Автозбереження
        if Config.GUI.get('auto_save', True):
            self.auto_save()
            
    def setup_style(self):
        """Налаштування стилю"""
        style = ttk.Style()
        
        # Налаштування теми
        style.theme_use('clam')
        
        # Конфігурація стилів
        style.configure('TLabel', 
                       background=self.theme['bg'],
                       foreground=self.theme['fg'])
        
        style.configure('TFrame',
                       background=self.theme['bg'])
                       
        style.configure('TButton',
                       background=self.theme['button_bg'],
                       foreground=self.theme['button_fg'],
                       borderwidth=1,
                       focuscolor='none')
                       
        style.map('TButton',
                 background=[('active', self.theme['button_active']),
                           ('pressed', self.theme['accent'])])
                           
        style.configure('TEntry',
                       background=self.theme['entry_bg'],
                       foreground=self.theme['entry_fg'],
                       borderwidth=1,
                       insertcolor=self.theme['fg'])
                       
        style.configure('TCombobox',
                       background=self.theme['entry_bg'],
                       foreground=self.theme['entry_fg'],
                       borderwidth=1)
                       
        style.configure('Treeview',
                       background=self.theme['bg'],
                       foreground=self.theme['fg'],
                       fieldbackground=self.theme['entry_bg'])
                       
        style.configure('Treeview.Heading',
                       background=self.theme['button_bg'],
                       foreground=self.theme['button_fg'])
                       
        # Кастомні стили
        style.configure('Accent.TButton',
                       background=self.theme['accent'],
                       foreground='white')
                       
        style.configure('Success.TButton',
                       background=self.theme['success'],
                       foreground='white')
                       
        style.configure('Warning.TButton',
                       background=self.theme['warning'],
                       foreground='white')
                       
        style.configure('Error.TButton',
                       background=self.theme['error'],
                       foreground='white')
        
        # Налаштування кореневого вікна
        self.root.configure(bg=self.theme['bg'])
        
    def create_widgets(self):
        """Створення віджетів"""
        # Головне меню
        self.create_menu()
        
        # Головний контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Панель навігації
        self.create_navigation(main_frame)
        
        # Notebook для вкладок
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Створення вкладок
        self.create_accounts_tab()
        self.create_automation_tab()
        self.create_messages_tab()
        self.create_statistics_tab()
        self.create_settings_tab()
        self.create_logs_tab()
        
    def create_menu(self):
        """Створення меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Імпорт акаунтів", command=self.import_accounts)
        file_menu.add_command(label="Експорт акаунтів", command=self.export_accounts)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.root.quit)
        
        # Інструменти
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Інструменти", menu=tools_menu)
        tools_menu.add_command(label="Перевірка проксі", command=self.check_proxies)
        tools_menu.add_command(label="Очистка логів", command=self.clear_logs)
        tools_menu.add_command(label="Резервна копія", command=self.create_backup)
        
        # Допомога
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Допомога", menu=help_menu)
        help_menu.add_command(label="Інструкція", command=self.show_help)
        help_menu.add_command(label="Про програму", command=self.show_about)
        
    def create_navigation(self, parent):
        """Створення панелі навігації"""
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Заголовок
        title_label = ttk.Label(nav_frame, text="🤖 Instagram Bot", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Статус
        self.status_label = ttk.Label(nav_frame, text="Готовий до роботи", 
                                     foreground=self.theme['success'])
        self.status_label.pack(side=tk.RIGHT)
        
        # Індикатор активності
        self.activity_var = tk.StringVar(value="●")
        self.activity_label = ttk.Label(nav_frame, textvariable=self.activity_var,
                                       foreground=self.theme['success'],
                                       font=('Arial', 12))
        self.activity_label.pack(side=tk.RIGHT, padx=(0, 10))
        
    def create_accounts_tab(self):
        """Вкладка акаунтів"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="👥 Акаунти")
        
        # Панель інструментів
        toolbar_frame = ttk.Frame(tab_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(toolbar_frame, text="➕ Додати акаунт",
                  command=self.add_account_dialog,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="✏️ Редагувати",
                  command=self.edit_account_dialog).pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="🗑️ Видалити",
                  command=self.delete_account,
                  style='Error.TButton').pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="🔄 Оновити",
                  command=self.refresh_accounts).pack(side=tk.LEFT, padx=(0, 5))
                  
        # Пошук
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side=tk.RIGHT)
        
        ttk.Label(search_frame, text="🔍 Пошук:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_accounts)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        
        # Таблиця акаунтів
        table_frame = ttk.Frame(tab_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Створення Treeview
        columns = ('username', 'status', 'proxy', 'last_activity', 'actions_today')
        self.accounts_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        # Налаштування колонок
        self.accounts_tree.heading('username', text='Ім\'я користувача')
        self.accounts_tree.heading('status', text='Статус')
        self.accounts_tree.heading('proxy', text='Проксі')
        self.accounts_tree.heading('last_activity', text='Остання активність')
        self.accounts_tree.heading('actions_today', text='Дії сьогодні')
        
        self.accounts_tree.column('username', width=150)
        self.accounts_tree.column('status', width=100)
        self.accounts_tree.column('proxy', width=150)
        self.accounts_tree.column('last_activity', width=150)
        self.accounts_tree.column('actions_today', width=100)
        
        # Скролбар
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.accounts_tree.yview)
        self.accounts_tree.configure(yscrollcommand=scrollbar.set)
        
        # Розміщення
        self.accounts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Контекстне меню
        self.create_context_menu()
        
    def create_automation_tab(self):
        """Вкладка автоматизації"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🤖 Автоматизація")
        
        # Основний контейнер
        main_container = ttk.Frame(tab_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Ліва панель - налаштування
        left_frame = ttk.LabelFrame(main_container, text="⚙️ Налаштування автоматизації", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Вибір акаунта
        ttk.Label(left_frame, text="Акаунт:").pack(anchor=tk.W)
        self.account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(left_frame, textvariable=self.account_var, state='readonly')
        self.account_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Цільовий користувач
        ttk.Label(left_frame, text="Цільовий користувач:").pack(anchor=tk.W)
        self.target_var = tk.StringVar()
        target_entry = ttk.Entry(left_frame, textvariable=self.target_var)
        target_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Дії
        actions_frame = ttk.LabelFrame(left_frame, text="Дії", padding=5)
        actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.like_posts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(actions_frame, text="Лайк останніх постів", 
                       variable=self.like_posts_var).pack(anchor=tk.W)
                       
        self.like_stories_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(actions_frame, text="Лайк сторіс", 
                       variable=self.like_stories_var).pack(anchor=tk.W)
                       
        self.reply_stories_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(actions_frame, text="Відповідь на сторіс", 
                       variable=self.reply_stories_var).pack(anchor=tk.W)
        
        # Кількість лайків
        likes_frame = ttk.Frame(left_frame)
        likes_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(likes_frame, text="Кількість лайків постів:").pack(anchor=tk.W)
        self.likes_count_var = tk.IntVar(value=2)
        likes_spin = ttk.Spinbox(likes_frame, from_=1, to=10, textvariable=self.likes_count_var, width=10)
        likes_spin.pack(anchor=tk.W)
        
        # Затримки
        delay_frame = ttk.LabelFrame(left_frame, text="Затримки (секунди)", padding=5)
        delay_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(delay_frame, text="Мін. затримка:").pack(anchor=tk.W)
        self.min_delay_var = tk.IntVar(value=Config.MIN_DELAY)
        min_delay_spin = ttk.Spinbox(delay_frame, from_=1, to=60, textvariable=self.min_delay_var, width=10)
        min_delay_spin.pack(anchor=tk.W, pady=(0, 5))
        
        ttk.Label(delay_frame, text="Макс. затримка:").pack(anchor=tk.W)
        self.max_delay_var = tk.IntVar(value=Config.MAX_DELAY)
        max_delay_spin = ttk.Spinbox(delay_frame, from_=1, to=120, textvariable=self.max_delay_var, width=10)
        max_delay_spin.pack(anchor=tk.W)
        
        # Кнопки управління
        control_frame = ttk.Frame(left_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = ttk.Button(control_frame, text="▶️ Запустити", 
                                      command=self.start_automation,
                                      style='Success.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Зупинити", 
                                     command=self.stop_automation,
                                     style='Error.TButton', state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="⏸️ Пауза", 
                  command=self.pause_automation).pack(side=tk.LEFT)
        
        # Права панель - моніторинг
        right_frame = ttk.LabelFrame(main_container, text="📊 Моніторинг", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Прогрес
        progress_frame = ttk.Frame(right_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(progress_frame, text="Прогрес:").pack(anchor=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Статистика
        stats_frame = ttk.LabelFrame(right_frame, text="Статистика", padding=5)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_text = tk.Text(stats_frame, height=8, width=40, 
                                 bg=self.theme['entry_bg'], fg=self.theme['entry_fg'])
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Логи реального часу
        logs_frame = ttk.LabelFrame(right_frame, text="Логи", padding=5)
        logs_frame.pack(fill=tk.BOTH, expand=True)
        
        self.live_logs = scrolledtext.ScrolledText(logs_frame, height=10, width=40,
                                                  bg=self.theme['entry_bg'], fg=self.theme['entry_fg'])
        self.live_logs.pack(fill=tk.BOTH, expand=True)
        
    def create_messages_tab(self):
        """Вкладка повідомлень"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="💬 Повідомлення")
        
        # Панель інструментів
        toolbar_frame = ttk.Frame(tab_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(toolbar_frame, text="➕ Додати",
                  command=self.add_message_dialog,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="✏️ Редагувати",
                  command=self.edit_message_dialog).pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="🗑️ Видалити",
                  command=self.delete_message,
                  style='Error.TButton').pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="📁 Імпорт з файлу",
                  command=self.import_messages).pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="💾 Експорт в файл",
                  command=self.export_messages).pack(side=tk.LEFT)
        
        # Основний контейнер
        main_container = ttk.Frame(tab_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Список повідомлень
        left_frame = ttk.LabelFrame(main_container, text="📝 Список повідомлень", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Listbox з повідомленнями
        self.messages_listbox = tk.Listbox(left_frame, height=15, 
                                          bg=self.theme['entry_bg'], fg=self.theme['entry_fg'],
                                          selectbackground=self.theme['select_bg'],
                                          selectforeground=self.theme['select_fg'])
        self.messages_listbox.pack(fill=tk.BOTH, expand=True)
        self.messages_listbox.bind('<Double-Button-1>', self.edit_message_dialog)
        
        # Права панель - попередній перегляд
        right_frame = ttk.LabelFrame(main_container, text="👁️ Попередній перегляд", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Текст повідомлення
        self.message_preview = tk.Text(right_frame, height=5, width=30, wrap=tk.WORD,
                                      bg=self.theme['entry_bg'], fg=self.theme['entry_fg'])
        self.message_preview.pack(fill=tk.X, pady=(0, 10))
        
        # Статистика повідомлень
        stats_text = tk.Text(right_frame, height=10, width=30,
                            bg=self.theme['entry_bg'], fg=self.theme['entry_fg'])
        stats_text.pack(fill=tk.BOTH, expand=True)
        
        # Оновлення списку повідомлень
        self.update_messages_list()
        
    def create_statistics_tab(self):
        """Вкладка статистики"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📈 Статистика")
        
        # Панель фільтрів
        filter_frame = ttk.LabelFrame(tab_frame, text="🔍 Фільтри", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Період
        period_frame = ttk.Frame(filter_frame)
        period_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(period_frame, text="Період:").pack(anchor=tk.W)
        self.period_var = tk.StringVar(value="7 днів")
        period_combo = ttk.Combobox(period_frame, textvariable=self.period_var,
                                   values=["1 день", "7 днів", "30 днів", "Весь час"],
                                   state='readonly', width=15)
        period_combo.pack()
        period_combo.bind('<<ComboboxSelected>>', self.update_statistics)
        
        # Акаунт
        account_frame = ttk.Frame(filter_frame)
        account_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(account_frame, text="Акаунт:").pack(anchor=tk.W)
        self.stats_account_var = tk.StringVar(value="Всі")
        stats_account_combo = ttk.Combobox(account_frame, textvariable=self.stats_account_var,
                                          state='readonly', width=20)
        stats_account_combo.pack()
        stats_account_combo.bind('<<ComboboxSelected>>', self.update_statistics)
        
        # Кнопка оновлення
        ttk.Button(filter_frame, text="🔄 Оновити", 
                  command=self.update_statistics,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(20, 0))
        
        # Контейнер графіків
        charts_frame = ttk.Frame(tab_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Створення matplotlib графіків
        self.create_charts(charts_frame)
        
    def create_settings_tab(self):
        """Вкладка налаштувань"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="⚙️ Налаштування")
        
        # Notebook для підкатегорій налаштувань
        settings_notebook = ttk.Notebook(tab_frame)
        settings_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Загальні налаштування
        self.create_general_settings(settings_notebook)
        
        # Налаштування безпеки
        self.create_security_settings(settings_notebook)
        
        # Налаштування проксі
        self.create_proxy_settings(settings_notebook)
        
        # Налаштування капчі
        self.create_captcha_settings(settings_notebook)
        
    def create_logs_tab(self):
        """Вкладка логів"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📋 Логи")
        
        # Панель інструментів
        toolbar_frame = ttk.Frame(tab_frame)
        toolbar_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(toolbar_frame, text="🔄 Оновити",
                  command=self.refresh_logs,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="🗑️ Очистити",
                  command=self.clear_logs,
                  style='Warning.TButton').pack(side=tk.LEFT, padx=(0, 5))
                  
        ttk.Button(toolbar_frame, text="💾 Експорт",
                  command=self.export_logs).pack(side=tk.LEFT, padx=(0, 5))
        
        # Фільтри логів
        filter_frame = ttk.Frame(toolbar_frame)
        filter_frame.pack(side=tk.RIGHT)
        
        ttk.Label(filter_frame, text="Рівень:").pack(side=tk.LEFT, padx=(0, 5))
        self.log_level_var = tk.StringVar(value="Всі")
        log_level_combo = ttk.Combobox(filter_frame, textvariable=self.log_level_var,
                                      values=["Всі", "INFO", "WARNING", "ERROR"],
                                      state='readonly', width=10)
        log_level_combo.pack(side=tk.LEFT, padx=(0, 10))
        log_level_combo.bind('<<ComboboxSelected>>', self.filter_logs)
        
        ttk.Label(filter_frame, text="Пошук:").pack(side=tk.LEFT, padx=(0, 5))
        self.log_search_var = tk.StringVar()
        self.log_search_var.trace('w', self.filter_logs)
        search_entry = ttk.Entry(filter_frame, textvariable=self.log_search_var, width=20)
        search_entry.pack(side=tk.LEFT)
        
        # Текстове поле для логів
        logs_frame = ttk.Frame(tab_frame)
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, 
                                                  bg=self.theme['entry_bg'], 
                                                  fg=self.theme['entry_fg'],
                                                  font=('Consolas', 10))
        self.logs_text.pack(fill=tk.BOTH, expand=True)
        
        # Автооновлення логів
        self.auto_refresh_logs()
        
    def create_general_settings(self, parent):
        """Загальні налаштування"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="🔧 Загальні")
        
        # Створення скролованого контейнера
        canvas = tk.Canvas(frame, bg=self.theme['bg'])
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Інтерфейс
        ui_frame = ttk.LabelFrame(scrollable_frame, text="Інтерфейс", padding=10)
        ui_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Тема
        theme_frame = ttk.Frame(ui_frame)
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(theme_frame, text="Тема:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=Config.GUI.get('theme', 'dark'))
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                  values=["dark", "light"], state='readonly', width=15)
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        theme_combo.bind('<<ComboboxSelected>>', self.change_theme)
        
        # Мова
        lang_frame = ttk.Frame(ui_frame)
        lang_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(lang_frame, text="Мова:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=Config.GUI.get('language', 'uk'))
        lang_combo = ttk.Combobox(lang_frame, textvariable=self.lang_var,
                                 values=["uk", "en", "ru"], state='readonly', width=15)
        lang_combo.pack(side=tk.LEFT, padx=(10, 0))
        
        # Автозбереження
        self.auto_save_var = tk.BooleanVar(value=Config.GUI.get('auto_save', True))
        ttk.Checkbutton(ui_frame, text="Автозбереження налаштувань", 
                       variable=self.auto_save_var).pack(anchor=tk.W)
        
        # Поведінка бота
        bot_frame = ttk.LabelFrame(scrollable_frame, text="Поведінка бота", padding=10)
        bot_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Headless режим
        self.headless_var = tk.BooleanVar(value=Config.HEADLESS)
        ttk.Checkbutton(bot_frame, text="Headless режим (без вікна браузера)", 
                       variable=self.headless_var).pack(anchor=tk.W, pady=(0, 5))
        
        # Таймаут
        timeout_frame = ttk.Frame(bot_frame)
        timeout_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(timeout_frame, text="Таймаут (секунди):").pack(side=tk.LEFT)
        self.timeout_var = tk.IntVar(value=Config.TIMEOUT)
        timeout_spin = ttk.Spinbox(timeout_frame, from_=5, to=60, textvariable=self.timeout_var, width=10)
        timeout_spin.pack(side=tk.LEFT, padx=(10, 0))
        
        # Кнопка збереження
        save_frame = ttk.Frame(scrollable_frame)
        save_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(save_frame, text="💾 Зберегти налаштування", 
                  command=self.save_settings,
                  style='Success.TButton').pack()
        
        # Розміщення скролованого контейнера
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def add_account_dialog(self):
        """Діалог додавання акаунта"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Додати акаунт")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.configure(bg=self.theme['bg'])
        
        # Центрування діалогу
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Основний фрейм
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Ім'я користувача
        ttk.Label(main_frame, text="Ім'я користувача:").pack(anchor=tk.W, pady=(0, 5))
        username_var = tk.StringVar()
        username_entry = ttk.Entry(main_frame, textvariable=username_var, width=40)
        username_entry.pack(fill=tk.X, pady=(0, 10))
        username_entry.focus()
        
        # Пароль
        ttk.Label(main_frame, text="Пароль:").pack(anchor=tk.W, pady=(0, 5))
        password_var = tk.StringVar()
        password_entry = ttk.Entry(main_frame, textvariable=password_var, show='*', width=40)
        password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Проксі (опційно)
        ttk.Label(main_frame, text="Проксі (опційно):").pack(anchor=tk.W, pady=(0, 5))
        proxy_var = tk.StringVar()
        proxy_entry = ttk.Entry(main_frame, textvariable=proxy_var, width=40)
        proxy_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Підказка для проксі
        hint_label = ttk.Label(main_frame, text="Формат: ip:port:username:password", 
                              foreground=self.theme['info'])
        hint_label.pack(anchor=tk.W, pady=(0, 20))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_account():
            if not username_var.get() or not password_var.get():
                messagebox.showerror("Помилка", "Заповніть всі обов'язкові поля!")
                return
                
            if self.db.add_account(username_var.get(), password_var.get(), proxy_var.get() or None):
                messagebox.showinfo("Успіх", "Акаунт успішно додано!")
                dialog.destroy()
                self.load_accounts()
            else:
                messagebox.showerror("Помилка", "Не вдалося додати акаунт!")
        
        ttk.Button(button_frame, text="💾 Зберегти", command=save_account,
                  style='Success.TButton').pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="❌ Скасувати", 
                  command=dialog.destroy).pack(side=tk.RIGHT)
        
    def load_accounts(self):
        """Завантаження акаунтів"""
        # Очищення таблиці
        for item in self.accounts_tree.get_children():
            self.accounts_tree.delete(item)
            
        # Завантаження з БД
        accounts = self.db.get_all_accounts()
        self.accounts = accounts
        
        for account in accounts:
            username = account[1]
            status = account[4]
            proxy = account[3] or "Немає"
            last_activity = account[5] or "Ніколи"
            
            # Отримання дій за сьогодні
            today_actions = self.db.get_today_actions(username)
            actions_count = sum(today_actions.values())
            
            # Додавання в таблицю
            self.accounts_tree.insert('', tk.END, values=(
                username, status, proxy, last_activity, actions_count
            ))
            
        # Оновлення комбобоксів
        usernames = [acc[1] for acc in accounts]
        self.account_combo['values'] = usernames
        
    def start_automation(self):
        """Запуск автоматизації"""
        if not self.account_var.get():
            messagebox.showerror("Помилка", "Виберіть акаунт!")
            return
            
        if not self.target_var.get():
            messagebox.showerror("Помилка", "Вкажіть цільового користувача!")
            return
            
        # Отримання даних акаунта
        account = self.db.get_account(self.account_var.get())
        if not account:
            messagebox.showerror("Помилка", "Акаунт не знайдено!")
            return
            
        # Створення і запуск бота в окремому потоці
        def run_bot():
            try:
                self.update_status("Запуск автоматизації...")
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                
                # Створення бота
                bot = InstagramBot(account[1], account[2], account[3])
                self.bots[account[1]] = bot
                self.running_bots.add(account[1])
                
                # Отримання повідомлень
                messages = self.message_manager.messages
                
                # Запуск автоматизації
                success = bot.run_automation(self.target_var.get(), messages)
                
                if success:
                    self.update_status("Автоматизація завершена успішно!")
                    self.log_message(f"✅ Автоматизація для {account[1]} завершена успішно")
                else:
                    self.update_status("Автоматизація завершена з помилками!")
                    self.log_message(f"❌ Автоматизація для {account[1]} завершена з помилками")
                    
            except Exception as e:
                self.update_status(f"Помилка: {str(e)}")
                self.log_message(f"❌ Помилка автоматизації: {str(e)}")
                
            finally:
                self.start_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)
                self.running_bots.discard(account[1])
                
        # Запуск в окремому потоці
        thread = threading.Thread(target=run_bot)
        thread.daemon = True
        thread.start()
        
    def stop_automation(self):
        """Зупинка автоматизації"""
        for username in list(self.running_bots):
            if username in self.bots:
                self.bots[username].close()
                del self.bots[username]
                
        self.running_bots.clear()
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("Автоматизація зупинена")
        
    def update_status(self, message):
        """Оновлення статусу"""
        self.status_label.config(text=message)
        
    def log_message(self, message):
        """Додавання повідомлення в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.live_logs.insert(tk.END, log_entry)
        self.live_logs.see(tk.END)
        
        # Обмеження кількості рядків
        lines = self.live_logs.get(1.0, tk.END).split('\n')
        if len(lines) > 1000:
            self.live_logs.delete(1.0, f"{len(lines)-1000}.0")
            
    def update_messages_list(self):
        """Оновлення списку повідомлень"""
        self.messages_listbox.delete(0, tk.END)
        for message in self.message_manager.messages:
            self.messages_listbox.insert(tk.END, message)
            
    def add_message_dialog(self):
        """Діалог додавання повідомлення"""
        message = tk.simpledialog.askstring("Додати повідомлення", 
                                           "Введіть текст повідомлення:")
        if message:
            self.message_manager.add_message(message)
            self.update_messages_list()
            
    def setup_logging(self):
        """Налаштування логування для GUI"""
        class GUILogHandler(logging.Handler):
            def __init__(self, gui):
                super().__init__()
                self.gui = gui
                
            def emit(self, record):
                log_entry = self.format(record)
                self.gui.log_message(log_entry)
                
        # Додавання обробника
        gui_handler = GUILogHandler(self)
        gui_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        gui_handler.setFormatter(formatter)
        
        logging.getLogger().addHandler(gui_handler)
        
    def auto_save(self):
        """Автозбереження налаштувань"""
        if self.auto_save_var.get():
            self.save_settings()
            
        # Повторити через 5 хвилин
        self.root.after(300000, self.auto_save)
        
    def save_settings(self):
        """Збереження налаштувань"""
        try:
            # Оновлення конфігурації
            Config.HEADLESS = self.headless_var.get()
            Config.TIMEOUT = self.timeout_var.get()
            Config.GUI['theme'] = self.theme_var.get()
            Config.GUI['language'] = self.lang_var.get()
            Config.GUI['auto_save'] = self.auto_save_var.get()
            
            # Збереження в файл
            Config.save_config()
            
            messagebox.showinfo("Успіх", "Налаштування збережено!")
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося зберегти налаштування: {e}")
            
    def create_context_menu(self):
        """Створення контекстного меню для таблиці акаунтів"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Редагувати", command=self.edit_account_dialog)
        self.context_menu.add_command(label="🗑️ Видалити", command=self.delete_account)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Перевірити статус", command=self.check_account_status)
        self.context_menu.add_command(label="📊 Статистика", command=self.show_account_stats)
        
        def show_context_menu(event):
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()
                
        self.accounts_tree.bind("<Button-3>", show_context_menu)
        
    def run(self):
        """Запуск GUI"""
        self.root.mainloop()
        
    def on_closing(self):
        """Обробник закриття програми"""
        # Зупинка всіх ботів
        self.stop_automation()
        
        # Збереження налаштувань
        if self.auto_save_var.get():
            self.save_settings()
            
        self.root.destroy()

# Додаткові методи (скорочена версія для економії місця)
    def edit_account_dialog(self): pass
    def delete_account(self): pass
    def refresh_accounts(self): pass
    def filter_accounts(self, *args): pass
    def pause_automation(self): pass
    def edit_message_dialog(self): pass
    def delete_message(self): pass
    def import_messages(self): pass
    def export_messages(self): pass
    def create_charts(self, parent): pass
    def update_statistics(self, *args): pass
    def create_security_settings(self, parent): pass
    def create_proxy_settings(self, parent): pass
    def create_captcha_settings(self, parent): pass
    def refresh_logs(self): pass
    def clear_logs(self): pass
    def export_logs(self): pass
    def filter_logs(self, *args): pass
    def auto_refresh_logs(self): pass
    def change_theme(self, *args): pass
    def import_accounts(self): pass
    def export_accounts(self): pass
    def check_proxies(self): pass
    def create_backup(self): pass
    def show_help(self): pass
    def show_about(self): pass
    def check_account_status(self): pass
    def show_account_stats(self): pass

if __name__ == "__main__":
    app = InstagramBotGUI()
    app.run()