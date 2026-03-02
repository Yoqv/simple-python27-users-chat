import socket
import select
import Tkinter as tk

PORT = 1729
IP = '127.0.0.1'
ADDRESS = (IP, PORT)
client_socket = socket.socket()
is_connected = False
waiting_for_connection = False

client_name = ""
messages_to_send = []
root = tk.Tk()
root.state('zoomed')
root.title("Users Chat")

MAX_NAME_LENGTH = 9
chat_box = tk.Text(state=tk.DISABLED)
console_text = tk.Label(font=("Arial 18", 16), fg='Red')
ACCEPT_MESSAGE = 'ACCEPT'
ADDED_STRING_LENGTH = len("[00:00] @: ")


def run_client():
    if is_connected:
        read_list, write_list, x_list = select.select([client_socket], [client_socket], [])
        for message in messages_to_send:
            if client_socket in write_list:
                client_socket.send(message)
                messages_to_send.remove(message)
        if client_socket in read_list:
            message_length = client_socket.recv(2)
            message_length = int(message_length)
            server_response = client_socket.recv(message_length)
            if server_response == '[Kick]':
                root.quit()
            else:
                add_message_to_chat_box(server_response)
    elif waiting_for_connection:
        register_name_in_server()

    root.after(1, run_client)


def is_private_message(message):
    if len(message.split()) < 2:
        return False
    if "!" in message.split()[1]:
        return True
    return False


def is_error_message(message):
    if len(message.split()) < 1:
        return False
    if "[Error]" in message.split()[0]:
        return True
    return False


def is_english(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


def valid_name(name):
    if not is_english(name):
        return False
    if len(name) == 0 or len(name) > MAX_NAME_LENGTH:
        return False
    for one_char in name:
        if not one_char.isalpha() and not one_char.isdigit():
            return False
    return True


def save_name_and_connect(widget):
    global client_name
    global is_connected
    global waiting_for_connection
    current_name = widget.get()
    if valid_name(current_name):
        try:
            client_socket.connect(ADDRESS)
            client_name = current_name
            message_to_send = str(len(client_name)) + client_name + "6"
            messages_to_send.append(message_to_send)
            waiting_for_connection = True
        except socket.error:
            console_text['text'] = "Could not connect to the server"
    else:
        widget.delete(0, tk.END)
        console_text['text'] = "Invalid username!"


def register_name_in_server():
    global waiting_for_connection
    global is_connected
    global client_name
    global client_socket
    read_list, write_list, x_list = select.select([client_socket], [client_socket], [])
    for message in messages_to_send:
        if client_socket in write_list:
            client_socket.send(message)
            messages_to_send.remove(message)
    if client_socket in read_list:
        response_length = client_socket.recv(2)
        response_length = int(response_length)
        server_response = client_socket.recv(response_length)
        if server_response == ACCEPT_MESSAGE:
            waiting_for_connection = False
            is_connected = True
            chat_screen()
        else:
            client_socket.close()
            client_socket = socket.socket()
            waiting_for_connection = False
            client_name = ""
            console_text['text'] = "Name already taken."


def add_message_to_chat_box(message, tags=None):
    if is_private_message(message):
        tags = 'orange'
    elif is_error_message(message):
        tags = 'error'
    fully_scrolled_down = (chat_box.yview()[1] == 1.0)
    chat_box.config(state=tk.NORMAL)
    chat_box.insert(tk.END, message + "\n", tags)
    chat_box.config(state=tk.DISABLED)
    if fully_scrolled_down:
        chat_box.yview(tk.END)


def focus_out_entry_box(widget, entry_text):
    if widget['fg'] == 'Black' and len(widget.get()) == 0:
        widget.delete(0, tk.END)
        widget['fg'] = 'Grey'
        widget.insert(0, 'Enter ' + entry_text + ' here')


def focus_in_entry_box(widget):
    if widget['fg'] == 'Grey':
        widget['fg'] = 'Black'
        widget.delete(0, tk.END)


def chat_screen():
    root.unbind('<Return>')
    clear_screen()
    global chat_box
    message_box = tk.Entry(font='Arial 18', fg='Grey')
    message_box.insert(0, 'Enter message here')
    message_box.bind("<FocusIn>", lambda args: focus_in_entry_box(message_box))
    message_box.bind("<FocusOut>", lambda args: focus_out_entry_box(message_box, 'message'))

    send_button = tk.Button(bg='Green', text="Send Message", command=lambda: send_message(message_box))
    root.bind('<Return>', lambda args: send_message(message_box))
    chat_box = tk.Text(state=tk.DISABLED, font=("Arial 18", 16))
    chat_box.tag_configure("error", foreground="red")
    chat_box.tag_configure("help", foreground="blue")
    chat_box.tag_configure("orange", foreground="orange")
    scroll = tk.Scrollbar(root, command=chat_box.yview)
    chat_box.configure(yscrollcommand=scroll.set)

    chat_box.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="nsew")
    message_box.grid(row=1, column=0, sticky='we')
    send_button.grid(row=1, column=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)


