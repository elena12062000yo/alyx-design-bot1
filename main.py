#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram бот @alyx_design_bot с улучшенным admin функционалом
"""

import logging
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from typing import Dict, List

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = "8307209669:AAFl5JKEBUPkJ8akr01RfXKwvLTNEoQPLqQ"
OWNER_ID = 1014948227
WEBSITE_URL = "https://www.alyxbabysitter.ru"

# База данных в памяти
class Database:
    def __init__(self):
        self.users: Dict[int, dict] = {}
        self.orders: List[dict] = []
        self.first_time_users: List[int] = []  # Для отслеживания новых пользователей
    
    def add_user(self, user_id: int, user_data: dict):
        """Добавить пользователя"""
        is_new_user = user_id not in self.users
        
        self.users[user_id] = {
            'id': user_id,
            'first_name': user_data.get('first_name', ''),
            'username': user_data.get('username', ''),
            'joined_at': datetime.now(),
            'last_seen': datetime.now(),
            'is_new': is_new_user
        }
        
        if is_new_user:
            self.first_time_users.append(user_id)
        
        return is_new_user
    
    def update_last_seen(self, user_id: int):
        """Обновить время последнего визита"""
        if user_id in self.users:
            self.users[user_id]['last_seen'] = datetime.now()
    
    def get_stats(self):
        """Получить статистику"""
        total_users = len(self.users)
        new_users_today = len([u for u in self.users.values() 
                              if u['joined_at'].date() == datetime.now().date()])
        return {
            'total_users': total_users,
            'new_users_today': new_users_today,
            'orders': len(self.orders)
        }

# Инициализация базы данных
db = Database()

# Сообщения бота
MESSAGES = {
    'welcome_new_user': """🎉 <b>Добро пожаловать!</b>

Я бот AI-дизайнера <b>Alyx Babysitter</b>!

Здесь вы можете:
• Посмотреть портфолио
• Узнать о услугах и ценах  
• Оформить заказ
• Связаться со мной

Нажмите кнопку <b>"🚀 Start"</b> чтобы начать!""",

    'start': """🎨 <b>AI Designer Alyx Babysitter</b>

Создаю уникальные визуалы с помощью ИИ:
• Цифровые двойники артистов
• AI-фотосессии и портреты
• Кинематографичные сниппеты
• Дизайн обложек релизов

Выберите нужный раздел ниже 👇""",

    'portfolio': """🎨 <b>Портфолио</b>

Посмотрите мои работы на сайте или выберите категорию:

• AI-портреты в стиле Y2K/трэп
• Реалистичные цифровые двойники артистов
• AI-фотосессии для брендов
• Кинематографичные видео-сниппеты
• Обложки релизов и дизайн

🌐 Полное портфолио: www.alyxbabysitter.ru""",

    'services': """💎 <b>Услуги и цены</b>

🤖 <b>Цифровой двойник</b>
От 15,000₽ | 2-3 недели
Создание AI-модели по вашим фото

📸 <b>AI-фотосессия</b>  
От 5,000₽ | 3-5 дней
Пакет от 10 фотографий

🎬 <b>AI-сниппет</b>
От 3,000₽ | 2-3 дня
Короткий ролик 9-15 секунд

🎨 <b>Дизайн обложки</b>
От 2,000₽ | 1-2 дня
Обложка для релиза/проекта

💼 <b>Коммерческая съемка</b>
От 8,000₽ | 5-7 дней
Рекламные визуалы для бизнеса

📞 Для заказа нажмите "Оформить заказ" ниже""",

    'contact': """📞 <b>Контакты</b>

Связаться со мной можно несколькими способами:

💬 <b>Telegram:</b> @alyx_babysitter
🌐 <b>Сайт:</b> www.alyxbabysitter.ru
📧 <b>Email по запросу</b>

Обычно отвечаю в течение 2-3 часов ⚡""",

    'about': """ℹ️ <b>О дизайнере</b>

👨‍🎨 <b>Alyx Babysitter</b>
AI-дизайнер и визуальный артист

🎯 <b>Специализация:</b>
• Создание цифровых двойников
• AI-генерация изображений
• Обучение нейросетей
• Визуальный дизайн

