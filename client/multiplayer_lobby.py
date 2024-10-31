import pygame
import pygame_utils
import socket
import threading
import multiplayer_game


_DEFAULT_FONT_NAME = "Lucinda"
_DEFAULT_FONT_SIZE = 72
_SMALL_FONT_SIZE = 56
_DEFAULT_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _DEFAULT_FONT_SIZE)
_SMALL_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _SMALL_FONT_SIZE)
_DEFAULT_TEXT_COLOR = (255, 255, 255)
_DEFAULT_BACKGROUND_COLOR = (64, 64, 64)
_SECONDARY_BACKGROUND_COLOR = (32, 32, 32)
_RED = (237, 28, 36)
_GREEN = (34, 177, 76)


class MultiplayerLobbyScene(pygame_utils.Scene):
    def __init__(self, returned_values):
        super().__init__(returned_values)
        self._username = returned_values["username"]
        self._network_client = NetworkClient(returned_values["hostname"])
        self._network_client.send_message(f"setname {self._username}")
        self._connected = False
        self._ready = False

        self._connection_title = _DEFAULT_FONT.render(f"Connected to: {returned_values["hostname"]}", True, _DEFAULT_TEXT_COLOR)
        self._connection_title_rect = self._connection_title.get_rect(center=(400, 300))

        self._player_1_name = _SMALL_FONT.render("", True, _DEFAULT_TEXT_COLOR)
        self._player_1_name_rect = self._player_1_name.get_rect(topleft=(50, 50))
        self._player_1_ready = _SMALL_FONT.render("", True, _DEFAULT_TEXT_COLOR)
        self._player_1_ready_rect = self._player_1_ready.get_rect(topleft=(50, 100))

        self._player_2_name = _SMALL_FONT.render("", True, _DEFAULT_TEXT_COLOR)
        self._player_2_name_rect = self._player_2_name.get_rect(topright=(550, 50))
        self._player_2_ready = _SMALL_FONT.render("", True, _DEFAULT_TEXT_COLOR)
        self._player_2_ready_rect = self._player_2_ready.get_rect(topright=(550, 100))

        self._ready_button = pygame_utils.Button(
            pygame.rect.Rect(300, 400, 200, 100),
            text="Ready",
            background_color=_SECONDARY_BACKGROUND_COLOR,
        )

    def update(self, dt):
        for message in self._network_client.get_messages():
            print(f"Received message: {message}")
            self._handle_message(message)

    def draw(self, screen):
        screen.fill(_DEFAULT_BACKGROUND_COLOR)
        screen.blit(self._connection_title, self._connection_title_rect)
        screen.blit(self._player_1_name, self._player_1_name_rect)
        screen.blit(self._player_1_ready, self._player_1_ready_rect)
        screen.blit(self._player_2_name, self._player_2_name_rect)
        screen.blit(self._player_2_ready, self._player_2_ready_rect)
        if self._connected and not self._ready:
            self._ready_button.draw(screen)
        

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._connected and not self._ready and self._ready_button.is_intersecting(event.pos):
                self._ready_button.set_background_color(_DEFAULT_BACKGROUND_COLOR)
                self._ready_button.set_text("")
                self._network_client.send_message(f"ready {self._player_idx}")

    def _handle_message(self, message):
        command, arg = message.split(" ", 1)
        if command == "set":
            self._player_idx = int(arg)
            if self._player_idx == 0:
                self._player_1_name = _SMALL_FONT.render(self._username, True, _DEFAULT_TEXT_COLOR)
                self._player_1_ready = _SMALL_FONT.render("Not Ready", True, _RED)
            elif self._player_idx == 1:
                self._player_2_name = _SMALL_FONT.render(self._username, True, _DEFAULT_TEXT_COLOR)
                self._player_2_ready = _SMALL_FONT.render("Not Ready", True, _RED)
            else:
                raise RuntimeError("Invalid player index")
            self._connected = True

        elif command == "name":
            if self._player_idx == 0:
                self._player_2_name = _SMALL_FONT.render(arg, True, _DEFAULT_TEXT_COLOR)
                self._player_2_ready = _SMALL_FONT.render("Not Ready", True, _RED)
            elif self._player_idx == 1:
                self._player_1_name = _SMALL_FONT.render(arg, True, _DEFAULT_TEXT_COLOR)
                self._player_1_ready = _SMALL_FONT.render("Not Ready", True, _RED)
            else:
                raise RuntimeError("Invalid player index")

        elif command == "ready":
            if arg == "0":
                self._player_1_ready = _SMALL_FONT.render("Ready", True, _GREEN)
            elif arg == "1":
                self._player_2_ready = _SMALL_FONT.render("Ready", True, _GREEN)

        elif command == "start":
            self._start_game(arg)

        else:
            raise RuntimeError("Invalid command")
        
    def _start_game(self, numbers):
        numbers, target = numbers[2:-1].split("], ")
        numbers = [int(num) for num in numbers.split(", ")]
        target = int(target)
        self._return_values = {
            pygame_utils.ReturnValues.NEXT_SCENE: multiplayer_game.MPGameScene,
            "numbers": (numbers, target),
            "player_idx": self._player_idx,
            "username": self._username,
            "network_client": self._network_client,
        }
        self._ended = True


class NetworkClient:
    def __init__(self, hostname):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.connect((hostname, 6779))
        self._socket.setblocking(False)
        self._incoming_messages = []
        self._receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
        self._receive_thread.start()

    def send_message(self, message: str):
        self._socket.sendall(message.encode())

    def get_messages(self):
        messages = self._incoming_messages.copy()
        self._incoming_messages.clear()
        return messages
    
    def _receive_messages(self):
        while True:
            try:
                self._incoming_messages.append(self._socket.recv(1024).decode())
            except BlockingIOError:
                pass