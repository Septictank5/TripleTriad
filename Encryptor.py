import PyQt5.QtNetwork as qtn
import json
import datamanip as dm
from logscript import MyLog


class Encryptor:
    def __init__(self):
        self.marker = chr(4)
        self.held_data = ''
        self.logger = MyLog('Encryptor', 'ENC.txt', 'a')

    def encrypt(self, value):
        templist = []
        newvalue = json.dumps(value)
        for item in newvalue:
            character = ord(item)
            character = character * 8 - 10
            templist.append(str(character))
        templist.append(self.marker)
        encrypted_data = ',x'.join(templist).encode()
        return encrypted_data

    def decrypt(self, value):
        templist = []
        decoded_value = value.decode()
        adjusted_decoded_value = self.adjust_value(decoded_value)
        if adjusted_decoded_value is False:
            return
        newvalue = adjusted_decoded_value.split(',x')
        for item in newvalue:
            x = int(item)
            x = (x + 10) // 8
            templist.append(chr(x))
        decrypted_value = ''.join(templist)
        decrypted_value = json.loads(decrypted_value)
        return decrypted_value

    def adjust_value(self, value):
        newvalue = self.held_data + value
        index = newvalue.find(',x' + self.marker)
        if index == -1:
            self.logger.log(f'Got an incomplete data set')
            self.held_data += newvalue
            self.logger.log(f'held_data is {self.held_data}')
            return False

        adjusted_value = newvalue[:index]
        self.store_excess(index, newvalue)
        return adjusted_value

    def store_excess(self, index, value):
        self.held_data = value[index + 4:]


class Server(qtn.QTcpServer):
    def __init__(self):
        super().__init__()
        self.socket_list = []
        self.listen(port=27015)

    def get_socket_address(self, socket):
        str_address = socket.localAddress().toString()
        clean_stage_1 = str_address.replace(':', '')
        clean_str_address = clean_stage_1.replace('f', '')
        return clean_str_address

    def recieve_data(self, socket):
        enc = self.get_encryptor(socket)
        incoming_data = socket.read(8192)
        incoming_data = enc.decrypt(incoming_data)
        if incoming_data is None:
            return None, None
        command = incoming_data['command']
        data = incoming_data['data']
        return command, data

    def send(self, socket, data):
        enc = self.get_encryptor(socket)
        cipher = enc.encrypt(data)
        socket.write(cipher)

    def get_encryptor(self, socket):
        for socket_data in self.socket_list:
            if socket in socket_data:
                return socket_data[1]

    def socket_disconnect(self, socket):
        for index, socket_data in enumerate(self.socket_list):
            if socket == socket_data[0]:
                del self.socket_list[index]
                return

    def add_socket(self, socket):
        self.socket_list.append((socket, Encryptor()))




class Client(qtn.QTcpSocket):
    def __init__(self):
        super().__init__()
        self.enc = Encryptor()
        self.data_handler = dm.DataHandler(self.send)
        self.disconnected.connect(lambda: print('disconnected'))

    def connect_to_server(self, ip):
        self.connectToHost(qtn.QHostAddress(ip), 27015)
        self.connected.connect(lambda: print('connected'))

    def receive_data(self):
        ciphered_data = self.read(8192)
        deciphered_data = self.enc.decrypt(ciphered_data)
        if deciphered_data is None:
            return None, None
        command = deciphered_data['command']
        data = deciphered_data['data']
        return command, data

    def _turn_to_dict(self, command, data):
        return {'command': command, 'data': data}

    def send(self, command, data):
        data_to_send = self._turn_to_dict(command, data)
        cipher = self.enc.encrypt(data_to_send)
        self.write(cipher)

    def disconnect(self):
        self.disconnectFromHost()

    def await_connection(self, time):
        return self.waitForConnected(time)