def valid_message(message):
    if not is_english(message):
        return False
    if len(message) == 0 or len(message) + ADDED_STRING_LENGTH + len(client_name) > 99:
        return False
    return True


def disconnect():
    if is_connected:
        message = 'quit'
        message_length = str(len(message))
        if len(message_length) < 2:
            message_length = "0" + message_length
        message_to_send = str(len(client_name)) + client_name + "1" + message_length + message
        client_socket.send(message_to_send)


def handle_command(message):
    args = message.split()
    args_length = len(args)
    if args[0] == '/private':
        if args_length >= 3:
            sent_to = args[1]
            private_message = ''
            counter = 0
            private_message_list = args[2:]
            for word in private_message_list:
                if counter != 0:
                    private_message = private_message + " " + word
                else:
                    private_message += word
                counter += 1
            message_length = str(len(private_message))
            if len(message_length) < 2:
                message_length = "0" + message_length
            sent_to_length = str(len(sent_to))
            message_to_send = str(len(client_name)) + client_name + "5"
            message_to_send += sent_to_length + sent_to + message_length + private_message
            messages_to_send.append(message_to_send)
        else:
            add_message_to_chat_box("Usage: /private (name) (message)", "error")
    elif args[0] == '/mute' or args[0] == '/kick' or args[0] == '/manager':
        if args_length == 2:
            command = ''
            if args[0] == '/mute':
                command = '4'
            elif args[0] == '/kick':
                command = '3'
            elif args[0] == '/manager':
                command = '2'
            other_name = args[1]
            other_name_length = str(len(other_name))
            message_to_send = str(len(client_name)) + client_name + command
            message_to_send += other_name_length + other_name
            messages_to_send.append(message_to_send)
        else:
            if args[0] == '/mute':
                add_message_to_chat_box("Usage: /mute (name)", "error")
            elif args[0] == '/manager':
                add_message_to_chat_box("Usage: /manager (name)", "error")
            elif args[0] == '/kick':
                add_message_to_chat_box("Usage: /kick (name)", "error")
    elif args[0] == '/help':
        add_message_to_chat_box("------------------------------------------------", "help")
        add_message_to_chat_box("/mute - Mute from chat", "help")
        add_message_to_chat_box("/kick - Kick from chat", "help")
        add_message_to_chat_box("/manager - Add manager", "help")
        add_message_to_chat_box("/private - Send private message", "help")
        add_message_to_chat_box("------------------------------------------------", "help")
    else:
        add_message_to_chat_box("Unknown command. Type /help for commands list.", "error")


def send_message(widget):
    if widget['fg'] == 'Black':
        message = widget.get()
        if message == 'quit':
            root.quit()
        if len(message) > 0 and message[0] == '/' and valid_message(message):
            widget.delete(0, tk.END)
            handle_command(message)
        else:
            widget.delete(0, tk.END)
            if valid_message(message):
                message_length = str(len(message))
                if len(message_length) < 2:
                    message_length = "0" + message_length
                message_to_send = str(len(client_name)) + client_name + "1" + message_length + message
                messages_to_send.append(message_to_send)
            else:
                if not is_english(message):
                    add_message_to_chat_box("Message must be English!", "error")
                elif len(message) != 0:
                    add_message_to_chat_box("Message is too long!", "error")


def clear_screen():
    for widget in root.winfo_children():
        widget.destroy()


def main():
    text_window = tk.Entry(font='Arial 18', fg='Grey')
    text_window.insert(0, 'Enter name here')
    text_window.bind("<FocusIn>", lambda args: focus_in_entry_box(text_window))
    text_window.bind("<FocusOut>", lambda args: focus_out_entry_box(text_window, 'name'))
    enter_name_button = tk.Button(bg='Grey', text="Enter Chat")
    enter_name_button.config(command=lambda: save_name_and_connect(text_window))
    root.bind('<Return>', lambda args: save_name_and_connect(text_window))

    text_window.pack()
    enter_name_button.pack()
    console_text.pack()

    root.after(1, run_client)
    root.mainloop()
    disconnect()


if __name__ == '__main__':
    main()
