"""
Simple Bot to reply to Telegram messages taken from the python-telegram-bot examples.

Source: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/echobot2.py
"""

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, Application, CallbackContext


class Bot():
    # TODO: move to environment variables
    PORT = 88
    TOKEN = '5177892449:AAFMBN4-Yq6HAyTbgBx66_rXfLru13QM3Yo'

    handlers = []

    def __init__(self):
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    # Define a few command handlers. These usually take the two arguments update and
    # context. Error handlers also receive the raised TelegramError object in error.
    def start(self, update,  context: CallbackContext.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi!')

    def help(self, update,  context: CallbackContext.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def echo(self, update,  context: CallbackContext.DEFAULT_TYPE):
        """Echo the user message."""
        update.message.reply_text(update.message.text)

    def error(self, update,  context: CallbackContext.DEFAULT_TYPE):
        """Log Errors caused by Updates."""
        self.logger.warning('Update "%s" caused error "%s"', update, context.error)

    def run(self):
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        # updater = Updater(self.TOKEN, use_context=True)
        application = Application.builder().token(self.TOKEN).build()

        # Get the dispatcher to register handlers
        # dp = updater.dispatcher
        if not(len(self.handlers)):
            # add default handlers
            application.add_handler(CommandHandler("start", self.start))
            application.add_handler(CommandHandler("help", self.help))
            application.add_handler(MessageHandler(filters.TEXT, self.echo))
        else:
            # add custom handlers
            for h in self.handlers:
                application.add_handler(h[0](**h[1]))

        # application.add_handler(conv_handler)

        # Run the bot until the user presses Ctrl-C
        application.run_polling()

        # log all errors
        # dp.add_error_handler(self.error)

        # Start the Bot
        # updater.start_polling()
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # updater.idle()
