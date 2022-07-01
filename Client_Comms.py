from Encryptor import Client
from MainMenuUI import MainMenu


class ClientUI(Client):
    def __init__(self):
        super().__init__()
        self.window = MainMenu()
        self.input_dialog = self.window.get_input_dialog()
        self.error_dialog = self.window.get_error_dialog()
        self.info_dialog = self.window.get_info_dialog()
        self.info_dialog.host_cancel_clicked().connect(self.disconnect)
        self.window.host_clicked().connect(self.host)
        self.window.join_clicked().connect(self.prep_server_screen)

    def host(self):
        self.connect_to_server("208.92.110.56")

        if self.await_connection(1000):
            response = self.input_dialog.prompt_host_game()
            if response[1]:
                self.server_name = response[0]
                self.send('Add To Server List', self.server_name)
                self.error_dialog.finished.connect(self.close_host)
                self.info_dialog.awaiting_player()
            else:
                self.disconnect()
        else:
            self.error_dialog.server_not_online()

    def prep_server_screen(self):
        self.connect_to_server("208.92.110.56")
        if self.await_connection(1000):
            self.send('Request Server List', '')
        else:
            self.error_dialog.server_not_online()

    def show_server_screen(self, serverlist):
        chosen_item = self.input_dialog.prompt_server_list(serverlist)
        if chosen_item[1]:
            self.send('Connect To Client', chosen_item[0])
        else:
            self.disconnect()

    def handle_data(self, command, data):
        if command == 'SLR':
            serverlist = data.split()
            if len(serverlist) == 0:
                self.error_dialog.error_no_servers()
            else:
                self.show_server_screen(serverlist)

        if command == 'RTD':
            self.disconnect()

    def close_host(self):
        self.error_dialog.finished.disconnect()
        self.send('Remove From Server List', self.server_name)

    def player_ready(self, cardlist):
        self.send('Ready', cardlist)

    def player_not_ready(self):
        self.send('Not Ready', '')

    def send_game_starting(self, cardlist):
        self.send('Game Start', cardlist)

    def card_place_notify(self, cell):
        self.send('Move Update', [cell.id, cell.card.id])

    def prompt_create_profile(self):
        return self.input_dialog.prompt_create_profile()

    def get_window(self):
        return self.window

    def host_success(self):
        self.info_dialog.success()
