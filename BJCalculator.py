import numpy as np
from collections import Counter
from house_rules import HouseRules


class BJCalc:
    def __init__(self, r=HouseRules(), cards=None, cards_composition=None, player_cards=None, dealer_cards=None):
        if cards and cards_composition:
            raise ValueError('cards and cards_composition must not be both filled')
        self.r = r
        if cards:
            self.cards = cards
            self.cards_composition = Counter(cards.cards)
        if cards_composition:
            self.cards_composition = cards_composition

    # calculating probabilities using dictionaries
    @staticmethod
    def probabilities(card_composition):
        total_cards = sum(card_composition.values())
        prob = {}
        for i in range(1, 10):
            prob[i] = card_composition[i] / total_cards
        prob[10] = (card_composition[10]+card_composition[11]+card_composition[12]+card_composition[13])/total_cards
        return prob
