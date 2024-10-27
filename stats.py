import pygame
import pygame_utils
import json
from math import ceil


_BACKGROUND_COLOR = (64, 64, 64)
_DEFAULT_FONT_NAME = "Lucinda"
_DEFAULT_FONT_SIZE = 36
_TITLE_FONT_SIZE = 96
_DEFAULT_FONT_COLOR = (255, 255, 255)
_RED = (255, 0, 0)
_GREEN = (0, 255, 0)
_DEFAULT_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _DEFAULT_FONT_SIZE)
_TITLE_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _TITLE_FONT_SIZE)


class StatsScene(pygame_utils.Scene):
    def __init__(self, returned_values):
        super().__init__(returned_values)
        update_stats(returned_values)
        stats = load_expanded_stats(returned_values["username"])

        if returned_values["win"]:
            self._victory_text = _TITLE_FONT.render("Victory!", True, _GREEN)
        else:
            self._victory_text = _TITLE_FONT.render("Failure", True, _RED)
        self._victory_text_rect = self._victory_text.get_rect(center=(400, 50))

        self._stats_text = _TITLE_FONT.render("Stats", True, _DEFAULT_FONT_COLOR)
        self._stats_text_rect = self._stats_text.get_rect(center=(400, 150))

        self._generate_stats_text(stats)

    def update(self, dt: int):
        pass

    def draw(self, screen: pygame.Surface):
        screen.fill(_BACKGROUND_COLOR)
        screen.blit(self._victory_text, self._victory_text_rect)
        screen.blit(self._stats_text, self._stats_text_rect)
        for text_surface, text_rect in self._stats_texts:
            screen.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event):
        pass

    def _generate_stats_text(self, stats: dict):
        self._stats_texts = []
        x = 10
        y = 200
        for key, value in stats.items():
            text = f"{snake_case_to_title_case(key)}: {value}"
            if key.endswith("_percentage"):
                text += "%"
            if key.endswith("time"):
                time = format_time(value)
                text = f"{snake_case_to_title_case(key)}: {time}"

            text_surface = _DEFAULT_FONT.render(text, True, _DEFAULT_FONT_COLOR)
            text_rect = text_surface.get_rect(topleft=(x, y))
            self._stats_texts.append((text_surface, text_rect))
            y += 40
            if y > 550:
                x += 400
                y = 200


def update_stats(returned_values):
    current_stats = load_stats(name=returned_values["username"])
    current_stats["games_played"] += 1
    if returned_values["mode"] == 1:
        current_stats["stopwatch_games_played"] += 1
        time_taken = returned_values["timer"]
    else:
        current_stats["time_limit_games_played"] += 1
        difficulty = returned_values["difficulty"].value
        difficulty_name = ("easy", "medium", "hard")[difficulty]
        if returned_values["win"]:
            key = "wins"
        else:
            key = "losses"
        current_stats[f"{difficulty_name}_{key}"] += 1
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

def load_expanded_stats(name: str) -> dict:
    stats = load_stats(name)
    try:
        stats["win_percentage"] = round(stats["wins"] / stats["games_played"] * 100, 2)
    except ZeroDivisionError:
        stats["win_percentage"] = 0
    try:
        stats["easy_win_percentage"] = round(stats["easy_wins"] / (stats["easy_wins"] + stats["easy_losses"]) * 100, 2)
    except ZeroDivisionError:
        stats["easy_win_percentage"] = 0
    try:
        stats["medium_win_percentage"] = round(stats["medium_wins"] / (stats["medium_wins"] + stats["medium_losses"]) * 100, 2)
    except ZeroDivisionError:
        stats["medium_win_percentage"] = 0
    try:
        stats["hard_win_percentage"] = round(stats["hard_wins"] / (stats["hard_wins"] + stats["hard_losses"]) * 100, 2)
    except ZeroDivisionError:
        stats["hard_win_percentage"] = 0
    stats["average_time"] = stats["total_time"] // stats["games_played"]  # since measured in milliseconds, decimals are negligible
    return stats

def save_stats(stats: dict, name: str):
    all_stats = load_stats()
    all_stats[name] = stats
    with open("stats.json", "w") as file:
        json.dump(all_stats, file, indent=4)


def snake_case_to_title_case(snake_case: str) -> str:
    return " ".join([word.capitalize() for word in snake_case.split("_")])


def format_time(time: int) -> str:  # time in milliseconds
    if time < 1000:
        return f"{time} ms"
    time /= 1000
    if time < 60:
        return f"{time:.2f} s"
    time /= 60
    if time < 60:
        return f"{time:.2f} m"
    time /= 60
    return f"{time:.2f} h"
