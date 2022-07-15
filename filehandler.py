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
        self.active_profile = self.directory + name + '.txt'
        with open(self.saveslist, 'r') as afile:
            saves = afile.readlines()
        saves.insert(0, self.active_profile + '\n')
        with open(self.saveslist, 'w') as afile:
            afile.writelines(saves)
        with open(self.active_profile, 'w') as savefile:
            json.dump({}, savefile, indent=4)

    def save_profile(self, cardlist, cards_for_game):
        self._create_backup(self.active_profile)
        with open(self.active_profile, 'w') as savefile:
            json.dump([cards_for_game, cardlist], savefile, indent=4)

        with open(self.saveslist, 'r') as savelist:
            data = savelist.readlines()

        if self.active_profile + '\n' in data:
            index = data.index(self.active_profile + '\n')
            moving = data.pop(index)
            data.insert(0, moving)
        else:
            data.insert(0, self.active_profile + '\n')

        with open(self.saveslist, 'w') as savelist:
            savelist.writelines(data)

    def load_profile(self, name):
        self.active_profile = self.directory + name + '.txt'
        with open(self.active_profile, 'r') as afile:
            cards_for_game, cardlist = json.load(afile)

        return cards_for_game, cardlist

    def get_last_profile(self):
        with open(self.saveslist, 'r') as savelist:
            filename = savelist.readline()

        filename = filename.replace('\n', '')

        try:
            with open(filename, 'r') as cardfile:
                cards_for_game, cardlist = json.load(cardfile)
        except FileNotFoundError:
            return None, None, []

        player_name = self.get_name_from_filename(filename)
        self.active_profile = filename

        return player_name, cardlist, cards_for_game

    def get_name_from_filename(self, filename):
        wo_directory = filename.replace('GameSaves/', '')
        name = wo_directory.replace('.txt', '')
        return name

    def create_starter_deck(self):
        x = 0
        length = len(self.card_data[0])
        recieved_cards = []
        templist = []
        while x < 5:
            value = random.randrange(0, length)
            if self.card_data[2][value] not in recieved_cards:
                recieved_cards.append(self.card_data[0][value])
                templist.append(self.card_data[0][value])
                x += 1
        x = 0
        length = len(self.card_data[2])
        recieved_cards.clear()
        while x < 5:
            value = random.randrange(0, length)
            if self.card_data[4][value] not in recieved_cards:
                recieved_cards.append(self.card_data[2][value])
                templist.append(self.card_data[2][value])
                x += 1
        x = 0
        length = len(self.card_data[3])
        recieved_cards.clear()
        while x < 5:
            value = random.randrange(0, length)
            if self.card_data[6][value] not in recieved_cards:
                recieved_cards.append(self.card_data[3][value])
                templist.append(self.card_data[3][value])
                x += 1

        return templist

    def update_and_save(self, cards, cards_for_game):
        templist = []
        for group in self.card_data:
            for card in group:
                if card in cards:
                    templist.append(card)

        self.save_profile(cards, cards_for_game)
        return templist

    def get_profile_list(self):
        with open(self.saveslist, 'r') as savesfile:
            saves = savesfile.readlines()

        templist = []
        for string in saves:
            savename = string.replace('\n', '')
            name = self.get_name_from_filename(savename)
            templist.append(name)

        return templist

    def _create_backup(self, profile):
        fix1 = profile[:len(profile) - 4]
        backup = fix1 + '_backup.txt'
        copyfile(profile, backup)

    def get_card_data(self):
        return self.card_data

    def get_random_card_from_group(self, group):
        index = random.randrange(0, len(self.card_data[group]))
        return self.card_data[group][index]

    def gen_hand_of_level(self, average):
        start = average - 2 if average - 2 >= 0 else 0
        end = average + 2 if average + 2 <= 9 else 9
        templist = []
        for i in range(5):
            templist.append(random.randint(start, end))
        list_average = self._mean_of_list_values(templist)
        while list_average < average:
            index = random.randrange(0, len(templist))
            templist[index] += 1
            list_average = self._mean_of_list_values(templist)
        while list_average > average:
            index = random.randrange(0, len(templist))
            templist[index] -= 1
            list_average = self._mean_of_list_values(templist)
        cpu_hand = []
        print(list_average, average)
        print(templist)
        for i in range(len(templist)):
            index = templist[i]
            card_index = random.randrange(0, len(self.card_data[index]))
            card = self.card_data[index][card_index]
            while card in cpu_hand:
                card_index = random.randrange(0, len(self.card_data[index]))
                card = self.card_data[index][card_index]
            cpu_hand.append(card)
        return cpu_hand

    def _mean_of_list_values(self, number_list):
        value = 0
        for item in number_list:
            value += item
        return value // len(number_list)

