import json
import random
from shutil import copyfile


class FileHandler:
    def __init__(self):
        with open('CardInfo.json', 'r') as myfile:
            self.card_data = json.load(myfile)
        self.directory = 'GameSaves/'
        self.saveslist = 'GameSaves/Saves.txt'
        try:
            file = open(self.saveslist, 'x')
            file.close()
        except FileExistsError:
            pass

    def profile_created(self, name):
        profile = self.directory + name + '.txt'
        with open(self.saveslist, 'w') as afile:
            afile.write(profile)
        with open(profile, 'w') as savefile:
            json.dump({}, savefile, indent=4)

    def save_profile(self, name, cardlist, cards_for_game):
        profile = self.directory + name + '.txt'
        self._create_backup(profile)
        with open(profile, 'w') as savefile:
            json.dump([cards_for_game, cardlist], savefile, indent=4)

        with open(self.saveslist, 'r') as savelist:
            data = savelist.readlines()

        if profile in data:
            index = data.index(profile)
            moving = data.pop(index)
            data.insert(0, moving)
        else:
            data.insert(0, profile)

        with open(self.saveslist, 'w') as savelist:
            savelist.writelines(data)

    def load_profile(self, name):
        with open(self.directory + name + '.txt', 'r')as afile:
            cards_for_game, cardlist = json.load(afile)

        return cards_for_game, cardlist


    def get_last_profile(self):
        with open(self.saveslist, 'r') as savelist:
            filename = savelist.readline()

        if filename == '':
            return None, None, []

        with open(filename, 'r') as cardfile:
            cards_for_game, cardlist = json.load(cardfile)

        player_name = self.get_name_from_filename(filename)

        return player_name, cardlist, cards_for_game

    def get_name_from_filename(self, filename):
        wo_directory = filename.replace('GameSaves/', '')
        name = wo_directory.replace('.txt', '')
        return name

    def create_starter_deck(self):
        x = 0
        length = len(self.card_data[2])
        recieved_cards = []
        templist = []
        while x < 50:
            value = random.randrange(0, length)
            if self.card_data[2][value] not in recieved_cards:
                recieved_cards.append(self.card_data[2][value])
                templist.append(self.card_data[2][value])
                x += 1
        x = 0
        length = len(self.card_data[4])
        recieved_cards.clear()
        while x < 3:
            value = random.randrange(0, length)
            if self.card_data[4][value] not in recieved_cards:
                recieved_cards.append(self.card_data[4][value])
                templist.append(self.card_data[4][value])
                x += 1
        x = 0
        length = len(self.card_data[6])
        recieved_cards.clear()
        while x < 2:
            value = random.randrange(0, length)
            if self.card_data[6][value] not in recieved_cards:
                recieved_cards.append(self.card_data[6][value])
                templist.append(self.card_data[6][value])
                x += 1

        return templist

    def _create_backup(self, profile):
        fix1 = profile[:len(profile) - 4]
        backup = fix1 + '_backup.txt'
        copyfile(profile, backup)
