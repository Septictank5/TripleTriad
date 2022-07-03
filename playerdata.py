import random

from filehandler import FileHandler


class Player:
    def __init__(self):
        self.hand = []

    def create_starter_deck(self, name, cardlist):
        self.name = name
        self.cardlist = cardlist
        templist = []
        for i in range(5):
            index = random.randrange(0, len(self.cardlist))
            if index not in templist:
                templist.append(index)

        for index in templist:
            self.hand.append(self.cardlist[index])

    def get_cards(self):
        return self.cardlist

    def get_name(self):
        return self.name

    def get_hand(self):
        return self.hand

    def get_profile_data(self):
        return self.name, self.cardlist, self.hand

    def fix_hand(self):
        while len(self.hand) < 5:
            index = random.randrange(0, len(self.cardlist))
            card = self.cardlist[index]
            if card in self.hand:
                continue
            else:
                self.hand.append(card)

    def set_from_profile(self, name, cardlist, hand):
        self.name = name
        self.cardlist = cardlist
        self.hand = hand

    def set_name(self, name):
        self.name = name

    def set_cardlist(self, cardlist):
        self.cardlist = cardlist










