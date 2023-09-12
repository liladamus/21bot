# Token Module

This module provides functionality for interacting with a token contract on the Ethereum blockchain. It includes methods for initializing the module, checking transaction confirmation, aborting games, getting token balances and allowances, starting and ending games, and monitoring transactions.

## Installation

To use this module, you need to have the following dependencies installed:

- Python 3.x
- `sqlite3` library
- `web3` library

You can install the required dependencies using pip:

```
pip install sqlite3 web3
```

## Usage

1. Import the `Token` class from the `token` module:

   ```python
   from token import Token
   ```

2. Create an instance of the `Token` class:

   ```python
   token = Token()
   ```

3. Use the available methods to interact with the token contract:

   - `is_tx_confirmed(chat_id)`: Checks whether a given transaction ID has been confirmed.
   - `abort_all_games()`: Aborts all ongoing games.
   - `get_pvp_balance(telegram_id)`: Gets the balance of PvP tokens for a given user.
   - `get_pvp_allowance(telegram_id)`: Gets the allowance of PvP tokens for the game contract.
   - `start_game(player_telegram_ids, starting_chips, chat_id)`: Starts a new game with the specified players and starting chips.
   - `end_game(winners_ids, losers_ids, starting_chips, chat_id)`: Ends a game and distributes the winnings to the winners.
   - `start_monitoring()`: Starts monitoring transactions in the background.

## Configuration

The module requires the following configuration parameters:

- `WEBSOCKET_PROVIDER_URL`: The URL of the WebSocket provider for connecting to the Ethereum network.
- `GAME_CA`: The address of the game contract on the Ethereum network.
- `PVP_CA`: The address of the PvP contract on the Ethereum network.
- `BOT_ADDRESS`: The address of the bot's wallet.
- `BOT_PRIVATE_KEY`: The private key of the bot's wallet.
- `CHAIN_ID`: The chain ID of the Ethereum network.
- `GAS_LIMIT`: The gas limit for transactions.
- `GAS_ADJUSTMENT`: The gas adjustment factor for adjusting the gas price.
- `BLOCK_SCANNER`: The URL of the block scanner for viewing transaction details.

Make sure to update these configuration parameters before using the module.

## Database

The module uses an SQLite database to store user secrets. The `user_secrets.db` file will be created automatically if it doesn't exist. The `user_secrets` table stores the user ID, secret, and wallet address.

## License

This module is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.