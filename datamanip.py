

class DataHandler:
    def __init__(self, sendfunc):
        self.send = sendfunc
        self.serverlist = []
        self.connectionpairs = []
        self.mydict = {
            'Add To Server List': self._add_to_server_list,
            'Connect To Client': self._connect_to_client,
            'To Other Client': self._pass_through,
            'Request Server List': self._server_list_request,
            'Remove From Server List': self._close_game
        }

    def handle_data(self, socket, command, data):
        if command not in self.mydict.keys():
            cipher_data = self._turn_to_dict(command, data)
            self._pass_through(socket, cipher_data)
            return
        self.mydict[command](socket, data)

    def remove_from_serverlist(self, socket):
        index = 0
        for sock, name in self.serverlist:
            if sock == socket:
                del self.serverlist[index]
            else:
                index += 1

    def _add_to_server_list(self, socket, cipher_data):
        self.serverlist.append((socket, cipher_data))

    def _connect_to_client(self, socket, cipher_data):
        for sock, info in self.serverlist:
            if cipher_data == info:
                self.connectionpairs.append((socket, sock))
                data1 = self._turn_to_dict('Connection Established As Client', '')
                data2 = self._turn_to_dict('Connection Established As Host', '')
                self.send(socket, data1)
                self.send(sock, data2)

    # noinspection PyUnusedLocal
    def _server_list_request(self, socket, data):
        string = ''
        for item in self.serverlist:
            string += item[1] + ' '

        replydata = {'command': 'SLR', 'data': string}
        self.send(socket, replydata)

    def _close_game(self, socket, data):
        for index, item in enumerate(self.serverlist):
            if item[1] == data:
                del self.serverlist[index]

    def _pass_through(self, socket, cipher_data):
        for sock1, sock2 in self.connectionpairs:
            if socket == sock1:
                self.send(sock2, cipher_data)
            elif socket == sock2:
                self.send(sock1, cipher_data)

    def _turn_to_dict(self, command, data):
        return {'command': command, 'data': data}

