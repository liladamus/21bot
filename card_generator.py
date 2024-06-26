from typing import List

from PIL import Image
import os
import unittest


class Card:
    RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
    SUITS = ['♠️', '♣️', '♦️', '♥️']

    def __init__(self, rank: str, suit: str):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        FACE_CARDS = {'11': 'J', '12': 'Q', '13': 'K', '14': 'A'}
        rank = FACE_CARDS.get(self.rank, self.rank)
        return f'{rank}{self.suit}'

    def format_for_treys(self):
        TREYS_RANKS: str = '23456789TJQKA'
        TREYS_SUITS: str = 'scdh'

        rank_idx = self.RANKS.index(self.rank)
        suit_ids = self.SUITS.index(self.suit)

        treys_rank = TREYS_RANKS[rank_idx]
        treys_suit = TREYS_SUITS[suit_ids]

        return treys_rank + treys_suit

    def to_dict(self):
        return {
            'rank': self.rank,
            'suit': self.suit,
        }


def card_notation_to_file(card: Card):
    value = card.rank
    suit = card.suit

    if value == "14":
        value = "ace"
    elif value == "13":
        value = "king"
    elif value == "12":
        value = "queen"
    elif value == "11":
        value = "jack"

    if suit == '♠️':
        suit = "spades"
    elif suit == '♥️':
        suit = "hearts"
    elif suit == '♦️':
        suit = "diamonds"
    elif suit == '♣️':
        suit = "clubs"
    else:
        raise ValueError("Invalid card suit")

    return f"{value}_of_{suit}.png"


def generate_card_image_public(cards: List[Card], file_name: str):
    CARD_WIDTH = 100  # Adjust as per your images
    CARD_HEIGHT = 200  # Adjust as per your images

    result = Image.new("RGB", (CARD_WIDTH * len(cards), CARD_HEIGHT))

    for i, card in enumerate(cards):
        card_file = card_notation_to_file(card)
        card_image_path = os.path.join(os.getcwd(), "card-images",
                                       card_file)  # Assuming card images are in a folder named "card-images"
        image = Image.open(card_image_path)
        result.paste(image, (i * CARD_WIDTH, 0))

    # Save the image to a file with the provided file name in the current directory
    image_path = os.path.join(os.getcwd(), file_name)
    result.save(image_path)

    return image_path



def generate_card_image(cards: List[Card]):
    CARD_WIDTH = 100  # Adjust as per your images
    CARD_HEIGHT = 200  # Adjust as per your images

    result = Image.new("RGB", (CARD_WIDTH * len(cards), CARD_HEIGHT))

    for i, card in enumerate(cards):
        card_file = card_notation_to_file(card)
        card_image_path = os.path.join(os.getcwd(), "card-images",
                                       card_file)  # Assuming card images are in a folder named "card-images"
        image = Image.open(card_image_path)
        result.paste(image, (i * CARD_WIDTH, 0))

    return result




class TestGenerateCardImage(unittest.TestCase):
    def setUp(self):
        self.cards = [Card(rank, suit) for rank in Card.RANKS for suit in Card.SUITS]
        self.hand = [Card('2', '♠️'), Card('3', '♠️')]
        self.flop = [Card('14', '♠️'), Card('13', '♠️'), Card('12', '♠️')]
        self.five_cards = [Card('14', '♠️'), Card('7', '♠️'), Card('7', '♠️'), Card('11', '♠️'), Card('10', '♠️')]

    def test_generate_card_image(self):
        image = generate_card_image(self.cards)
        image2 = generate_card_image(self.hand)
        image3 = generate_card_image(self.flop)
        image4 = generate_card_image(self.five_cards)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(image.size, (100 * len(self.cards), 200))

        # Save the image to a file named "cards" in the current directory
        image.save(os.path.join(os.getcwd(), 'cards.png'))
        image2.save(os.path.join(os.getcwd(), 'hand.png'))
        image3.save(os.path.join(os.getcwd(), 'flop.png'))
        image4.save(os.path.join(os.getcwd(), 'five_cards.png'))



if __name__ == '__main__':
    unittest.main()