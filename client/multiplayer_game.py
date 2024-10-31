import pygame
import pygame_utils
import game
import stats

_BACKGROUND_COLOR = (64, 64, 64)

class MPGameScene(game.GameScene):
    def __init__(self, returned_values):
        self._network_client = returned_values["network_client"]
        returned_values["mode"] = game.Modes.MULTIPLAYER
        super().__init__(returned_values)
        self._player_idx = returned_values["player_idx"]
        self._username = returned_values["username"]


    def update(self, dt):
        for message in self._network_client.get_messages():
            print(f"Received message: {message}")
            self._handle_message(message)
        return super().update(dt)
    
    def _handle_message(self, message):
        command, arg = message.split(" ", 1)
        if command == "finish":
            self._win = int(arg) == self._player_idx
            self._handle_finish()
        elif command == "ready":
            pass
        else:
            raise RuntimeError("Invalid command")
        
    def _end_scene(self):
        self._network_client.send_message(f"finish {self._player_idx}")

    def _handle_finish(self):
        self._return_values = {
            pygame_utils.ReturnValues.NEXT_SCENE: stats.StatsScene,
            "win": self._win,
            "mode": 0,
            "username": self._username,
            "timer": self._timer
        }
        self._ended = True

    def handle_quit(self):
        self._return_values = {
            pygame_utils.ReturnValues.NEXT_SCENE: stats.StatsScene,
            "mode": 0,
            "username": self._return_values["username"],
            "timer": self._timer,
            "win": False
        }
        self._ended = True


    
