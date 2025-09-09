#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from typing import Dict, List

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация бота
BOT_TOKEN = "8307209669:AAFl5JKEBUPkJ8akr01RfXKwvLTNEoQPLqQ"
OWNER_ID = 1014948227
WEBSITE_URL = "https://www.alyxbabysitter.ru"

# Простая база данных
class Database:
    def __init__(self):
        self.users: Dict[int, dict] = {}
        self.orders: List[dict] = []
        self.subscribers: List[int] = []
    
    def add_user(self, user_id: int, user_data: dict):
        self.users[user_id] = {
            'id': user_id,
            'first_name': user_data.get('first_name', ''),
            'username': user_data.get('username', ''),
            'joined_at': datetime.now()
        }
    
    def add_order(self, order_data: dict):
        order_data['id'] = len(self.orders) + 1
        order_data['created_at'] = datetime.now()
        self.orders.append(order_data)
        return order_data['id']
    
    def subscribe_user(self, user_id: int):
        if user_id not in self.subscribers:
            self.subscribers.append(user_id)

db = Database()

# Тексты сообщений
MESSAGES = {
    'start': """🎨 <b>Добро пожаловать в мир AI-дизайна!</b>

Я Alyx Babysitter — AI-дизайнер, создаю:
• 🤖 Цифровые двойники
• 📸 AI-фотосессии  
• 🎬 Видео-сниппеты
• 🎨 Обложки и дизайн
• 💼 Коммерческие съемки

<i>Быстро, чисто и системно.</i>

🌐 Сайт: www.alyxbabysitter.ru
📱 Telegram: @alyx_babysitter""",

    'portfolio': """🎨 <b>Мое портфолио</b>

Посмотрите мои работы:
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
Рекламные визуалы для бизнеса""",

    'contact': """📞 <b>Контакты</b>

🎯 <b>Готовы начать проект?</b>

📱 <b>Telegram:</b> @alyx_babysitter
🌐 <b>Сайт:</b> www.alyxbabysitter.ru
⏰ <b>Время работы:</b> 10:00 - 22:00 MSK

🚀 <b>Как происходит работа:</b>
1. Обсуждаем задачу и бюджет
2. Заключаем договор, 50% предоплата  
3. Выполняю работу с промежуточными показами
4. Финальная приемка и доплата

⚡ <i>Обычно отвечаю в течение 30 минут!</i>""",

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
• Коммерческие проекты для брендов

📱 Telegram: @alyx_babysitter"""
}

# Клавиатуры
def get_main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🎨 Портфолио", callback_data="portfolio"),
            InlineKeyboardButton("💎 Услуги", callback_data="services")
        ],
        [
            InlineKeyboardButton("📞 Контакты", callback_data="contact"),
            InlineKeyboardButton("ℹ️ О дизайнере", callback_data="about")
        ],
        [
            InlineKeyboardButton("🌐 Открыть сайт", url=WEBSITE_URL)
        ],
        [
            InlineKeyboardButton("🔔 Подписаться на новости", callback_data="subscribe")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
    return InlineKeyboardMarkup(keyboard)

# Обработчики команд
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.to_dict())
    
    await update.message.reply_text(
        MESSAGES['start'],
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        MESSAGES['portfolio'],
        parse_mode='HTML',
        reply_markup=get_back_keyboard()
    )

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📋 Заказать услугу", url="https://t.me/alyx_babysitter")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    
    await update.message.reply_text(
        MESSAGES['services'],
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Написать @alyx_babysitter", url="https://t.me/alyx_babysitter")],
        [InlineKeyboardButton("🌐 Открыть сайт", url=WEBSITE_URL)],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    
    await update.message.reply_text(
        MESSAGES['contact'],
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 Написать в Telegram", url="https://t.me/alyx_babysitter")],
        [InlineKeyboardButton("🌐 Посмотреть портфолио", url=WEBSITE_URL)],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    
    await update.message.reply_text(
        MESSAGES['about'],
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработчик callback запросов
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "back_to_main":
        await query.edit_message_text(
            MESSAGES['start'],
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    
    elif data == "portfolio":
        await query.edit_message_text(
            MESSAGES['portfolio'],
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )
    
    elif data == "services":
        keyboard = [
            [InlineKeyboardButton("📋 Заказать услугу", url="https://t.me/alyx_babysitter")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            MESSAGES['services'],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "contact":
        keyboard = [
            [InlineKeyboardButton("💬 Написать @alyx_babysitter", url="https://t.me/alyx_babysitter")],
            [InlineKeyboardButton("🌐 Открыть сайт", url=WEBSITE_URL)],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            MESSAGES['contact'],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "about":
        keyboard = [
            [InlineKeyboardButton("📱 Написать в Telegram", url="https://t.me/alyx_babysitter")],
            [InlineKeyboardButton("🌐 Посмотреть портфолио", url=WEBSITE_URL)],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            MESSAGES['about'],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "subscribe":
        user_id = query.from_user.id
        db.subscribe_user(user_id)
        
        await query.edit_message_text(
            "🔔 <b>Подписка активирована!</b>\n\nТеперь вы будете получать уведомления о новых работах.\n\n💬 Для заказов пишите: @alyx_babysitter",
            parse_mode='HTML',
            reply_markup=get_back_keyboard()
        )

# Команда статистики для владельца
async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для использования этой команды.")
        return
    
    total_users = len(db.users)
    total_subscribers = len(db.subscribers)
    
    stats_message = f"""📊 <b>Статистика бота</b>

👥 <b>Пользователи:</b> {total_users}
🔔 <b>Подписчиков:</b> {total_subscribers}

⏰ <b>Обновлено:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"""
    
    await update.message.reply_text(stats_message, parse_mode='HTML')

def main():
    """Основная функция запуска бота"""
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("portfolio", portfolio_command))
    application.add_handler(CommandHandler("services", services_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Обработчик callback кнопок
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Запускаем бота
    logger.info("🚀 Запуск упрощенного бота @alyx_design_bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
