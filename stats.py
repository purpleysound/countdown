import pygame
import pygame_utils
import json


_BACKGROUND_COLOR = (64, 64, 64)


class StatsScene(pygame_utils.Scene):
    def __init__(self, returned_values):
        super().__init__(returned_values)
        update_stats(returned_values)

    def update(self, dt: int):
        pass

    def draw(self, screen: pygame.Surface):
        screen.fill(_BACKGROUND_COLOR)

    def handle_event(self, event: pygame.event.Event):
        pass


def update_stats(returned_values):
    current_stats = load_stats(name=returned_values["username"])
    current_stats["games_played"] += 1
    if returned_values["mode"] == 1:
        current_stats["stopwatch_games_played"] += 1
        time_taken = returned_values["timer"]
    else:
        current_stats["time_limit_games_played"] += 1
        difficulty = returned_values["difficulty"].value
        if returned_values["win"]:
            key = "wins"
        else:
            key = "losses"
        current_stats[f"{difficulty}_{key}"] += 1
        start_time = (2 - difficulty) * 30000 + 31000
        time_taken = start_time - returned_values["timer"]
    current_stats["total_time"] += time_taken
    if returned_values["win"]:
        current_stats["wins"] += 1
    else:
        current_stats["losses"] += 1
    save_stats(current_stats, returned_values["username"])

def load_stats(name = None) -> dict:
    try:
        with open("stats.json", "r") as file:
            stats = json.load(file)
    except FileNotFoundError:
        stats = {}
    if name is None:
        return stats
    return stats.get(name, {
        "games_played": 0,
        "stopwatch_games_played": 0,
        "time_limit_games_played": 0,
        "total_time": 0,
        "wins": 0,
        "losses": 0,
        "easy_wins": 0,
        "easy_losses": 0,
        "medium_wins": 0,
        "medium_losses": 0,
        "hard_wins": 0,
        "hard_losses": 0
    })

def save_stats(stats: dict, name: str):
    all_stats = load_stats()
    all_stats[name] = stats
    with open("stats.json", "w") as file:
        json.dump(all_stats, file, indent=4)
