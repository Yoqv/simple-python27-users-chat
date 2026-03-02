# Simple Python 2.7 Multi-User Chat

A robust, multi-user chat application featuring a graphical user interface (GUI), private messaging, and administrative controls. Built using Python 2.7, Sockets, and Tkinter.



## 🚀 Features

- **Graphical User Interface:** Built with `Tkinter` for a smooth user experience.
- **Admin System:** Designated managers can `/kick` or `/mute` users.
- **Private Messaging:** Send direct messages using the `/private` command.
- **Real-time Communication:** Uses `select` for non-blocking I/O multiplexing.
- **Status Notifications:** Alerts when users join or leave the chat.

## 🛠️ Commands

Inside the chat, you can use the following commands:

| Command | Description |
| :--- | :--- |
| `/help` | List all available commands. |
| `/private <name> <message>` | Send a private message to a specific user. |
| `/manager <name>` | Grant manager privileges (Admin only). |
| `/mute <name>` | Mute/Unmute a user in the chat (Admin only). |
| `/kick <name>` | Remove a user from the server (Admin only). |
| `quit` | Safely disconnect from the server. |

## 💻 Installation & Usage

### Prerequisites
- Python 2.7.x installed on your machine.

### Running the App
1. **Start the Server:**
   Open a terminal and run:
   ```bash
   python server.py

Note: The default manager is set to "yoav" in the code.

2. Start the Client(s):
    Open another terminal (or multiple) and run:
   ```bash
    python client.py
3. Connect: Enter a unique username and start chatting!

## 🔧 Technical Details

Networking: TCP Sockets.

Concurrency: select.select for handling multiple clients simultaneously on a single thread.

Protocol: Custom message framing (Length-prefixing) to prevent packet fragmentation issues.
