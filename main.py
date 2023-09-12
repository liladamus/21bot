import os
import threading
from pvp.pvptoken import Token

from telegram.ext import Updater, CommandHandler
from game_logic import BlackjackGame
import time

START_GAME_TIMER = 20  # 20 seconds
JOIN_GAME_TIMER = 20  # 20 seconds
TURN_TIMER = 30  # 30 seconds


class BlackJackBot:
    def __init__(self, token):
        self.updater = Updater(token=token, use_context=True)
        self.game = BlackjackGame()
        self._register_handlers()
        self.timer = None  # Timer variable
        self.token = Token("FAKE")  # boolet todo: remove "FAKE" when token is ready

    def _register_handlers(self):
        dp = self.updater.dispatcher
        dp.add_handler(CommandHandler('start21', self.start_blackjack))
        dp.add_handler(CommandHandler('join21', self.join_blackjack))
        dp.add_handler(CommandHandler('hitme', self.hitme))
        dp.add_handler(CommandHandler('stand', self.stand))
        dp.add_handler(CommandHandler('status21', self.status))
        dp.add_handler(CommandHandler('help21', self.help))
        dp.add_handler(CommandHandler('fix21', self.fix))

    def reset(self, update, context):
        self.timer = None
        self.game.reset_game()

    def fix(self, update, context):
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id

        # Get the list of administrators for the group
        administrators = context.bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in administrators]

        if user_id in admin_ids:
            tx = self.token.abort_all_games()
            self.reset(update, context)
            update.message.reply_text(f'Game state has been reset. \n\n'
                                      f'Transaction details: {tx}')
        else:
            update.message.reply_text('You are not an admin.')

    def help(self, update, context):
        update.message.reply_text("Welcome to Blackjack!\n\n"
                                  "To play the game, use the following commands:\n"
                                  "/start21 - Start a new game of Blackjack.\n"
                                  "/join21 - Join the current game if it is active and has not started yet.\n"
                                  "/hitme - Draw an additional card from the deck during your turn.\n"
                                  "/stand - End your turn and keep your current hand.\n"
                                  "/status21 - Display the current status of each player's hand.\n"
                                  "/help21 - Get instructions on how to play the game.")

    def _check_balance_and_allowance(self, telegram_id, update, context):
        # check if wallet address is registered
        if not self.token.get_wallet_address(telegram_id):
            update.message.reply_text(
                f'You need to connect your wallet using /connect@pvp_casinobot')
            return False
        balance = self.token.get_pvp_balance(telegram_id)
        allowance = self.token.get_pvp_allowance(telegram_id)
        if balance < self.game.starting_chips:
            update.message.reply_text(
                f'You don\'t have enough PVP tokens to join the game.')
            return False
        elif allowance < self.game.starting_chips:
            update.message.reply_text(
                f'You need to approve PVP tokens for the Poker Contract, please visit https://pvpcasino.io and click '
                f'Approve PVP BlackJack to simplify the process.')
            return False
        else:
            return True

    def _handle_start_game_tokens(self, update, context):
        # Send the tokens to the contract
        tx_hash = self.token.start_game([player.telegram_id for player in self.game.players],
                                        self.game.starting_chips,
                                        update.effective_chat.id)
        if tx_hash:
            update.message.reply_text(
                f'Setting up the table, please be patient...')
            # Start a thread to monitor the transaction
            threading.Thread(target=self._monitor_transactions, args=(update, context),
                             kwargs={'mode': 'start'}).start()
        else:
            update.message.reply_text(
                f'Error sending the game starting tokens to the contract. Please try again later.')

    def _handle_end_game_tokens(self, update, context):
        winner_ids = [winner.telegram_id for winner in self.game.determine_winners()]
        loser_ids = [player.telegram_id for player in self.game.players if player.telegram_id not in winner_ids]
        # Send the tokens to the contract
        tx_hash = self.token.end_game(winner_ids, loser_ids, self.game.starting_chips, update.effective_chat.id)
        if tx_hash:
            update.message.reply_text(
                f'Sending the game tokens to the winners, please be patient...')
            # Start a thread to monitor the transaction
            threading.Thread(target=self._monitor_transactions, args=(update, context),
                             kwargs={'mode': 'end'}).start()
        else:
            update.message.reply_text(
                f'Error sending the game tokens to the winners. Please try again later.')

    def _monitor_transactions(self, update, context, mode="start"):
        # check if tx is confirmed
        while True:
            tx = self.token.is_tx_confirmed(update.effective_chat.id)
            if tx:
                if mode == "start":
                    self.begin_game(update, context, tx)
                if mode == "end":
                    self.endgame(update, context, tx)
                break
            time.sleep(5)

    def start_blackjack(self, update, context):
        if not self.game.is_game_active:
            self.game.starting_chips = int(context.args[0]) if context.args else 1000
            if not self._check_balance_and_allowance(update.message.from_user.id, update, context):
                return
            self.game.is_game_active = True
            player = self.game.add_player(update.message.from_user.id, update.message.from_user.first_name)
            update.message.reply_text(
                f'{repr(player)} has started a new game of Blackjack! \n'
                f'The bet is {"{:,}".format(self.game.starting_chips)} PVP tokens. \n'
                f'Other players can join by using the command /join21.'
            )
            self.start_timer(START_GAME_TIMER, update, context,
                             caller='start')  # Start the timer with a duration of 1 minute
        else:
            update.message.reply_text(
                'A game is already in progress. Please wait for it to finish or join the current game using /join21.')

    def join_blackjack(self, update, context):
        print(update.message.from_user, " join_blackjack")
        user_id = update.message.from_user.id
        if self.game.is_game_active and not self.game.has_game_started:
            if not self.game.is_player_part_of_game(user_id):
                if not self._check_balance_and_allowance(user_id, update, context):
                    return
                player = self.game.add_player(user_id, update.message.from_user.first_name)
                update.message.reply_text(f'Player {repr(player)} has joined the game!')
                self.start_timer(JOIN_GAME_TIMER, update, context, auto_begin=True,
                                 caller='join')  # Start the timer with a duration of 1 minute
            else:
                update.message.reply_text('You are already part of the game.')
        elif self.game.has_game_started:
            update.message.reply_text('The game has already started. Please wait for the next game.')
        else:
            update.message.reply_text('No active game found. Start a new game using /start21')

    def begin_game(self, update, context, scanner_link=None):
        if self.game.is_game_active and not self.game.has_game_started:
            self.game.has_game_started = True
            self.game.start_new_game()
            players = self.game.players
            message = ""
            for player in players:
                message += f"Player {repr(player)} has been dealt: {repr(player.hand)} with total of {self.game.calculate_total(player.telegram_id)}\n"
            message += f"\nTransaction details: {scanner_link}"
            update.message.reply_text(message)
            self.inform_current_player(update, context)
        else:
            update.message.reply_text('No active game found or the game has already started.')

    def inform_current_player(self, update, context):
        current_player = self.game.next_player()
        if current_player:
            update.message.reply_text(f'It is now {repr(current_player)}\'s turn. Please decide to /hitme or /stand.')
            self.start_timer(TURN_TIMER, update, context,
                             caller='inform')  # Start the timer with a duration of 2 minutes
        else:
            update.message.reply_text('All players have taken their turns.')
            self._handle_end_game_tokens(update, context)

    def hitme(self, update, context):
        player = update.message.from_user.id
        if player == self.game.current_player.telegram_id:
            self.stop_timer(update, context)  # Stop the timer when the player takes their turn
            card = self.game.player_hit(self.game.current_player)
            if card:
                total = self.game.calculate_total(player)
                if total > 21:
                    update.message.reply_text(
                        f'{repr(self.game.current_player)} drew {repr(card)}.\n'
                        f'{repr(self.game.current_player)} has busted with a total of {total}!'
                    )
                    self.game.bust_player(self.game.current_player)
                elif total == 21:
                    # send audio file with caption of "BLACKJACK!"
                    update.message.reply_audio(
                        audio=open('BLACKJACK.mp3', 'rb'),
                        caption=f'🃏 BLACKJACK! 🃏\n\n'
                                f'{repr(self.game.current_player)} drew {repr(card)}.\n'
                                f'{repr(self.game.current_player)} has a total of {total}!'
                    )
                    self.game.player_stand(self.game.current_player)
                else:
                    update.message.reply_text(
                        f'{repr(self.game.current_player)} drew {repr(card)}.\n'
                        f'{repr(self.game.current_player)}\'s total is now {total}. Moving to the next player.'
                    )
                self.inform_current_player(update, context)
            else:
                update.message.reply_text('Error drawing card.')
        else:
            update.message.reply_text('It is not your turn.')

    def stand(self, update, context):
        player = update.message.from_user.id
        if player == self.game.current_player.telegram_id:
            self.stop_timer(update, context)  # Stop the timer when the player takes their turn
            total = self.game.calculate_total(player)
            update.message.reply_text(f'{repr(self.game.current_player)} stands with a total of {total}.')
            self.game.player_stand(self.game.current_player)
            self.inform_current_player(update, context)
        else:
            update.message.reply_text('It is not your turn.')

    def status(self, update, context):
        if not self.game.has_game_started:
            update.message.reply_text('The game has not started yet.')
            return
        text = ''
        for player in self.game.players:
            total = self.game.calculate_total(player.telegram_id)
            text = text + f'{repr(player)} has cards: {repr(player.hand)} with a total of {total}. \n'
        update.message.reply_text(text)

    def endgame(self, update, context, tx):
        winners = self.game.determine_winners()
        message = ""
        win_amount = self.game.starting_chips * len(self.game.players) / len(winners) if len(winners) > 0 else 0

        if len(winners) == 1:
            message = f'Game over! The winner is {repr(winners[0])} with a total of {self.game.calculate_total(winners[0].telegram_id)}!'
            message += f'\n{repr(winners[0])} will receive {"{:,}".format(win_amount)} PVP tokens.'
        elif len(winners) == 0:
            message = 'Game over! There are no winners!'
        else:
            winners_str = ', '.join([repr(winner) for winner in winners])
            message = f'Game over! It\'s a tie between: {winners_str} with a total of {self.game.calculate_total(winners[0].telegram_id)}!\n'
            message += f'Each winner will receive {"{:,}".format(win_amount)} PVP tokens.'

        message += f"\nTransaction details: {tx}"
        update.message.reply_text(message)

        # Reset the game state for the next round
        self.reset(update, context)

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def start_timer(self, duration, update, context, auto_begin=False, caller="Nobody"):
        print(f"timer started {duration} seconds - auto_begin: {auto_begin} - caller: {caller}")
        self.stop_timer(update, context)  # Stop any existing timer
        self.timer = threading.Timer(duration, self.handle_timeout, args=(update, context, auto_begin))
        self.timer.start()

    def stop_timer(self, update, context):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def handle_timeout(self, update, context, auto_begin=False):
        current_player = self.game.current_player
        if auto_begin:
            self._handle_start_game_tokens(update, context)
            return
        if current_player:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Time is up for {repr(current_player)}. Moving to the next player.')
            self.game.player_stand(current_player)
            self.inform_current_player(update, context)
            print(f"next player called by handle_timeout")
        elif self.game.is_game_active and not self.game.has_game_started:
            context.bot.send_message(chat_id=update.effective_chat.id, text='Time is up for joining the game. the '
                                                                            'game will reset.')
            self.game.reset_game()


def main():
    # read telegram token from docker compose file
    token = os.environ.get('TELEGRAM_TOKEN')
    bot = BlackJackBot(token)
    bot.run()


if __name__ == "__main__":
    main()
