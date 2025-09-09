#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Telegram бот для AI-дизайнера Alyx Babysitter
Полная версия - все в одном файле для быстрого старта
"""

import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebApp
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json
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

# База данных в памяти
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
            'joined_at': datetime.now(),
            'last_seen': datetime.now()
        }
    
    def update_last_seen(self, user_id: int):
        if user_id in self.users:
            self.users[user_id]['last_seen'] = datetime.now()
    
    def add_order(self, order_data: dict):
        order_data['id'] = len(self.orders) + 1
        order_data['created_at'] = datetime.now()
        order_data['status'] = 'new'
        self.orders.append(order_data)
        return order_data['id']
    
    def subscribe_user(self, user_id: int):
        if user_id not in self.subscribers:
            self.subscribers.append(user_id)
    
    def unsubscribe_user(self, user_id: int):
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)

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

🔥 <b>Нажмите Menu внизу, чтобы открыть портфолио!</b>""",

    'portfolio': """🎨 <b>Мое портфолио</b>

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

🏆 <b>Подход к работе:</b>
Быстро, чисто и системно. Каждый проект — это уникальное техническое решение с фокусом на детали и качество.

📱 Telegram: @alyx_babysitter""",

    'help': """❓ <b>Помощь</b>

🚀 <b>Как сделать заказ:</b>
1. Выберите услугу в разделе "Услуги"
2. Нажмите "Оформить заказ"
3. Заполните бриф
4. Ожидайте связи в течение часа

💬 <b>Команды бота:</b>
/start - Главная страница
/portfolio - Портфолио
/services - Услуги и цены  
/contact - Контакты
/about - О дизайнере

🌐 <b>Полное портфолио:</b>
www.alyxbabysitter.ru

📞 <b>Прямая связь:</b>
@alyx_babysitter в Telegram

⚡ Обычно отвечаю в течение 30 минут!""",

    'contact': """📞 <b>Контакты</b>

🎯 <b>Готовы начать проект?</b>

📱 <b>Telegram:</b> @alyx_babysitter
🌐 <b>Сайт:</b> www.alyxbabysitter.ru
⏰ <b>Время работы:</b> 10:00 - 22:00 MSK

💬 <b>Способы связи:</b>
• Написать в личные сообщения
• Оформить заказ через бота
• Открыть портфолио через Menu

🚀 <b>Как происходит работа:</b>
1. Обсуждаем задачу и бюджет
2. Заключаем договор, 50% предоплата  
3. Выполняю работу с промежуточными показами
4. Финальная приемка и доплата

⚡ <i>Обычно отвечаю в течение 30 минут!</i>"""
}

# Данные о услугах
SERVICES_DATA = {
    'order_twin': {
        'name': '🤖 Цифровой двойник',
        'price': 'От 15,000₽',
        'time': '2-3 недели',
        'description': 'Создание реалистичной AI-модели по вашим фотографиям'
    },
    'order_photo': {
        'name': '📸 AI-фотосессия',
        'price': 'От 5,000₽', 
        'time': '3-5 дней',
        'description': 'Пакет AI-фотографий в любой стилистике'
    },
    'order_video': {
        'name': '🎬 AI-сниппет',
        'price': 'От 3,000₽',
        'time': '2-3 дня', 
        'description': 'Короткий кинематографичный ролик 9-15 секунд'
    },
    'order_cover': {
        'name': '🎨 Обложка релиза',
        'price': 'От 2,000₽',
        'time': '1-2 дня',
        'description': 'Дизайн обложки для музыкального релиза'
    },
    'order_commercial': {
        'name': '💼 Коммерческая съемка',
        'price': 'От 8,000₽',
        'time': '5-7 дней',
        'description': 'Рекламные визуалы для продукта или услуги'
    }
}

