import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, BotCommand, MenuButtonCommands
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from pathlib import Path
import asyncio

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "7754735588:AAFkiW8ykrfvE3cMK-3uLuoC56dhKeRrC_g"

BESTIARY = {
    "creature1": {
        "name": "Тодд",
        "description": "Он не идёт, а продавливает лес своей тяжёлой поступью, а его ледяной взгляд выхватывает жертв даже в кромешной тьме, будто он сам — лишь ещё один хищник в этом гниющем мире.",
        "image_path1": "images/bestiary/hunter1.jpg",
        "image_path2": "images/bestiary/hunter2.jpg"
    },
    "creature2": {
        "name": "Волки Хагаан",
        "description": "Их укус гниёт, как сам лес, а их шерсть — сплошная корка из крови и грязи.",
        "image_path1": "images/bestiary/wolf.png",
        "image_path2": "images/bestiary/wolf(colored).jpg"
    },
    "creature3": {
        "name": "Вана’квеши",
        "description": "Они не бегут, а скользят на своих костяных ногах. Их раздвоенные челюсти шепчут что-то на забытом языке.",
        "image_path1": "images/bestiary/deer.jpg"
    },
    "creature4": {
        "name": "Вендиго",
        "description": "Он не охотится, а медленно сходит с ума — его олений череп скрипит с каждым шагом, а костяные пальцы, изодранные собственными зубами, тянутся к теплу живой плоти, которую когда-то называл себе подобной.",
        "image_path1": "images/bestiary/Vendigo1.jpg",
        "image_path2": "images/bestiary/Vendigo2.jpg"
    },
}

LOCATIONS = {
    "location1": {
        "name": "Гнилой лес (Врэквуд)",
        "description": "Здесь земля дышит через разверстые корни, а между стволами мелькают тени тех, кто осмелился войти.",
        "image_path1": "images/locations/forest2.jpg",
        "image_path2": "images/locations/forest1.jpg"
    },
}

