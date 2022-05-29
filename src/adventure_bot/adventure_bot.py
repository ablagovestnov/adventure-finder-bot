from typing import Dict

from telegram.constants import ParseMode

from src.bot.bot import Bot
from src.services.location import LocationService
from typing import Dict

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters, CallbackQueryHandler,
)

class AdventureBot(Bot):
    CHOOSING, TYPING_REPLY, TYPING_CHOICE, FILTER_CHOICE = range(4)
    FILTER_MESSAGES = {
        'По сеттингу': {
            'greetings': 'Хорошо! Сейчас заявлены игры в следующих игровых сеттингах:',
            'failure': 'К сожалению игровых стеттингов не нашлось',
            'dict': 'setting',
            'filter_name': 'Сеттинг',
        },
        'По мастеру': {
            'greetings': 'Отлично! Следующие ведущих сейчас проводят игры:',
            'failure': 'К сожалению ведущих не нашлось',
            'dict': 'master',
            'filter_name': 'Мастер',
        },
        'По системе': {
            'greetings': 'Прекрасно! На сегодняшний день заявлены следующие игровые системы:',
            'failure': 'К сожалению игровых систем не нашлось',
            'dict': 'system',
            'filter_name': 'Система',
        },
        'По жанру': {
            'greetings': 'Шикарно! Сейчас есть игры следующих жанров:',
            'failure': 'К сожалению нет игр с указанным жанром',
            'dict': 'genre',
            'filter_name': 'Жанр',
        },
    }
    reply_keyboard = [
        # ["Игры сегодня", "Игры завтра"],
        ["Все игры"],
        # ["Поискать по фильтру"],
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    locationService = LocationService()

    def facts_to_str(self, user_data: Dict[str, str]) -> str:
        """Helper function for formatting the gathered user info."""
        facts = [f"{key} - {value}" for key, value in user_data.items()]
        return "\n".join(facts).join(["\n", "\n"])

    async def start(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        """Start the conversation and ask user for input."""
        reply_keyboard = [
            ["Все игры"],
            ["По системе", "По жанру", "По сеттингу", "По мастеру"],
        ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await update.message.reply_text(
            "Привет! Я Поисковик Приключений!"
            "Я помогу тебе посмотреть, какие игры есть на этой неделе в клубе Локаций"
            "Посмотрим? Выбери, что хочешь узнать",
            reply_markup=markup,
        )
        return self.CHOOSING

    async def regular_choice(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text
        context.user_data["choice"] = text
        await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")

        return self.TYPING_REPLY

    async def today_choice(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text
        print('Incoming today', text)
        context.user_data["choice"] = text
        await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")

        return self.TYPING_REPLY

    async def tomorrow_choice(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text

        print('Incoming tomorrow', text)
        context.user_data["choice"] = text
        await update.message.reply_text(f"Your {text.lower()}? Yes, I would love to hear about that!")

        return self.TYPING_REPLY

    def split_array(self, seq, num):
        avg = len(seq) / float(num)
        out = []
        last = 0.0

        while last < len(seq):
            out.append(seq[int(last):int(last + avg)])
            last += avg

        return out

    def get_html_card(self, game):
        return f"""
                    \n
                    <b>{game.get('title')}</b> 
                    {game.get('time') or ' - '}\n
                    <i>Сеттинг:</i> {game.get('setting') or ' - '}
                    <i>Система:</i> {game.get('system') or ' - '}
                    <i>Программа:</i> {game.get('program') or ' - '}
                    <i>Игру проводит:</i> {game.get('master') or ' - '}
                    <i>Места:</i> {game.get('seats') or ' - '}
                    <a href='{game.get('url')}'>Ссылка на игру</a>
                    """

    async def all_choice(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text

        context.user_data["choice"] = text
        for game in self.locationService.games:
            await update.message.reply_text(
                self.get_html_card(game),
                ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Подробнее об игре...", callback_data='id::'+game.get('id'))],
                ])
            )
        return self.CHOOSING

    async def unknown_command(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        """Ask the user for info about the selected predefined choice."""
        text = update.message.text

        context.user_data["choice"] = text
        await update.message.reply_text(
            'Не понятно - воспользуйся лучше кнопками'
        )
        return self.CHOOSING

    async def filter_item_choice(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        if not(update.message.text) or not(self.FILTER_MESSAGES.get(update.message.text)):
            await update.message.reply_text('Что-то непонятное, пропробуем еще раз')
            return self.CHOOSING

        filter_settings = self.FILTER_MESSAGES.get(update.message.text)
        options = []
        d = self.locationService.dicts.get(filter_settings.get('dict'))
        if d:
            for key in d:
                options.append(InlineKeyboardButton(d.get(key), callback_data=str(filter_settings.get('dict')) + '::' + str(key)))
            await update.message.reply_text(
                filter_settings.get('greetings'),
                reply_markup=InlineKeyboardMarkup([[button] for button in options])
            )
            return self.CHOOSING

        await update.message.reply_text(filter_settings.get('failure'))
        return self.CHOOSING


    async def filter_apply(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        [prop, value] = str(query['data']).split('::')
        for game in list(filter(lambda g: g.get(prop) == self.locationService.dicts.get(prop).get(value), self.locationService.games)):
            await query.message.reply_text(
                self.get_html_card(game),
                ParseMode.HTML,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Подробнее об игре...", callback_data='id::'+game.get('id'))],
                ])
            )
        return self.CHOOSING

    async def show_game_description(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        [prop, value] = str(query['data']).split('::')
        game = list(filter(lambda g: g.get(prop) == value, self.locationService.games)).pop()
        if game:
            img = game.get('img')
            if img:
                await query.message.reply_photo(
                    photo=game.get('img'),
                    caption=game.get('description')[0:1024] + '...' if game.get('description') else ''
                )
            else:
                await query.message.reply_text(
                    game.get('description')[0:1024] + '...' if game.get('description') else '',
                    ParseMode.HTML,
                    disable_web_page_preview=True,
                )
        return self.CHOOSING


    async def received_information(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        """Store info provided by user and ask for the next category."""
        user_data = context.user_data
        text = update.message.text
        category = user_data["choice"]
        user_data[category] = text
        del user_data["choice"]

        await update.message.reply_text(
            "Neat! Just so you know, this is what you already told me:"
            f"{self.facts_to_str(user_data)}You can tell me more, or change your opinion"
            " on something.",
            reply_markup=self.markup,
        )

        return self.CHOOSING

    async def done(self, update: Update, context: CallbackContext.DEFAULT_TYPE) -> int:
        await update.message.reply_text(
            f"До встречи! приятной игры!!",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    async def help(self, update,  context: CallbackContext.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        await update.message.reply_text(
            f"""
            Доступные команды бота: \n
            /start - запуск/перезапуск бота
            /help - получение информации
            /about - описание бота
            /done - завершение работы
            """
        )

    def __init__(self):
        self.handlers += [
            (
                ConversationHandler,
                {
                    'entry_points': [CommandHandler("start", self.start)],
                    'states': {
                        self.CHOOSING: [
                            MessageHandler(
                                filters.Regex("^Все игры"), self.all_choice
                            ),
                            MessageHandler(
                                filters.Regex("^(По системе|По жанру|По мастеру|По сеттингу)"), self.filter_item_choice
                            ),

                            MessageHandler(
                                filters.TEXT & ~filters.COMMAND, self.unknown_command
                            ),
                            CallbackQueryHandler(self.filter_apply, pattern="^(system::|setting::|genre::|master::)"),
                            CallbackQueryHandler(self.show_game_description, pattern="^id::"),
                        ],
                        self.FILTER_CHOICE: [
                            CallbackQueryHandler(self.filter_apply, pattern="^(system::|setting::|genre::|master::)"),
                        ],
                        self.TYPING_CHOICE: [
                            MessageHandler(
                                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                                self.regular_choice
                            ),
                        ],
                        self.TYPING_REPLY: [
                            MessageHandler(
                                filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                                self.received_information,
                            ),
                            CallbackQueryHandler(self.filter_apply, pattern="^(system::|genre::|master::|program::)$"),

                        ],
                    },
                    'fallbacks': [
                        CommandHandler("help", self.help),
                        CommandHandler("done", self.done),
                        MessageHandler(filters.Regex("^Done$"), self.done),
                    ],
                }
            ),

        ]
        super().__init__()
