import random


class Card:
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    SUITS = ['♠️', '♣️', '♦️', '♥️']

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f'{self.rank}{self.suit}'

    def to_dict(self):
        return {
            'rank': self.rank,
            'suit': self.suit,
        }


class Player:
    def __init__(self, telegram_id: str, name: str):
        self.telegram_id = telegram_id
        self.hand = []
        self.name = name
        self.has_busted = False
        self.has_stood = False

    def __repr__(self):
        return f'{self.name}'

    def to_dict(self):
        return {
            'name': self.name,
            'hand': self.hand,
            'telegram_id': self.telegram_id,
        }


class BlackjackGame:
    def __init__(self):
        self.players: list[Player] = []  # List of Player instances
        self.cards = self._initialize_deck()
        self.hands = {}  # Dictionary with Player instance as key and list of cards as value
        self.is_game_active = False
        self.has_game_started = False
        self.current_player = None
        self.starting_chips = 1000

    def bust_player(self, player):
        player.has_busted = True

    def is_player_part_of_game(self, player_id):
        return any(player.telegram_id == player_id for player in self.players)

    def _initialize_deck(self):
        suits = Card.SUITS
        values = Card.RANKS
        return [Card(value, suit) for suit in suits for value in values]

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def get_player(self, player_id):
        for player in self.players:
            if player.telegram_id == player_id:
                return player

    def calculate_total(self, player_id):
        player = self.get_player(player_id)
        total = 0
        aces = 0
        for card in player.hand:
            if card.rank in ['J', 'Q', 'K']:
                total += 10
            elif card.rank == 'A':
                total += 11
                aces += 1
            else:
                total += int(card.rank)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def add_player(self, player_id, player_name):
        if not self.is_player_part_of_game(player_id):
            player = Player(player_id, player_name)
            self.players.append(player)
            return player

    def player_hit(self, player):
        card = self.cards.pop()
        player.hand.append(card)
        return card

    def player_stand(self, player):
        player.has_stood = True

    def next_player(self):
        if not self.current_player:
            self.current_player = self.players[0]
        else:
            current_index = self.players.index(self.current_player)
            next_index = (current_index + 1) % len(self.players)
            while next_index != current_index:
                if not self.players[next_index].has_stood and not self.players[next_index].has_busted:
                    self.current_player = self.players[next_index]
                    break
                next_index = (next_index + 1) % len(self.players)
            else:
                # If no valid next player is found, allow the current player to play again
                if not self.current_player.has_stood and not self.current_player.has_busted:
                    self.current_player = self.current_player
                else:
                    self.current_player = None
        return self.current_player

    def determine_winners(self):
        print(self.players)
        player_totals = {player: self.calculate_total(player.telegram_id) for player in self.players if
                         not player.has_busted}
        if len(player_totals.values()) == 0:
            return []
        max_total = max(player_totals.values())
        winners = [player for player, total in player_totals.items() if total == max_total and total <= 21]
        return winners

    def reset_game(self):
        self.players = []
        self.cards = self._initialize_deck()
        self.hands = {}
        self.is_game_active = False
        self.has_game_started = False
        self.current_player = None

    def deal_initial_cards(self):
        for player in self.players:
            player.hand = [self.cards.pop(), self.cards.pop()]
        return self.hands

    def start_new_game(self):
        self.shuffle_deck()
        self.deal_initial_cards()
