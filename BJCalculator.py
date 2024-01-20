import numpy as np
import pandas as pd
import copy
from collections import Counter
from blackjack_calculator.house_rules import HouseRules
from cards import Cards


class BJCalc:
    master = {}
    hard = None
    soft = None
    dealer_prob = None

    def __init__(self, r=HouseRules(), cards=Cards(), cards_composition=None, player_cards=None, dealer_card=None,
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
        self.player_cards = player_cards
        self.dealer_card = dealer_card
        self.dealer_cardval = min(10, dealer_card)
        self.player_cardval = sum(min(i, 10) for i in player_cards)
        self.default_strat = self.generate_markov_chain_terminal({0: 0})

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
        """ method 1, seems wrong
        discarded_cards = []
        for i in range(1, self.depth + 1):
            temp_cards = []
            for j in range(10 ** i):
                temp_cards.append([int(d) + 1 for d in str(j).zfill(i)])
            temp_cards = [set(item) for item in set(frozenset(item) for item in temp_cards)]
            discarded_cards += temp_cards
        return discarded_cards
        """
        # method 2, saving each possible discarded cards as dict, then saving all in a list
        discarded_cards = []
        temp_cards = []
        template = dict(zip(range(1, 11), [0, ] * 10))
        # depth == 1
        for i in range(1, 11):
            temp_cards.append(template.copy())
            temp_cards[-1][i] += 1
        discarded_cards += temp_cards
        prev_cards = temp_cards
        temp_cards = []
        if self.depth == 1:
            return [frozenset(i.items()) for i in discarded_cards]
        # depth > 1
        for i in range(2, self.depth + 1):
            for j in prev_cards:
                if sum(np.array(list(j.values())) * np.array(range(1, 11))) > 21:
                    continue
                for k in range(1, 11):
                    temp_cards.append(j.copy())
                    temp_cards[-1][k] += 1
                    if temp_cards[-1] in temp_cards[:-1]:
                        del temp_cards[-1]
            discarded_cards += temp_cards
            prev_cards = temp_cards
            temp_cards = []
        return [frozenset(i.items()) for i in discarded_cards]

    def generate_probabilites(self, discarded_cards):
        d = copy.deepcopy(self.cards_composition)
        for i, j in dict(discarded_cards).items():
            d[i] -= j
        return self.probabilities(d)

    def generate_markov_chain_terminal(self, p):
        """
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
        """
        # v = np.array(list(p.values()))
        k = [17, 18, 19, 20, 21, "Bust"]
        hard = pd.DataFrame(0, index=k, columns=range(2, 32))
        soft = pd.DataFrame(0, index=k, columns=range(11, 32))
        # a faster way of indexing would be very helpful
        for i in range(31, 16, -1):
            if i > 21:
                hard[i]["Bust"] = 1
            else:
                hard[i][i] = 1
        for i in range(31, 26, -1):
            soft[i][i - 10] = 1

        if min(p.values()) <= 0:
            return {"hard": hard, "soft": soft}

        for i in range(16, 1, -1):
            hard[i] = soft[i + 11] * p[1] + sum([hard[i + j] * p[j] for j in range(2, 11)])
            if i > 11:
                soft[i + 10] = hard[i]
            elif i > 7:
                soft[i + 10] = hard[i + 10]
            elif i == 7:
                if self.r.s17:
                    soft[i + 10] = hard[i + 10]
                else:
                    soft[i + 10] = hard[i]
            else:
                soft[i + 10] = soft[i + 11] * p[1] + sum([soft[i + 10 + j] * p[j] for j in range(2, 11)])
        soft[11] = soft[12] * p[1] + sum([soft[11 + j] * p[j] for j in range(2, 11)])
        return {"hard": hard, "soft": soft}

    # d is existing discarded card, card = new card, col = score, t = hard/soft
    def mc_lookup(self, d, card, col, t):
        if t == "hard":
            if col >= 17:
                return self.default_strat[t][col]
        if t == "soft":
            if col >= 27:
                return self.default_strat[t][col]
            ''' erronous, and this part can be ommitted, but it might be faster to include if fixed
            elif col <= 21:
                if self.r.s17:
                    if col >= 17:
                        return self.default_strat[t][col]
                elif not self.r.s17:
                    if col >= 18:
                        return self.default_strat[t][col]
            '''

        # returns a column needed, d is the existing discarded cards
        d_copy = dict(d.copy())
        d_copy[card] += 1
        try:
            return self.master[frozenset(d_copy.items())][t][col]
        except KeyError:
            # this may not seem obvious, but it works, with a reason, if im not mistaken. can be made faster
            return 0

    def generate_markov_chain(self, d, p):
        k = [17, 18, 19, 20, 21, "Bust"]
        hard = pd.DataFrame(0, index=k, columns=range(2, 32))
        soft = pd.DataFrame(0, index=k, columns=range(11, 32))
        # a faster way of indexing would be very helpful
        for i in range(31, 16, -1):
            if i > 21:
                hard[i]["Bust"] = 1
            else:
                hard[i][i] = 1
        for i in range(31, 26, -1):
            soft[i][i - 10] = 1

        if min(p.values()) <= 0:
            return {"hard": hard, "soft": soft}

        for i in range(16, 1, -1):
            hard[i] = self.mc_lookup(d, 1, i + 11, "soft") * p[1] + \
                      sum([self.mc_lookup(d, j, i + j, "hard") * p[j] for j in range(2, 11)])
            if i > 11:
                soft[i + 10] = hard[i]
            elif i > 7:
                soft[i + 10] = hard[i + 10]
            elif i == 7:
                if self.r.s17:
                    soft[i + 10] = hard[i + 10]
                else:
                    soft[i + 10] = hard[i]
            else:
                soft[i + 10] = sum([self.mc_lookup(d, j, i + 10 + j, "soft") * p[j] for j in range(1, 11)])
        soft[11] = sum([self.mc_lookup(d, j, 11 + j, "soft") * p[j] for j in range(1, 11)])
        return {"hard": hard, "soft": soft}

    def generate_probabilites_all(self):
        temp = None
        if self.depth != 0:
            disc = self.generate_discarded_cards()
            for i in disc:
                self.master[i] = {}
                self.master[i]["p"] = self.generate_probabilites(i)
                self.master[i]["depth"] = sum(dict(i).values())
            for i in range(self.depth, 0, -1):
                print("calculating for depth {}".format(i))
                if i == self.depth:
                    for j in disc:
                        if self.master[j]["depth"] == i:
                            temp = self.generate_markov_chain_terminal(self.master[j]["p"])
                            self.master[j]["hard"] = temp["hard"]
                            self.master[j]["soft"] = temp["soft"]
                else:
                    for j in disc:
                        if self.master[j]["depth"] == i:
                            temp = self.generate_markov_chain(j, self.master[j]["p"])
                            self.master[j]["hard"] = temp["hard"]
                            self.master[j]["soft"] = temp["soft"]
                pass
            print("calculating for depth 0")
            temp = self.generate_markov_chain(frozenset(dict(zip(range(1, 11), [0, ] * 10)).items()),
                                              self.probabilities(self.cards_composition))
        elif self.depth == 0:
            temp = self.generate_markov_chain_terminal(self.probabilities(self.cards_composition))
        self.hard = temp["hard"]
        self.soft = temp["soft"]

    def model_run(self):
        self.generate_probabilites_all()


if __name__ == "__main__":
    x = BJCalc(player_cards=[10, 10], dealer_card=1, depth=5)
    x.model_run()
    # error checking, must only have values 1, there may be rounding errors due to np.int64 data type
    print(x.hard.sum(axis=0).value_counts())
    print(x.soft.sum(axis=0).value_counts())
