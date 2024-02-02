import requests
from bs4 import BeautifulSoup
from telegram import ForceReply, Update, InputMediaPhoto
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

bot_token = '6979342574:AAHHQx6Bvj7lghjO4e1fk7rqASfBXFk6N9w'

async def scrape_data():
    url = 'https://qefira.com.et/'
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    listings_container = soup.find('div', class_='hp-listings')
    listings = listings_container.find_all('article', class_='hp-listing')

    data = []
    for listing in listings:
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
            'Image URL': image_url 
        })

    return data


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! use /listings to get recent listings on Qefira",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("use /listings to get recent listings on Qefira")


async def get_listings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    recent_listings = await scrape_data()
    # await update.message.reply_text(recent_listings)
    for listing in recent_listings:
        item = listing['Item']
        added_date = listing['Added Date']
        phone_number = listing['Phone Number']
        price = listing['Price']
        image_url = listing['Image URL']

        # Create a formatted message
        message = f"<b>Item:</b> {item}\n"
        message += f"<b>Added Date:</b> {added_date}\n"
        message += f"<b>Phone Number:</b> {phone_number}\n"
        message += f"<b>Price:</b> {price}"

        # Send the image and formatted message
        media = [InputMediaPhoto(media=image_url, caption=message, parse_mode='HTML')]
        await update.message.reply_media_group(media)


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(bot_token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(CommandHandler("listings", get_listings))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()