# Состояния заказа
ORDER_STATES = {}

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
            InlineKeyboardButton("🌐 Открыть сайт", web_app=WebApp(url=WEBSITE_URL))
        ],
        [
            InlineKeyboardButton("🔔 Подписаться на новости", callback_data="subscribe")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_services_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🤖 Цифровой двойник", callback_data="order_twin"),
            InlineKeyboardButton("📸 AI-фотосессия", callback_data="order_photo")
        ],
        [
            InlineKeyboardButton("🎬 AI-сниппет", callback_data="order_video"),
            InlineKeyboardButton("🎨 Обложка", callback_data="order_cover")
        ],
        [
            InlineKeyboardButton("💼 Коммерческая съемка", callback_data="order_commercial")
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_portfolio_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🌐 Полное портфолио", web_app=WebApp(url=WEBSITE_URL))
        ],
        [
            InlineKeyboardButton("🤖 Цифровые двойники", callback_data="portfolio_twins"),
            InlineKeyboardButton("📸 AI-фотосессии", callback_data="portfolio_photos")
        ],
        [
            InlineKeyboardButton("🎬 Видео-сниппеты", callback_data="portfolio_videos"),
            InlineKeyboardButton("🎨 Обложки", callback_data="portfolio_covers")
        ],
        [
            InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        ]
    ]
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
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    await update.message.reply_text(
        MESSAGES['portfolio'],
        parse_mode='HTML',
        reply_markup=get_portfolio_keyboard()
    )

