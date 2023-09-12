# token.py
import sqlite3
from web3 import Web3
from .constants import *
import threading
import time


class Token:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls is FakeToken:
            return object.__new__(cls)
        if args and args[0] == "FAKE":
            print('wood wood')
            return FakeToken(*args, **kwargs)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Initialize the SQLite database connection and create the table if it doesn't exist
        conn = sqlite3.connect('user_secrets.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_secrets (
                user_id INTEGER PRIMARY KEY,
                secret TEXT,
                wallet_address TEXT
            )
        ''')
        conn.commit()
        conn.close()

        # Set up Web3 instance and contract
        self.w3 = Web3(Web3.HTTPProvider(WEBSOCKET_PROVIDER_URL))
        self.gamecontract = self.w3.eth.contract(address=GAME_CA, abi=GAME_ABI)
        self.pvpcontract = self.w3.eth.contract(address=PVP_CA, abi=PVP_ABI)

        # Start monitoring transactions
        self.start_monitoring()

    def get_wallet_address(self, user_id):
        conn = sqlite3.connect('user_secrets.db')
        cursor = conn.cursor()
        cursor.execute('SELECT wallet_address FROM user_secrets WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def is_tx_confirmed(self, chat_id):
        """
        Checks whether a given transaction ID has been confirmed.
        """
        tx_data = self.game_transactions.get(chat_id, {})
        if tx_data.get('confirmed'):
            # Replace 'tx_scan_link' with the actual key for the transaction scan link in your data structure
            return Token._generate_scan_link(tx_data['tx_hash'])
        else:
            return None  # or any other falsy value you prefer

    def abort_all_games(self):
        function_data = self.gamecontract.encodeABI(fn_name='abortAllGames', args=[False])

        nonce = self.w3.eth.get_transaction_count(BOT_ADDRESS)
        suggested_gas_price = self.w3.eth.gas_price
        gas_price_factor = 2.5
        adjusted_gas_price = int(suggested_gas_price * gas_price_factor)

        transaction = {
            'chainId': CHAIN_ID,
            'gas': GAS_LIMIT,
            'gasPrice': adjusted_gas_price,
            'nonce': nonce,
            'to': GAME_CA,
            'data': function_data
        }

        # Sign the transaction
        private_key = BOT_PRIVATE_KEY
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction using Infura
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Format the transaction hash for Etherscan link
        tx_hash_formatted = tx_hash.hex()
        return Token._generate_scan_link(tx_hash_formatted)

    def get_pvp_balance(self, telegram_id):
        wallet_address = self.get_wallet_address(telegram_id)
        pvp_balance_wei = self.pvpcontract.functions.balanceOf(wallet_address).call()
        pvp_balance_eth = self.w3.from_wei(pvp_balance_wei, 'ether')
        return pvp_balance_eth

    def get_pvp_allowance(self, telegram_id):
        wallet_address = self.get_wallet_address(telegram_id)
        pvp_allowance_wei = self.pvpcontract.functions.allowance(wallet_address, GAME_CA).call()
        pvp_allowance_eth = self.w3.from_wei(pvp_allowance_wei, 'ether')
        return pvp_allowance_eth

    def start_game(self, player_telegram_ids, starting_chips, chat_id):
        player_addresses = [self.get_wallet_address(telegram_id) for telegram_id in player_telegram_ids]

        ## Construct player bets in wei
        player_bets_wei = [starting_chips * 10 ** 18] * len(player_telegram_ids)

        # Construct the transaction data for the newGame function
        function_data = self.gamecontract.encodeABI(
            fn_name='newGame',
            args=[chat_id, 1, player_addresses, player_bets_wei, False]
        )

        # Get the nonce and suggested gas price
        nonce = self.w3.eth.get_transaction_count(BOT_ADDRESS)
        suggested_gas_price = self.w3.eth.gas_price

        # Set up the transaction parameters
        transaction = {
            'chainId': CHAIN_ID,  # Mainnet chain ID
            'gas': GAS_LIMIT,
            'gasPrice': suggested_gas_price,
            'nonce': nonce,
            'to': GAME_CA,
            'data': function_data
        }

        # Sign the transaction
        private_key = BOT_PRIVATE_KEY
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction using Infura
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Format the transaction hash for Etherscan link
        tx_hash_formatted = tx_hash.hex()

        self.game_transactions[chat_id] = {
            'tx_hash': tx_hash_formatted,
            'confirmed': False
        }

        return Token._generate_scan_link(tx_hash_formatted)

    def end_game(self, winners_ids, losers_ids, starting_chips, chat_id):
        # Get addresses of all players
        winner_addresses = [self.get_wallet_address(winner.telegram_id) for winner in winners_ids]
        loser_addresses = [self.get_wallet_address(loser.telegram_id) for loser in losers_ids]

        total_players = len(winner_addresses) + len(loser_addresses)
        total_chips = starting_chips * total_players

        # Conversion rate from game's chip unit to wei
        chip_to_wei_conversion = 10 ** 18  # Assuming 1 chip = 1e9 wei

        # Convert winner's and loser's chips to wei
        winner_chips_wei = (total_chips // len(winner_addresses)) * chip_to_wei_conversion
        loser_chips_wei = (total_chips // len(loser_addresses)) * chip_to_wei_conversion

        # Construct the transaction data for the endGame function
        # boolet todo: make the contract work with list of winners and losers and update ABI
        function_data = self.gamecontract.encodeABI(
            fn_name='endGame',
            args=[
                chat_id,
                winner_addresses,  # Address of the winner
                loser_addresses,  # Address of the loser
                winner_chips_wei,  # Chips won by the winners (to be sent to each winner's address)
                loser_chips_wei,
                False  # Unused chips to be returned to loser's address
            ]
        )

        # Get nonce and suggested gas price
        nonce = self.w3.eth.get_transaction_count(BOT_ADDRESS)
        suggested_gas_price = self.w3.eth.gas_price

        # Set up the transaction parameters
        transaction = {
            'chainId': CHAIN_ID,
            'gas': GAS_LIMIT,
            'gasPrice': int(suggested_gas_price * GAS_ADJUSTMENT),  # Adjusted gas price
            'nonce': nonce,
            'to': GAME_CA,
            'data': function_data
        }

        # Sign the transaction
        private_key = BOT_PRIVATE_KEY
        signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction using Web3
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Format the transaction hash for Etherscan link
        tx_hash_formatted = tx_hash.hex()

        self.game_transactions[chat_id] = {
            'tx_hash': tx_hash_formatted,
            'confirmed': False
        }

        return Token._generate_scan_link(tx_hash_formatted)

    def start_monitoring(self):
        """
        Starts a background thread to monitor transactions.
        """
        self.game_transactions = {}
        threading.Thread(target=self._monitor_transactions).start()

    @staticmethod
    def _generate_scan_link(tx_hash):
        return f"https://{BLOCK_SCANNER}/tx/{tx_hash}"

    def _monitor_transactions(self):
        while True:
            # Get the latest block number
            latest_block = self.w3.eth.block_number

            # Check all pending transactions
            for chat_id, tx_info in self.game_transactions.items():
                tx_hash = tx_info['hash']
                tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)

                if tx_receipt is not None:
                    # Transaction has been mined
                    status = tx_receipt['status']
                    if status == 1:
                        # Transaction successful
                        self.game_transactions[chat_id]['confirmed'] = True
                    else:
                        # Transaction failed
                        self.game_transactions[chat_id]['confirmed'] = False

            # Remove confirmed transactions from the dictionary
            # optional todo: remove transactions that have been pending for too long and are unlikely to be confirmed
            # optional todo: remove transactions of the games that have been aborted
            # optional todo: remove transactions of the games that have been ended
            # self.game_transactions = {chat_id: tx_info for chat_id, tx_info in self.game_transactions.items() if
            #                           not tx_info['confirmed']}

            # Sleep for 5 seconds before checking again
            time.sleep(5)


class FakeToken(Token):
    def _initialize(self):
        # Fake initialization
        pass

    def get_wallet_address(self, user_id):
        # Fake implementation
        return "FAKE_WALLET_ADDRESS"

    def is_tx_confirmed(self, chat_id):
        # Fake implementation
        return 'https://etherscan.io/tx/FAKE_TX_HASH'

    def abort_all_games(self):
        # Fake implementation
        return 'https://etherscan.io/tx/FAKE_TX_HASH'

    def get_pvp_balance(self, telegram_id):
        # Fake implementation
        return 1000001

    def get_pvp_allowance(self, telegram_id):
        # Fake implementation
        return 1000001

    def start_game(self, player_telegram_ids, starting_chips, chat_id):
        # Fake implementation
        return "FAKE_TX_HASH"

    def end_game(self, winners_ids, losers_ids, starting_chips, chat_id):
        # Fake implementation
        return "FAKE_TX_HASH"

    def start_monitoring(self):
        # Fake implementation
        pass

    @staticmethod
    def _generate_scan_link(tx_hash):
        # Fake implementation
        return "FAKE_SCAN_LINK"