STORY_NOTES = {
    "note1": {
        "name": "Рэйвенкрест и окрестности",
        "description": "Город под названием Рэйвенкрест стоит совсем рядом с лесом Вреквуд. Лес известен своей дремучестью, потому то его так и назвали. Но за этим названием может стоять и нечто большее..." + "\n" + "В городишке уж очень популярна охота всвязи с наличием таких обшиных дебрей поблизости. А сами охотники часто отдыхают в местных тавернах.",
        "image_path1": "images/notes/note1.png"
    },
    "note2": {
        "name": "Слухи",
        "description": "Страшные слухи ползут по городу. Множество охотников, от стариков до молодняка, сообщают о некоем страшном большом звере, что похож на оленя, но им не является. Голова и рога белы, а ходит он на задних лапах. Из глотки его исходит ужасающий неестественный рев. Но как миниму один охотник считает это чудище лишь бешенным крупным оленем.",
        "image_path1": "images/notes/note2.png"
    },
    "note3": {
        "name": "Бешенный олень",
        "description": "Высокий худой силуэт медленно движется меж деревьев. Он слегка пригнулся к земле, но рога все равно цепляются за ветки и ломают их. Очи-огоньки блуждают по окружающему его пространству, пока вдруг не остановились на охотнике...",
        "image_path1": "images/notes/note3.png"
    },
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    context.user_data['last_media_messages'] = []
    context.user_data['last_keyboard_message'] = None
    
    try:
        commands = [
            BotCommand("start", "Запустить бота и открыть главное меню")
        ]
        await context.bot.set_my_commands(commands)
        await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    except Exception as e:
        logging.error(f"Error setting up commands: {e}")
    
    keyboard = [
        [InlineKeyboardButton("🐾 Бестиарий", callback_data='bestiary')],
        [InlineKeyboardButton("🗺 Локации", callback_data='locations')],
        [InlineKeyboardButton("📝 Сюжетные заметки", callback_data='notes')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Добро пожаловать в игровую энциклопедию! Выберите категорию:',
        reply_markup=reply_markup
    )

async def delete_previous_messages(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Delete previous media and keyboard messages."""
    if 'last_media_messages' in context.user_data:
        for msg_id in context.user_data['last_media_messages']:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            except Exception as e:
                logging.error(f"Error deleting media message {msg_id}: {e}")
        context.user_data['last_media_messages'] = []
    
    if 'last_keyboard_message' in context.user_data and context.user_data['last_keyboard_message']:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=context.user_data['last_keyboard_message'])
        except Exception as e:
            logging.error(f"Error deleting keyboard message: {e}")
        context.user_data['last_keyboard_message'] = None

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()

    if query.data == 'bestiary':
        await delete_previous_messages(context, query.message.chat_id)
        
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f'beast_{key}')] 
                   for key, item in BESTIARY.items()]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Выберите существо из бестиария:",
            reply_markup=reply_markup
        )
    
    elif query.data == 'locations':
        await delete_previous_messages(context, query.message.chat_id)
        
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f'loc_{key}')] 
                   for key, item in LOCATIONS.items()]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Выберите локацию:",
            reply_markup=reply_markup
        )
    
    elif query.data == 'notes':
        await delete_previous_messages(context, query.message.chat_id)
        
        keyboard = [[InlineKeyboardButton(item["name"], callback_data=f'note_{key}')] 
                   for key, item in STORY_NOTES.items()]
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Выберите сюжетную заметку:",
            reply_markup=reply_markup
        )
    
    elif query.data == 'main_menu':
        await delete_previous_messages(context, query.message.chat_id)
        
        keyboard = [
            [InlineKeyboardButton("🐾 Бестиарий", callback_data='bestiary')],
            [InlineKeyboardButton("🗺 Локации", callback_data='locations')],
            [InlineKeyboardButton("📝 Сюжетные заметки", callback_data='notes')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text='Добро пожаловать в игровую энциклопедию! Выберите категорию:',
            reply_markup=reply_markup
        )
    
    elif query.data.startswith('beast_'):
        item_key = query.data.replace('beast_', '')
        item = BESTIARY[item_key]
        keyboard = [[InlineKeyboardButton("🔙 К бестиарию", callback_data='bestiary')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if not os.path.exists(item['image_path1']):
                logging.error(f"File not found: {item['image_path1']}")
                raise FileNotFoundError(f"Image file not found: {item['image_path1']}")

            media_group = []
            caption = f"{item['name']}\n\n{item['description']}"
            
            try:
                media_group.append(
                    InputMediaPhoto(
                        media=open(item['image_path1'], 'rb'),
                        caption=caption
                    )
                )
            except Exception as e:
                logging.error(f"Error opening first image {item['image_path1']}: {str(e)}")
                raise
            
            if 'image_path2' in item:
                if not os.path.exists(item['image_path2']):
                    logging.error(f"Second image file not found: {item['image_path2']}")
                else:
                    try:
                        media_group.append(
                            InputMediaPhoto(
                                media=open(item['image_path2'], 'rb')
                            )
                        )
                    except Exception as e:
                        logging.error(f"Error opening second image {item['image_path2']}: {str(e)}")
            
            if not media_group:
                raise Exception("No valid images to send")
            
            await delete_previous_messages(context, query.message.chat_id)
            
            sent_media = await context.bot.send_media_group(
                chat_id=query.message.chat_id,
                media=media_group
            )
            
            context.user_data['last_media_messages'] = [msg.message_id for msg in sent_media]
            
            keyboard_message = await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Выберите действие:",
                reply_markup=reply_markup
            )
            
            context.user_data['last_keyboard_message'] = keyboard_message.message_id
            
        except FileNotFoundError as e:
            logging.error(f"File not found error: {str(e)}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{item['name']}\n\n{item['description']}\n\n⚠️ Ошибка: файл изображения не найден",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Error in beast handler: {str(e)}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{item['name']}\n\n{item['description']}\n\n⚠️ Ошибка при загрузке изображений: {str(e)}",
                reply_markup=reply_markup
            )
        finally:
            for media in media_group:
                try:
                    if hasattr(media.media, 'close'):
                        media.media.close()
                except:
                    pass
    
    elif query.data.startswith('loc_'):
        item_key = query.data.replace('loc_', '')
        item = LOCATIONS[item_key]
        keyboard = [[InlineKeyboardButton("🔙 К локациям", callback_data='locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if not os.path.exists(item['image_path1']):
                logging.error(f"File not found: {item['image_path1']}")
                raise FileNotFoundError(f"Image file not found: {item['image_path1']}")

            media_group = []
            caption = f"{item['name']}\n\n{item['description']}"
            
            try:
                media_group.append(
                    InputMediaPhoto(
                        media=open(item['image_path1'], 'rb'),
                        caption=caption
                    )
                )
            except Exception as e:
                logging.error(f"Error opening first image {item['image_path1']}: {str(e)}")
                raise
            
            if 'image_path2' in item:
                if not os.path.exists(item['image_path2']):
                    logging.error(f"Second image file not found: {item['image_path2']}")
                else:
                    try:
                        media_group.append(
                            InputMediaPhoto(
                                media=open(item['image_path2'], 'rb')
                            )
                        )
                    except Exception as e:
                        logging.error(f"Error opening second image {item['image_path2']}: {str(e)}")
            
            if not media_group:
                raise Exception("No valid images to send")
            
            await delete_previous_messages(context, query.message.chat_id)
            
            sent_media = await context.bot.send_media_group(
                chat_id=query.message.chat_id,
                media=media_group
            )
            
            context.user_data['last_media_messages'] = [msg.message_id for msg in sent_media]
            
            keyboard_message = await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Выберите действие:",
                reply_markup=reply_markup
            )
            
            context.user_data['last_keyboard_message'] = keyboard_message.message_id
            
        except FileNotFoundError as e:
            logging.error(f"File not found error: {str(e)}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{item['name']}\n\n{item['description']}\n\n⚠️ Ошибка: файл изображения не найден",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Error in location handler: {str(e)}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{item['name']}\n\n{item['description']}\n\n⚠️ Ошибка при загрузке изображений: {str(e)}",
                reply_markup=reply_markup
            )
        finally:
            for media in media_group:
                try:
                    if hasattr(media.media, 'close'):
                        media.media.close()
                except:
                    pass
    
    elif query.data.startswith('note_'):
        item_key = query.data.replace('note_', '')
        item = STORY_NOTES[item_key]
        keyboard = [[InlineKeyboardButton("🔙 К заметкам", callback_data='notes')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            if not os.path.exists(item['image_path1']):
                logging.error(f"File not found: {item['image_path1']}")
                raise FileNotFoundError(f"Image file not found: {item['image_path1']}")

            media_group = []
            caption = f"{item['name']}\n\n{item['description']}"
            
            try:
                media_group.append(
                    InputMediaPhoto(
                        media=open(item['image_path1'], 'rb'),
                        caption=caption
                    )
                )
            except Exception as e:
                logging.error(f"Error opening first image {item['image_path1']}: {str(e)}")
                raise
            
            if 'image_path2' in item:
                if not os.path.exists(item['image_path2']):
                    logging.error(f"Second image file not found: {item['image_path2']}")
                else:
                    try:
                        media_group.append(
                            InputMediaPhoto(
                                media=open(item['image_path2'], 'rb')
                            )
                        )
                    except Exception as e:
                        logging.error(f"Error opening second image {item['image_path2']}: {str(e)}")
            
            if not media_group:
                raise Exception("No valid images to send")
            
            await delete_previous_messages(context, query.message.chat_id)
            
            sent_media = await context.bot.send_media_group(
                chat_id=query.message.chat_id,
                media=media_group
            )
            
            context.user_data['last_media_messages'] = [msg.message_id for msg in sent_media]
            
            keyboard_message = await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Выберите действие:",
                reply_markup=reply_markup
            )
            
            context.user_data['last_keyboard_message'] = keyboard_message.message_id
            
        except FileNotFoundError as e:
            logging.error(f"File not found error: {str(e)}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{item['name']}\n\n{item['description']}\n\n⚠️ Ошибка: файл изображения не найден",
                reply_markup=reply_markup
            )
        except Exception as e:
            logging.error(f"Error in note handler: {str(e)}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"{item['name']}\n\n{item['description']}\n\n⚠️ Ошибка при загрузке изображений: {str(e)}",
                reply_markup=reply_markup
            )
        finally:
            for media in media_group:
                try:
                    if hasattr(media.media, 'close'):
                        media.media.close()
                except:
                    pass

def main():
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 