async def services_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    await update.message.reply_text(
        MESSAGES['services'],
        parse_mode='HTML',
        reply_markup=get_services_keyboard()
    )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    keyboard = [
        [InlineKeyboardButton("💬 Написать @alyx_babysitter", url="https://t.me/alyx_babysitter")],
        [InlineKeyboardButton("📋 Оформить заказ", callback_data="start_order")],
        [InlineKeyboardButton("🌐 Открыть сайт", web_app=WebApp(url=WEBSITE_URL))],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    
    await update.message.reply_text(
        MESSAGES['contact'],
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📱 Написать в Telegram", url="https://t.me/alyx_babysitter")],
        [InlineKeyboardButton("🌐 Посмотреть портфолио", web_app=WebApp(url=WEBSITE_URL))],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
    ]
    
    await update.message.reply_text(
        MESSAGES['about'],
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db.update_last_seen(user_id)
    
    await update.message.reply_text(
        MESSAGES['help'],
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )

# Обработчик callback запросов
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    db.update_last_seen(user_id)
    
    # Основная навигация
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
            reply_markup=get_portfolio_keyboard()
        )
    
    elif data == "services":
        await query.edit_message_text(
            MESSAGES['services'],
            parse_mode='HTML',
            reply_markup=get_services_keyboard()
        )
    
    elif data == "contact":
        keyboard = [
            [InlineKeyboardButton("💬 Написать @alyx_babysitter", url="https://t.me/alyx_babysitter")],
            [InlineKeyboardButton("📋 Оформить заказ", callback_data="start_order")],
            [InlineKeyboardButton("🌐 Открыть сайт", web_app=WebApp(url=WEBSITE_URL))],
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
            [InlineKeyboardButton("🌐 Посмотреть портфолио", web_app=WebApp(url=WEBSITE_URL))],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            MESSAGES['about'],
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # Подписка на новости
    elif data == "subscribe":
        db.subscribe_user(user_id)
        
        keyboard = [
            [InlineKeyboardButton("🔕 Отписаться", callback_data="unsubscribe")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            "🔔 <b>Подписка активирована!</b>\n\nТеперь вы будете получать уведомления о новых работах и специальных предложениях.\n\n<i>Обычно отправляю 1-2 сообщения в неделю.</i>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif data == "unsubscribe":
        db.unsubscribe_user(user_id)
        
        await query.edit_message_text(
            "🔕 <b>Подписка отключена</b>\n\nВы больше не будете получать уведомления.\n\nЕсли передумаете, всегда можете подписаться снова!",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    
    # Система заказов
    elif data.startswith("order_"):
        service = SERVICES_DATA.get(data)
        if service:
            keyboard = [
                [InlineKeyboardButton("📋 Оформить заказ", callback_data=f"create_{data}")],
                [InlineKeyboardButton("💬 Обсудить детали", url="https://t.me/alyx_babysitter")],
                [InlineKeyboardButton("🔙 К услугам", callback_data="services")]
            ]
            
            message = f"""<b>{service['name']}</b>

💰 <b>Стоимость:</b> {service['price']}
⏰ <b>Сроки:</b> {service['time']}

📝 <b>Что включено:</b>
{service['description']}

<b>Процесс работы:</b>
1. Обсуждаем техническое задание
2. Заключаем договор, 50% предоплата
3. Выполняю работу с промежуточными показами
4. Финальная приемка и доплата

💬 <i>Можем обсудить детали и скорректировать под ваш бюджет!</i>"""
            
            await query.edit_message_text(
                message,
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif data.startswith("create_order_"):
        service_type = data.replace("create_", "")
        service = SERVICES_DATA.get(service_type)
        
        if service:
            ORDER_STATES[user_id] = {
                'service_type': service_type,
                'service_name': service['name'],
                'step': 'name'
            }
            
            keyboard = [[InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]]
            
            await query.edit_message_text(
                f"""📋 <b>Оформление заказа: {service['name']}</b>

<b>Шаг 1 из 4:</b> Как к вам обращаться?

Напишите ваше имя или никнейм следующим сообщением.""",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    
    elif data == "cancel_order":
        if user_id in ORDER_STATES:
            del ORDER_STATES[user_id]
        
        await query.edit_message_text(
            "❌ <b>Заказ отменен</b>\n\nВы можете оформить заказ в любое время!",
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
    
    elif data == "start_order":
        await query.edit_message_text(
            "💎 <b>Выберите услугу для заказа:</b>",
            parse_mode='HTML',
            reply_markup=get_services_keyboard()
        )

# Обработка текстовых сообщений для заказов
async def handle_order_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ORDER_STATES:
        return
    
    order_state = ORDER_STATES[user_id]
    text = update.message.text
    
    if order_state['step'] == 'name':
        order_state['name'] = text
        order_state['step'] = 'contact'
        
        keyboard = [[InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]]
        
        await update.message.reply_text(
            f"""📋 <b>Оформление заказа: {order_state['service_name']}</b>

<b>Шаг 2 из 4:</b> Контакты

Как с вами связаться? Напишите:
• Telegram: @username
• Телефон: +7 (xxx) xxx-xx-xx  
• Email: example@mail.com

Или любой удобный способ связи.""",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif order_state['step'] == 'contact':
        order_state['contact'] = text
        order_state['step'] = 'budget'
        
        keyboard = [[InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]]
        
        await update.message.reply_text(
            f"""📋 <b>Оформление заказа: {order_state['service_name']}</b>

<b>Шаг 3 из 4:</b> Бюджет

Какой у вас бюджет на проект?

Можете написать:
• Конкретную сумму
• Диапазон (например: 5,000-10,000₽)
• "Обсудим" - если хотите узнать стоимость""",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif order_state['step'] == 'budget':
        order_state['budget'] = text
        order_state['step'] = 'description'
        
        keyboard = [[InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]]
        
        await update.message.reply_text(
            f"""📋 <b>Оформление заказа: {order_state['service_name']}</b>

<b>Шаг 4 из 4:</b> Описание проекта

Расскажите подробнее о вашем проекте:
• Что именно нужно создать?
• Какая стилистика?
• Есть ли референсы?
• Особые пожелания?

Чем больше деталей, тем точнее смогу оценить проект!""",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif order_state['step'] == 'description':
        order_state['description'] = text
        
        # Сохраняем заказ
        order_data = {
            'user_id': user_id,
            'username': update.effective_user.username or 'Не указан',
            'first_name': update.effective_user.first_name or 'Не указано',
            'service_type': order_state['service_type'],
            'service_name': order_state['service_name'],
            'name': order_state['name'],
            'contact': order_state['contact'],
            'budget': order_state['budget'],
            'description': order_state['description']
        }
        
        order_id = db.add_order(order_data)
        
        # Удаляем состояние заказа
        del ORDER_STATES[user_id]
        
        # Отправляем подтверждение клиенту
        await update.message.reply_text(
            f"""✅ <b>Заказ #{order_id} оформлен!</b>

<b>Что дальше:</b>
• Свяжусь с вами в течение часа
• Обсудим все детали проекта  
• При необходимости скорректируем бюджет
• Заключим договор и приступим к работе

<b>Ваши данные:</b>
📋 Услуга: {order_state['service_name']}
👤 Имя: {order_state['name']}
📞 Контакт: {order_state['contact']}
💰 Бюджет: {order_state['budget']}

📱 Также можете написать напрямую: @alyx_babysitter

<i>Спасибо за доверие! 🙏</i>""",
            parse_mode='HTML'
        )
        
        # Отправляем уведомление владельцу
        owner_message = f"""🔔 <b>Новый заказ #{order_id}</b>

<b>Клиент:</b>
👤 {order_data['first_name']} (@{order_data['username']})
🆔 ID: {user_id}

<b>Заказ:</b>
📋 {order_data['service_name']}
💰 Бюджет: {order_data['budget']}
📞 Контакт: {order_data['contact']}

<b>Описание проекта:</b>
{order_data['description']}

<i>Время заказа: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"""
        
        try:
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=owner_message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления владельцу: {e}")

# Команды для владельца
async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для использования этой команды.")
        return
    
    if not context.args:
        await update.message.reply_text(
            """📢 <b>Команда рассылки</b>

<b>Использование:</b>
/broadcast <текст сообщения>

<b>Пример:</b>
/broadcast 🎉 Новая работа в портфолио! Посмотрите AI-портреты в стиле Y2K.""",
            parse_mode='HTML'
        )
        return
    
    message = ' '.join(context.args)
    
    sent_count = 0
    failed_count = 0
    
    for subscriber_id in db.subscribers:
        try:
            await context.bot.send_message(
                chat_id=subscriber_id,
                text=f"🔔 <b>Новости от Alyx Babysitter</b>\n\n{message}",
                parse_mode='HTML'
            )
            sent_count += 1
        except Exception as e:
            failed_count += 1
            logger.error(f"Не удалось отправить сообщение пользователю {subscriber_id}: {e}")
    
    await update.message.reply_text(
        f"""📊 <b>Рассылка завершена!</b>

✅ Отправлено: {sent_count}
❌ Не доставлено: {failed_count}
👥 Всего подписчиков: {len(db.subscribers)}""",
        parse_mode='HTML'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ У вас нет прав для использования этой команды.")
        return
    
    total_users = len(db.users)
    total_orders = len(db.orders)
    total_subscribers = len(db.subscribers)
    
    week_ago = datetime.now() - timedelta(days=7)
    new_users_week = sum(1 for user in db.users.values() if user['joined_at'] > week_ago)
    
    stats_message = f"""📊 <b>Статистика бота</b>

👥 <b>Пользователи:</b>
• Всего: {total_users}
• Новых за неделю: {new_users_week}
• Подписчиков: {total_subscribers}

📋 <b>Заказы:</b>
• Всего заказов: {total_orders}

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
    application.add_handler(CommandHandler("help", help_command))
    
    # Команды для владельца
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Обработчик callback кнопок
    application.add_handler(CallbackQueryHandler(callback_handler))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_order_text
    ))
    
    # Запускаем бота
    logger.info("🚀 Запуск бота @alyx_design_bot...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == "__main__":
    main()
