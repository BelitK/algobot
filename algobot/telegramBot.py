from telegram.ext import Updater, CommandHandler
from datetime import datetime

from enums import LONG, SHORT


class TelegramBot:
    def __init__(self, gui, apiKey):
        self.updater = Updater(apiKey, use_context=True)

        # Get the dispatcher to register handlers
        self.gui = gui
        dp = self.updater.dispatcher

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("help", self.help_telegram))
        dp.add_handler(CommandHandler("override", self.override_telegram))
        dp.add_handler(CommandHandler(('stats', 'statistics'), self.get_statistics_telegram))
        dp.add_handler(CommandHandler("forcelong", self.force_long_telegram))
        dp.add_handler(CommandHandler("forceshort", self.force_short_telegram))
        dp.add_handler(CommandHandler('exitposition', self.exit_position_telegram))
        dp.add_handler(CommandHandler(("position", 'getposition'), self.get_position_telegram))

    def start(self):
        # Start the Bot
        self.updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        # self.updater.idle()

    def stop(self):
        self.updater.stop()

    @staticmethod
    def help_telegram(update, context):
        update.message.reply_text("Here are your help commands available:\n"
                                  "/help -> To get commands available.\n"
                                  "/forcelong  -> To force long.\n"
                                  "/forceshort -> To force short.\n"
                                  "/position or /getposition -> To get position.\n"
                                  "/stats or /statistics -> To get current statistics.\n"
                                  "/override -> To exit trade and wait for next cross.\n"
                                  "/exitposition -> To exit position.")

    def get_statistics_telegram(self, update, context):
        trader = self.gui.trader
        startingBalance = trader.startingBalance
        profit = trader.get_profit()
        profitPercentage = trader.startingBalance + profit
        coinName = trader.coinName
        profitLabel = trader.get_profit_or_loss_string(profit=profit)

        update.message.reply_text(f"Here are your statistics:\n"
                                  f'Symbol: {trader.symbol}\n'
                                  f'Position: {trader.get_position_string()}\n'
                                  f'Total trades made: {len(trader.trades)}\n'
                                  f"Coin owned: {trader.coin}\n"
                                  f"Coin owed: {trader.coinOwed}\n"
                                  f"Starting balance: ${round(startingBalance, 2)}\n"
                                  f"Balance: ${round(trader.balance, 2)}\n"
                                  f"{profitLabel}: ${round(abs(profit), 2)}\n"
                                  f'{profitLabel} Percentage: {round(abs(profitPercentage), 2)}%\n'
                                  f'Autonomous Mode: {trader.inHumanControl}\n'
                                  f'Stop Loss: ${round(trader.get_stop_loss(), 2)}\n'
                                  f"Custom Stop Loss: ${trader.customStopLoss}\n"
                                  f"Current {coinName} price: ${trader.dataView.get_current_price()}"
                                  )

    def override_telegram(self, update, context):
        update.message.reply_text("Overriding.")
        self.gui.exit_position(False)
        update.message.reply_text("Successfully overrode.")

    def force_long_telegram(self, update, context):
        position = self.gui.trader.get_position()
        if position == LONG:
            update.message.reply_text("Bot is already in a long position.")
        else:
            update.message.reply_text("Forcing long.")
            self.gui.force_long()
            update.message.reply_text("Successfully forced long.")

    def force_short_telegram(self, update, context):
        position = self.gui.trader.get_position()
        if position == SHORT:
            update.message.reply_text("Bot is already in a short position.")
        else:
            update.message.reply_text("Forcing short.")
            self.gui.force_short()
            update.message.reply_text("Successfully forced short.")

    def exit_position_telegram(self, update, context):
        if self.gui.trader.get_position() is None:
            update.message.reply_text("Bot is not in a position.")
        else:
            update.message.reply_text("Exiting position.")
            self.gui.exit_position(True)
            update.message.reply_text("Successfully exited position.")

    def get_position_telegram(self, update, context):
        position = self.gui.trader.get_position()
        if position == SHORT:
            update.message.reply_text("Bot is currently in a short position.")
        elif position == LONG:
            update.message.reply_text("Bot is currently in a long position.")
        else:
            update.message.reply_text("Bot is currently not in any position.")

