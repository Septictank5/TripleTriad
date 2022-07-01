import PyQt5.QtWidgets as qtw
import sys
import json


class Window(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        with open("Data/TTACards.xml") as myfile:
            data_dict = myfile.readlines()

        mylist = [[], [], [], [], [], [], [], [], [], []]
        index = 0
        for item in data_dict:
            newitem = item.strip()
            if newitem.startswith("<Group"):
                localindex = newitem.index('"')
                index = int(newitem[localindex:localindex + 3].replace('"', '')) - 1
                continue
            if newitem.startswith("<Card"):
                newitem = newitem.replace('Card ', '')
                name = self.findname(newitem)
                blue_image_file = self.findbluefile(newitem)
                red_image_file = self.findredfile(newitem)
                left_number = self.findleftnumber(newitem)
                top_number = self.findtopnumber(newitem)
                right_number = self.findrightnumber(newitem)
                bottom_number = self.findbottomnumber(newitem)
                group = index
                mylist[index].append({'name': name, 'bluefile': blue_image_file, 'redfile': red_image_file,
                                      'left': left_number, 'top': top_number, 'right': right_number,
                                      'bottom': bottom_number, 'group': index})

        with open('CardInfo.json', 'w') as myfile:
            json.dump(mylist, myfile, indent=4)

    def findname(self, data: str):
        index = 7
        secondindex = data.index('"', index, -1)
        print(data[index:secondindex])
        return data[index:secondindex]

    def findbluefile(self, data):
        index = data.index('BlueImage') + 11
        secondindex = data.index('"', index, -1)
        return data[index:secondindex]

    def findredfile(self, data):
        index = data.index('RedImage') + 10
        secondindex = data.index('"', index, -1)
        return data[index:secondindex]

    def findleftnumber(self, data):
        index = data.index('LeftNumber') + 12
        return 10 if data[index] == 'A' else int(data[index])

    def findtopnumber(self, data):
        index = data.index('TopNumber') + 11
        return 10 if data[index] == 'A' else int(data[index])

    def findrightnumber(self, data):
        index = data.index('RightNumber') + 13
        return 10 if data[index] == 'A' else int(data[index])

    def findbottomnumber(self, data):
        index = data.index('BottomNumber') + 14
        return 10 if data[index] == 'A' else int(data[index])

myapp = qtw.QApplication(sys.argv)
window = Window()
sys.exit(myapp.exec())
