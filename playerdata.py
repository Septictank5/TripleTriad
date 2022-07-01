import random

from filehandler import FileHandler


class Player:
    def __init__(self):
        self.filehandler = FileHandler()
        self.cards_for_game = []
        self.get_last_profile()

    def load_profile(self, name):
        self.cards_for_game, self.cardlist = self.filehandler.load_profile(name)

    def create_starter_deck(self, name):
        self.name = name
        self.filehandler.profile_created(name)
        self.cardlist = self.filehandler.create_starter_deck()
        templist = []
        for i in range(5):
            index = random.randrange(0, len(self.cardlist))
            if index not in templist:
                templist.append(index)

        for index in templist:
            self.cards_for_game.append(self.cardlist[index])

        self.save_data()

    def save_data(self):
        self.filehandler.save_profile(self.name, self.cardlist, self.cards_for_game)

    def get_cards(self):
        return self.cardlist

    def get_name(self):
        return self.name

    def get_hand(self):
        return self.cards_for_game

    def get_last_profile(self):
        self.name, self.cardlist, self.cards_for_game = self.filehandler.get_last_profile()










