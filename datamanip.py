

class DataHandler:
    def __init__(self, sendfunc):
        self.send = sendfunc
        self.serverlist = []
        self.connectionpairs = []
        self.mydict = {
            'Add To Server List': self.add_to_server_list,
            'Connect To Client': self.connect_to_client,
            'To Other Client': self.pass_through,
            'Request Server List': self.server_list_request,
            'Remove From Server List': self.close_game
        }

    def add_to_server_list(self, socket, cipher_data):
        self.serverlist.append((socket, cipher_data))

    def connect_to_client(self, socket, cipher_data):
        for sock, info in self.serverlist:
            if cipher_data == info:
                self.connectionpairs.append((socket, sock))
                data1 = self.turn_to_dict('Connection Established As Client', '')
                data2 = self.turn_to_dict('Connection Established As Host', '')
                self.send(socket, data1)
                self.send(sock, data2)

    # noinspection PyUnusedLocal
    def server_list_request(self, socket, data):
        string = ''
        for item in self.serverlist:
            string += item[1] + ' '

        replydata = {'command': 'SLR', 'data': string}
        self.send(socket, replydata)

    def remove_from_serverlist(self, socket):
        index = 0
        for sock, name in self.serverlist:
            if sock == socket:
                del self.serverlist[index]
            else:
                index += 1

    def close_game(self, socket, data):
        for index, item in enumerate(self.serverlist):
            if item[1] == data:
                del self.serverlist[index]

    def inform_ready(self, socket, data):
        ready = self.turn_to_dict('Ready', data)
        self.pass_through(socket, ready)

    def inform_not_ready(self, socket, data):
        notready = self.turn_to_dict('Not Ready', data)
        self.pass_through(socket, notready)

    def game_start(self, socket, data):
        game_start = self.turn_to_dict('Game Start', data)
        self.pass_through(socket, game_start)

    def move_update(self, socket, data):
        move_update = self.turn_to_dict('Move Update', data)
        self.pass_through(socket, move_update)

    def card_lost(self, socket, data):
        card_lost = self.turn_to_dict('Card Lost', data)
        self.pass_through(socket, card_lost)

    def reward_update(self, socket, data):
        reward_update = self.turn_to_dict('Reward Update', data)
        self.pass_through(socket, reward_update)

    def pass_through(self, socket, cipher_data):
        for sock1, sock2 in self.connectionpairs:
            if socket == sock1:
                self.send(sock2, cipher_data)
            elif socket == sock2:
                self.send(sock1, cipher_data)

    def turn_to_dict(self, command, data):
        return {'command': command, 'data': data}

