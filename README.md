# BlackJackBot

The `BlackJackBot` class represents a Telegram bot that allows users to play the game of Blackjack. It uses the `python-telegram-bot` library to interact with the Telegram API.

## Installation

## Installation

To use the `BlackJackBot` class, you need to have the following dependencies installed:

- [Pillow](https://pypi.org/project/Pillow/) (version 8.4.0)
- [python-telegram-bot](https://pypi.org/project/python-telegram-bot/) (version 13.11)
- [web3](https://pypi.org/project/web3/) (version 5.31.4)

You can install these dependencies using pip, the package installer for Python. Open your terminal or command prompt and run the following commands:

```bash
pip install Pillow==8.4.0
pip install python-telegram-bot==13.11
pip install web3==5.31.4
```


## Commands

The `BlackJackBot` class provides the following commands for users to interact with the bot:

- `/start21`: Start a new game of Blackjack.
- `/join21`: Join the current game if it is active and has not started yet.
- `/hitme`: Draw an additional card from the deck during your turn.
- `/stand`: End your turn and keep your current hand.
- `/status21`: Display the current status of each player's hand.
- `/help21`: Get instructions on how to play the game.
- `/fix21`: Reset the game state (only available to administrators).

## Game Flow

1. The bot is initialized with a Telegram bot token and sets up the necessary handlers for the commands.
2. Users can start a new game by using the `/start21` command. They can optionally specify the starting chips for the game.
3. Other users can join the game using the `/join21` command before the game starts.
4. Once the game starts, each player takes turns to either draw an additional card (`/hitme`) or end their turn (`/stand`).
5. The bot keeps track of each player's hand and calculates the total value of their cards.
6. If a player's total exceeds 21, they bust and are eliminated from the game.
7. After all players have taken their turns, the bot determines the winners based on the highest total value without exceeding 21.
8. The bot distributes the game tokens to the winners.
9. The game state is reset for the next round.

## Additional Features

The `BlackJackBot` class also includes the following additional features:

- Timer: The bot uses a timer to limit the duration of each player's turn and the time available for joining the game.
- Balance and Allowance Check: The bot checks the user's balance and allowance of PVP tokens before allowing them to join the game.
- Transaction Monitoring: The bot monitors the status of transactions related to the game tokens.
- Admin Functionality: The bot includes an admin command (`/fix21`) to reset the game state, which is only available to administrators.

Please note that some parts of the code are missing, such as the implementation of the `BlackjackGame` class and the `Token` class. You will need to provide the missing code or replace it with your own implementation.

## Deployment
To start the project using Docker Compose, open a terminal and navigate to the directory where the `docker-compose.yml` file is located. Then run the following command:

```shell
docker-compose --build up -d && docker-compose logs -f
```

This command will build the image, start the container in detached mode (`-d`), and run the bot in the background.

To view the logs of the running container, you can use the following command:

```shell
docker-compose logs -f
```

The `-f` flag allows you to follow the logs in real-time.

Please note that you need to have Docker and Docker Compose installed on your machine for this to work.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.