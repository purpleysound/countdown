import pygame
import pygame_utils
import random
import numbers_solver
from main_menu import Modes, Difficulty


_DEFAULT_FONT_NAME = "Lucinda"
_DEFAULT_FONT_SIZE = 96
_DEFAULT_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _DEFAULT_FONT_SIZE)
_DEFAULT_TEXT_COLOR = (255, 255, 255)
_DEFAULT_BACKGROUND_COLOR = (64, 64, 64)


class GameScene(pygame_utils.Scene):
    def __init__(self, returned_values):
        super().__init__(returned_values)
        self._numbers, self._target, self._solution = generate_numbers()
        mode = returned_values["mode"] # 1 for stopwatch, -1 for time limit countdown
        if mode == Modes.STOPWATCH:
            self._timer = 0
        elif mode == Modes.TIME_LIMIT:
            self._difficulty = returned_values["difficulty"]
            if self._difficulty == Difficulty.EASY:
                self._timer = 91000
            elif self._difficulty == Difficulty.MEDIUM:
                self._timer = 61000
            elif self._difficulty == Difficulty.HARD:
                self._timer = 31000
            else:
                raise ValueError("Invalid difficulty")
        else:
            raise ValueError("Invalid mode")
        self._timer_direction = mode.value
        self._timer_started = False

    def update(self, dt: int):
        if not self._timer_started:
            self._timer_started = True
            return
        if self._target not in self._numbers:
            self._timer += self._timer_direction * dt
            if self._timer <= 0:
                self._time_out()

    def draw(self, screen: pygame.Surface):
        screen.fill(_DEFAULT_BACKGROUND_COLOR)
        timer_text = _DEFAULT_FONT.render(str(self._timer // 1000), True, _DEFAULT_TEXT_COLOR)
        timer_rect = timer_text.get_rect(center=(400, 50))
        screen.blit(timer_text, timer_rect)

    def handle_event(self, event: pygame.event.Event):
        pass

    def _time_out(self):
        pass


def generate_numbers() -> tuple[list[int, int, int, int, int, int], int, numbers_solver.Solution]:
    """Generates 6 numbers for the game and a target number"""
    while True:
        BIG_NUMBERS = [25, 50, 75, 100]
        SMALL_NUMBERS = list(range(1, 11)) * 2
        big_count = random.randint(0, 4)
        small_count = 6 - big_count
        numbers = random.sample(BIG_NUMBERS, big_count) + random.sample(SMALL_NUMBERS, small_count)
        target = random.randint(100, 999)

        solution = numbers_solver.number_solver_gives_up(numbers, target, 1)
        if solution is not None:
            return numbers, target, solution
        
if __name__ == "__main__":
    numbers, target, solution = generate_numbers()
    print(numbers, target, "\n", solution)