💼 <b>Опыт работы:</b>
• 100+ проектов выполнено
• Работа с артистами и лейблами
• Коммерческие проекты для брендов"""
}

# Клавиатуры
def get_welcome_keyboard():
    """Клавиатура для нового пользователя"""
    keyboard = [
        [InlineKeyboardButton("🚀 Start", callback_data="start_bot")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_main_keyboard():
    """Основная клавиатура"""
    keyboard = [
        [InlineKeyboardButton("🎨 Портфолио", callback_data="portfolio"),
         InlineKeyboardButton("💎 Услуги", callback_data="services")],
        [InlineKeyboardButton("📞 Контакты", callback_data="contact"),
         InlineKeyboardButton("ℹ️ О дизайнере", callback_data="about")],
        [InlineKeyboardButton("📋 Оформить заказ", url="https://t.me/alyx_babysitter")],
        [InlineKeyboardButton("🌐 Открыть сайт", url=WEBSITE_URL)]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Клавиатура с кнопкой назад"""
    keyboard = [
        [InlineKeyboardButton("🔙 Назад в меню", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Обработчики команд
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    is_new_user = db.add_user(user.id, user.to_dict())
    
    if is_new_user:
        # Приветствие для нового пользователя
        await update.message.reply_text(
            MESSAGES['welcome_new_user'],
            parse_mode='HTML',
            reply_markup=get_welcome_keyboard()
        )
    else:
        # Обычное меню для существующих пользователей
        await update.message.reply_text(
            MESSAGES['start'],
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /portfolio"""
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    await update.message.reply_text(
        MESSAGES['portfolio'],
        parse_mode='HTML',
        reply_markup=get_back_keyboard()
    )

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /services"""
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    await update.message.reply_text(
        MESSAGES['services'],
        parse_mode='HTML',
        reply_markup=get_back_keyboard()
    )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /contact"""
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    await update.message.reply_text(
        MESSAGES['contact'],
        parse_mode='HTML',
        reply_markup=get_back_keyboard()
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /about"""
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    await update.message.reply_text(
        MESSAGES['about'],
        parse_mode='HTML',
        reply_markup=get_back_keyboard()
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда статистики (только для владельца)"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде")
        return
    
    stats = db.get_stats()
    stats_text = f"""📊 <b>Статистика бота</b>

👥 Всего пользователей: {stats['total_users']}
🆕 Новых за сегодня: {stats['new_users_today']}
📋 Всего заказов: {stats['orders']}

📅 Последнее обновление: {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
    
    await update.message.reply_text(stats_text, parse_mode='HTML')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда рассылки (только для владельца)"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде")
        return
    
    # Получаем текст сообщения
    message_text = ' '.join(context.args)
    
    if not message_text:
        await update.message.reply_text(
            """📢 <b>Система рассылки</b>

Использование: /broadcast [сообщение]

Пример:
/broadcast Привет! У меня новые работы на сайте!

Сообщение будет отправлено всем пользователям бота.""",
            parse_mode='HTML'
        )
        return
    
    # Отправляем рассылку
    sent_count = 0
    failed_count = 0
    
    for user_id in db.users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"📢 <b>Сообщение от Alyx:</b>\n\n{message_text}",
                parse_mode='HTML'
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
    
    # Отчет о рассылке
    await update.message.reply_text(
        f"""✅ <b>Рассылка завершена</b>

📨 Отправлено: {sent_count}
❌ Ошибок: {failed_count}
👥 Всего пользователей: {len(db.users)}""",
        parse_mode='HTML'
    )

async def admin_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Справка по admin командам"""
    user_id = update.effective_user.id
    
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет доступа к этой команде")
        return
    
    help_text = """👑 <b>Admin команды</b>

📊 /stats - Статистика пользователей
📢 /broadcast [текст] - Рассылка сообщения всем пользователям
❓ /admin_help - Эта справка

<b>Примеры использования:</b>

<code>/broadcast Привет! Новые работы на сайте!</code>
<code>/stats</code>

<b>Автоматические функции:</b>
• Новые пользователи получают приветственное сообщение
• Статистика обновляется автоматически
• Логирование всех действий в bot.log"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')

# Обработчик callback кнопок
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на кнопки"""
    query = update.callback_query
    user_id = query.from_user.id
    
    await query.answer()
    db.update_last_seen(user_id)
    
    if query.data == "start_bot":
        # Переход от приветствия к основному меню
        await query.edit_message_text(
            MESSAGES['start'],
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    
    elif query.data == "portfolio":
        await query.edit_message_text(
            MESSAGES['portfolio'],
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
    
    elif query.data == "services":
        await query.edit_message_text(
            MESSAGES['services'],
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
    
    elif query.data == "contact":
        await query.edit_message_text(
            MESSAGES['contact'],
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
    
    elif query.data == "about":
        await query.edit_message_text(
            MESSAGES['about'],
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
    
    elif query.data == "back_to_main":
        await query.edit_message_text(
            MESSAGES['start'],
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )

def main():
    """Основная функция запуска бота"""
    
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # Admin команды
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("admin_help", admin_help_command))
    
    # Обработчик callback кнопок
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Запускаем бота
    logger.info("🚀 Запуск бота @alyx_design_bot с admin функциями...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

