import requests
from bs4 import BeautifulSoup
from telegram import ForceReply, Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import telegram

bot_token = '6751312142:AAGtAOOvdDulXbcUi86exAxMDsSDPhYO7Qs'
generic_image_url = 'https://t3.ftcdn.net/jpg/02/48/42/64/360_F_248426448_NVKLywWqArG2ADUxDq6QprtIzsF82dMF.jpg'
channel_id = '-1002093943364'
VALID_CATEGORIES = ["recent", "cars", "mobiles-tablets", "house", "fashion"]

async def scrape_data(url):
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    listings_container = soup.find('div', class_='hp-listings')

    if listings_container != None:
        listings = listings_container.find_all('article', class_='hp-listing')

    data = []
    for listing in listings:
        link = listing.find('a')['href']
        image_url = listing.find('img')['src'] 
        item = listing.find('h4', class_='hp-listing__title').text.strip()
        added_date = listing.find('time', class_='hp-listing__created-date').text.strip().split('on ')[1]
        phone_number = listing.find('div', class_='hp-listing__attribute--phone-number').text.strip().split(': ')[1]
        price = listing.find('div', class_='hp-listing__attribute--price-range').text.strip().split(': ')[1]

        data.append({
            'Item': item,
            'Added Date': added_date,
            'Phone Number': phone_number,
            'Price': price,
            'Image URL': image_url,
            'Link': link
        })

    return data


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    user = update.effective_user
    welcome_message = (
        f"<b>Welcome to Qefira Bot, {user.first_name}!</b>\n\n"
        "I'm here to help you find listings on Qefira.\n\n"
        "To get started, you can use the following commands:\n\n"
        "/listings [category] - Get listings from Qefira based on the specified category.\n"
        "For example: /listings cars\n\n"
        "If you need assistance, you can always use the /help command."
    )
    await update.message.reply_text(welcome_message, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display help information about the available commands."""
    help_message = (
        "<b>Welcome to Qefira Bot Help</b>\n\n"
        "Here are the available commands:\n\n"
        "/start - Start the bot and get a welcome message.\n"
        "/help - Display this help message.\n"
        "/listings [category] - Get listings from Qefira based on the specified category. Available categories are:\n"
        "  - recent: Get recent listings.\n"
        "  - cars: Get listings for cars.\n"
        "  - mobiles-tablets: Get listings for mobile phones and tablets.\n"
        "  - house: Get listings for houses.\n"
        "  - fashion: Get listings for fashion items.\n\n"
        "Example: /listings cars"
    )
    await update.message.reply_text(help_message, parse_mode='HTML')

async def get_listings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    category = context.matches[0].group(1)

    if category not in VALID_CATEGORIES:
        await update.message.reply_text("Invalid category. Please choose from: " + ", ".join(VALID_CATEGORIES))
        return

    baseUrl = 'https://qefira.com.et'
    if category != 'recent':
        url = baseUrl + '/listing-category/' + category + '/'
    else:
        url = baseUrl
    
    print("URL: " + url)

    recent_listings = await scrape_data(url)
    bot = telegram.Bot(token=bot_token)

    start_message = f"\n\n<b>Results for {category} listings:</b>\n\n"
    await bot.send_message(chat_id=channel_id, text=start_message, parse_mode='HTML')

    channel_link = f"View listings for {category} on the channel: https://t.me/qefira_buy"
    await update.message.reply_text(channel_link)

    for listing in recent_listings:
        item = listing['Item']
        added_date = listing['Added Date']
        phone_number = listing['Phone Number']
        price = listing['Price']
        image_url = listing['Image URL']
        link = listing['Link']

        try: 
            if '?' in image_url:
                image_url = image_url.split('?')[0]

            if image_url.endswith('.svg'):
                image_url = generic_image_url

            # Create a formatted message
            message = f"<b>Item:</b> {item}\n"
            message += f"<b>Added Date:</b> {added_date}\n"
            message += f"<b>Phone Number:</b> {phone_number}\n"
            message += f"<b>Price:</b> {price}\n"
            message += f"<b>Link:</b> {link}"

            media = [InputMediaPhoto(media=image_url, caption=message, parse_mode='HTML')]
            # await update.message.reply_media_group(media)
            await bot.send_media_group(chat_id=channel_id, media=media)

        except telegram.error.BadRequest as e:
            if "wrong file identifier/http url specified" in str(e):
                message = f"<b>Item:</b> {item}\n"
                message += f"<b>Added Date:</b> {added_date}\n"
                message += f"<b>Phone Number:</b> {phone_number}\n"
                message += f"<b>Price:</b> {price}\n"
                message += f"<b>Link:</b> {link}\n"
                message += "Image format not supported. Sending a generic image instead."
                media = [InputMediaPhoto(media=generic_image_url, caption=message, parse_mode='HTML')]
                # await update.message.reply_media_group(media)
                await bot.send_media_group(chat_id=channel_id, media=media)
            else:
                raise e

    end_message = "<b>End of listings.</b>\n\n"
    await bot.send_message(chat_id=channel_id, text=end_message, parse_mode='HTML')

def main() -> None:
    """Start the bot."""
    print("Starting the bot...")
    try:
        application = Application.builder().token(bot_token).build()

        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("listings", get_listings, filters=filters.Regex(r'^\/listings (.+)$')))

        print("Bot is running successfully!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        print(f"An error occurred while starting the bot: {str(e)}") 

if __name__ == "__main__":
    main()