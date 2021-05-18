import numpy as np
import pandas as pd
import copy
from collections import Counter
from house_rules import HouseRules


class BJCalc:
    master = {}

    def __init__(self, r=HouseRules(), cards=None, cards_composition=None, player_cards=None, dealer_cards=None,
                 depth=1):
        if cards and cards_composition:
            raise ValueError('cards and cards_composition must not be both filled')
        self.r = r
        self.depth = depth
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
        try:
            prob[10] = (card_composition[10] + card_composition[11] + card_composition[12] + card_composition[
                13]) / total_cards
        except KeyError:
            prob[10] = card_composition[10] / total_cards

        return prob

    # only working with cards 1 to 10
    # trying to generate sets representing the combination of cards discarded
    def generate_discarded_cards(self):
        discarded_cards = []
        for i in range(1, self.depth + 1):
            temp_cards = []
            for j in range(10 ** i):
                temp_cards.append([int(d) + 1 for d in str(j).zfill(i)])
            temp_cards = [set(item) for item in set(frozenset(item) for item in temp_cards)]
            discarded_cards += temp_cards
        return discarded_cards

    def generate_probabilites(self, discarded_cards):
        d = copy.deepcopy(self.cards_composition)
        for i in discarded_cards:
            d[i] -= 1
        return self.probabilities(d)

    def generate_markov_chain_terminal(self, p):
        '''
        k = [17,18,19,20,"Bust"]
        template = dict(zip(k,[0,]*5))
        hard = dict(zip(range(2, 32), [template, ] * 30))
        soft = dict(zip(range(11, 32), [template, ] * 21))
        for i in range(31, 16, -1):
            if i > 21:
                hard[i]["Bust"] = 1
            else:
                hard[i][i] = 1
        for i in range(31, 26, -1):
            soft[i][i-10] = 1
        for i in range(16, 12, -1):
            for j in k:
        '''
        v = np.array(p.values)
        k = [17, 18, 19, 20, "Bust"]
        hard = pd.DataFrame(0, index=k, columns=range(2, 32))
        soft = pd.DataFrame(0, index=k, columns=range(11, 32))
        if min(p.values) <= 0:
            return {"hard": hard, "soft": soft}
        # a faster way of indexing would be very helpful
        for i in range(31, 16, -1):
            if i < 21:
                hard[i]["Bust"] = 1
            else:
                hard[i][i] = 1
        for i in range(31, 26, -1):
            soft[i][i-10] = 1


    def generate_probabilites_all(self):
        disc = self.generate_discarded_cards()
        for i in disc:
            self.master[i] = {}
            self.master[i]["p"] = self.generate_probabilites(i)
        for i in range(self.depth, 0, -1):
            pass
