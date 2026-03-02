import socket
import select
from datetime import datetime

HOST = '127.0.0.1'
PORT = 1729

server_socket = socket.socket()
server_socket.bind((HOST, PORT))
server_socket.listen(5)
open_client_sockets = []
messages_to_send = []
managers_list = ["yoav"]
clients_dict = {}
ACCEPT_MESSAGE = "ACCEPT"
REJECT_MESSAGE = "REJECT"
NO_PERMISSION_MESSAGE = "[Error] You are not a manager!"
muted_list = []


def send_waiting_messages(write_list):
    for message in messages_to_send:
        clients_sockets, data = message
        for c in clients_sockets:
            if c in write_list:
                c.send(data)
                clients_sockets.remove(c)
        if len(clients_sockets) == 0:
            messages_to_send.remove(message)


def receive_data_from_client(my_socket):
    try:
        name_length = my_socket.recv(1)
        name_length = int(name_length)
        name = my_socket.recv(name_length)
        command = my_socket.recv(1)
        command = int(command)
    except socket.error:
        open_client_sockets.remove(my_socket)
        for name, client_socket in clients_dict.items():
            if client_socket is my_socket:
                clients_dict.pop(name)
        print "Client crashed"
        return None, None, None, None
    if command == 1:
        message_length = my_socket.recv(2)
        message_length = int(message_length)
        message = my_socket.recv(message_length)
        return command, name, None, message
    if command == 2 or command == 3 or command == 4:
        other_name_length = int(my_socket.recv(1))
        other_name = my_socket.recv(other_name_length)
        return command, name, other_name, None
    if command == 5:
        other_name_length = int(my_socket.recv(1))
        other_name = my_socket.recv(other_name_length)
        message_length = my_socket.recv(2)
        message_length = int(message_length)
        message = my_socket.recv(message_length)
        return command, name, other_name, message
    if command == 6:
        return command, name, None, None
    return None, None, None, None


def valid_message(message):
    if 0 < len(message) < 100:
        return True
    return False


def send_message_to_all(message_to_send):
    all_clients_list = []
    for client_socket in open_client_sockets:
        all_clients_list.append(client_socket)
    now = datetime.now()
    current_time = now.strftime("[%H:%M]")
    message_to_send = current_time + " " + message_to_send
    message_length = str(len(message_to_send))
    if len(message_length) < 2:
        message_length = "0" + message_length
    if valid_message(message_to_send):
        messages_to_send.append((all_clients_list, message_length + message_to_send))


def send_not_found_message(sender_name, other_name):
    message_not_found = "[Error] " + other_name + " was not found!"
    sender_socket = clients_dict[sender_name]
    add_message([sender_socket], message_not_found)


def send_private_message(sender_name, other_name, message):
    now = datetime.now()
    current_time = now.strftime("[%H:%M]")
    if other_name not in clients_dict:
        send_not_found_message(sender_name, other_name)
    else:
        message_one = current_time + " !From " + sender_name + ": " + message  # someone
        message_two = current_time + " !To " + other_name + ": " + message  # sender

        socket_one = clients_dict[other_name]
        socket_two = clients_dict[sender_name]
        add_message([socket_one], message_one)
        add_message([socket_two], message_two)


def is_manager(name, client_socket):
    if name not in managers_list:
        add_message([client_socket], NO_PERMISSION_MESSAGE)
        return False
    return True


def get_length_in_bytes(message):
    message_length = str(len(message))
    if len(message_length) < 2:
        message_length = "0" + message_length
    return message_length


def add_message(my_socket_list, message):
    if valid_message(message):
        messages_to_send.append((my_socket_list, get_length_in_bytes(message) + message))


def handle_commands(command, name, other_name, message, current_socket):
    if message == 'quit':
        open_client_sockets.remove(current_socket)
        clients_dict.pop(name)
        print "Client left"
    if command == 1:
        if message == 'quit':
            send_message_to_all(name + " has left the chat.")
        elif message == 'view-managers':
            managers_string = 'Managers: '
            for manager in managers_list:
                if managers_list[-1] != manager:
                    managers_string += manager + ", "
                else:
                    managers_string += manager + "."
            add_message([current_socket], managers_string)
        else:
            if name not in muted_list:
                if name in managers_list:
                    name = "@" + name
                send_message_to_all(name + ": " + message)
            else:
                reply_message = "[Error] You can't speak here!"
                add_message([current_socket], reply_message)
    elif command == 2:
        if other_name in clients_dict:
            if is_manager(name, current_socket) and other_name not in managers_list:
                managers_list.append(other_name)
                reply_message = other_name + " is now manager."
                add_message([current_socket], reply_message)
            elif other_name in managers_list:
                add_message([current_socket], "[Error] " + other_name + " is already a manager")
        else:
            send_not_found_message(name, other_name)
    elif command == 3:
        if other_name in clients_dict:
            if is_manager(name, current_socket):
                send_message_to_all(other_name + " has been kicked from the chat by " + name + ".")
                kicked_socket = clients_dict[other_name]
                add_message([kicked_socket], "[Kick]")
        else:
            send_not_found_message(name, other_name)
    elif command == 4:
        if is_manager(name, current_socket):
            if other_name not in muted_list:
                muted_list.append(other_name)
                reply_message = other_name + " is now muted."
            else:
                muted_list.remove(other_name)
                reply_message = other_name + " is now unmuted."
            add_message([current_socket], reply_message)
    elif command == 5:
        send_private_message(name, other_name, message)
    elif command == 6:
        if name not in clients_dict:
            add_message([current_socket], ACCEPT_MESSAGE)
            clients_dict.update({name: current_socket})
            send_message_to_all(name + " has joined the chat.")
        else:
            add_message([current_socket], REJECT_MESSAGE)
            open_client_sockets.remove(current_socket)


def main():
    while True:
        read_list, write_list, x_list = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
        for current_socket in read_list:
            if current_socket is server_socket:
                new_socket, address = server_socket.accept()
                open_client_sockets.append(new_socket)
            else:
                command, name, other_name, message = receive_data_from_client(current_socket)
                if current_socket in open_client_sockets:
                    handle_commands(command, name, other_name, message, current_socket)

        send_waiting_messages(write_list)


if __name__ == '__main__':
    main()
