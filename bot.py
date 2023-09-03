import telegram.ext
from process import ask, append_interaction_to_chat_log
import logging, os
import openai
import prompts

PORT = int(os.environ.get('PORT', '8443'))
with open('token.txt', 'r') as f:
    TOKEN = str(f.read())
print(PORT)
session = {}

if "chat_log" not in session:
    session['chat_log'] = []


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text("Hello! Welcome to CometBot")


def help(update, context):
    update.message.reply_text("""
    The Following commands are available:
    /start -> Welcome to Comet
    /help ->This Message
    /about -> About CometBot
    /contact -> Developer Info
    /company -> Company Info
    /clear -> Clear Message History
    """)

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', context)


def about(update, context):
    update.message.reply_text("""
            CometBot is not just a chatbot. It's so much more than that. It's an AI-enabled customer service solution that answers your questions, responds to your tweets, and helps you find the products you're looking for. CometBot has the power to save you time, increase your sales, and make your customer service operation more efficient.
        """)


def contact(update, context):
    update.message.reply_text("Developer: Kazuki Ito \n email: comet1407@hotmail.com\n")

def company(update, context):
    update.message.reply_text("Company: Comet Information Tech Co., LTd\n Email: comet1407@hotmail.com \n Phone Number: +6811111111 \n Address: Hino Kaido street, Hino City, Tokyo, Japan")

def handle_message(update, context):
    answer = generate_response(update.message.text)
    update.message.reply_text(f"{str(answer)}")

def generate_response(text):
    session['chat_log'].append({
        "message": text,
        "is_user": True
    })

    # search_results = semantic_search(text, index, top_k=3)
    messages = construct_messages(session['chat_log'], text)
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    bot_response = response["choices"][0]["message"]["content"]
    print("bot_response------------: ", bot_response)
    session["chat_log"].append({
        "message": bot_response,
        "is_user": False
    })
    return bot_response

def construct_messages(history, text):
    messages = [{"role": "system", "content": prompts.system_message}]
    # messages = [];
    for entry in history:
        role = "user" if entry["is_user"] else "assistant"
        messages.append({"role": role, "content": entry["message"]})
    return messages

def main():
    updater = telegram.ext.Updater(TOKEN, use_context=True)
    bot = updater.dispatcher

    bot.add_handler(telegram.ext.CommandHandler("start", start))
    bot.add_handler(telegram.ext.CommandHandler("help", help))
    bot.add_handler(telegram.ext.CommandHandler("about", about))
    bot.add_handler(telegram.ext.CommandHandler("contact", contact))
    bot.add_handler(telegram.ext.CommandHandler("company", company))
    bot.add_handler(telegram.ext.MessageHandler(
    telegram.ext.Filters.text, handle_message))

    bot.add_error_handler(error)
    updater.start_polling()

    updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=TOKEN,
        webhook_url='https://web3taskbot.herokuapp.com/' + TOKEN
    )

    updater.idle()


if __name__ == '__main__':
    main()
