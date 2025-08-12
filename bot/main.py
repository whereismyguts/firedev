import os
import logging
import asyncio
import uuid
from datetime import datetime
import aiohttp

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
logger = logging.getLogger("firedev-bot")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

if not BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN env var is required")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Store user data in memory (for production, consider Redis)
user_data = {}

def get_category_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="🔥 Fire Source", callback_data="fire")
    builder.button(text="👤 Volunteer Position", callback_data="volunteer")
    builder.button(text="🚒 Fire Brigade", callback_data="brigade")
    builder.button(text="✈️ Fireplane Flight", callback_data="plane")
    builder.adjust(1)
    return builder.as_markup()

@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "🔥 **Fire Coordination Bot**\n\n"
        "Send your location (static or live) and I'll ask what category it represents.\n\n"
        "Commands:\n"
        "/help - Show this help\n"
        "/cancel - Cancel current operation\n"
        "/stop_live - Stop live location updates"
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "📍 **How to use:**\n\n"
        "1. Share your location (tap 📎 → Location)\n"
        "2. Choose what the location represents\n"
        "3. Watch it appear on the map!\n\n"
        "🎯 **Live Locations:**\n"
        "Enable live location sharing for real-time tracking.\n"
        "Use /stop_live to end live updates."
    )

@dp.message(Command("cancel"))
async def cancel_command(message: types.Message):
    user_id = message.from_user.id
    user_data.pop(user_id, None)
    await message.answer("❌ Operation canceled.")

@dp.message(Command("stop_live"))
async def stop_live_command(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_data:
        user_data[user_id]['live_active'] = False
    await message.answer("⏹️ Live location updates stopped.")

@dp.message(F.location)
async def handle_location(message: types.Message):
    user_id = message.from_user.id
    location = message.location
    
    # Initialize user data if needed
    if user_id not in user_data:
        user_data[user_id] = {}
    
    # Store location
    user_data[user_id]['last_location'] = {
        'lat': location.latitude, 
        'lon': location.longitude
    }
    
    # Check if this is a live location
    if location.live_period:
        user_data[user_id]['live_id'] = user_data[user_id].get('live_id') or str(uuid.uuid4())
        user_data[user_id]['live_active'] = True
        await message.answer(
            "📍 **Live location detected!**\n"
            "Choose category and I'll track updates in real-time:",
            reply_markup=get_category_keyboard()
        )
    else:
        await message.answer(
            "📍 **Location received!**\n"
            "What does this location represent?",
            reply_markup=get_category_keyboard()
        )

@dp.edited_message(F.location)
async def handle_edited_location(edited_message: types.Message):
    """Handle live location updates"""
    user_id = edited_message.from_user.id
    location = edited_message.location
    
    if user_id not in user_data:
        return
    
    # Update stored location
    user_data[user_id]['last_location'] = {
        'lat': location.latitude,
        'lon': location.longitude
    }
    
    # If already categorized and live tracking is active, send update
    if (user_data[user_id].get('live_active') and 
        user_data[user_id].get('category')):
        await send_location_update(user_id, edited_message.from_user)

@dp.callback_query(F.data.in_(["fire", "volunteer", "brigade", "plane"]))
async def handle_category_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    category = callback.data
    
    if user_id not in user_data or 'last_location' not in user_data[user_id]:
        await callback.answer("❌ No location found. Please send your location first.")
        return
    
    user_data[user_id]['category'] = category
    location = user_data[user_id]['last_location']
    
    # Prepare payload
    now = datetime.utcnow().isoformat()
    payload = {
        'category': category,
        'lat': location['lat'],
        'lon': location['lon'],
        'user': callback.from_user.username or f"id_{callback.from_user.id}",
        'timestamp': now,
        'action': 'active'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            if user_data[user_id].get('live_active'):
                # Use PUT for live locations with fixed ID
                live_id = user_data[user_id]['live_id']
                async with session.put(
                    f"{BACKEND_URL}/report/{live_id}", 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        category_emoji = {"fire": "🔥", "volunteer": "👤", "brigade": "🚒", "plane": "✈️"}
                        await callback.message.edit_text(
                            f"✅ **Live {category_emoji.get(category, '📍')} {category} tracking started!**\n\n"
                            f"I'll keep updating your position automatically.\n"
                            f"Use /stop_live to end tracking."
                        )
                    else:
                        await callback.message.edit_text("❌ Failed to save live location. Try again.")
            else:
                # Use POST for static locations
                async with session.post(
                    f"{BACKEND_URL}/report",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 201:
                        category_emoji = {"fire": "🔥", "volunteer": "👤", "brigade": "🚒", "plane": "✈️"}
                        await callback.message.edit_text(
                            f"✅ **{category_emoji.get(category, '📍')} {category} location saved!**\n\n"
                            f"View the map: https://whereismyguts.github.io/firedev/"
                        )
                    else:
                        await callback.message.edit_text("❌ Failed to save location. Try again.")
        
        await callback.answer()
        
    except Exception as e:
        logger.exception("Failed to save location: %s", e)
        await callback.message.edit_text("❌ Error saving location. Check if backend is running.")
        await callback.answer()

async def send_location_update(user_id: int, user: types.User):
    """Send live location update to backend"""
    if user_id not in user_data:
        return
    
    location = user_data[user_id]['last_location']
    category = user_data[user_id]['category']
    live_id = user_data[user_id]['live_id']
    
    payload = {
        'category': category,
        'lat': location['lat'],
        'lon': location['lon'],
        'user': user.username or f"id_{user.id}",
        'timestamp': datetime.utcnow().isoformat(),
        'action': 'active'
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{BACKEND_URL}/report/{live_id}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status != 200:
                    logger.warning(f"Live update failed: {response.status}")
    except Exception as e:
        logger.warning(f"Live update failed: {e}")

async def main():
    logger.info("Starting Fire Coordination Bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
