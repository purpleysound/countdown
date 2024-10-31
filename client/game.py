import pygame
import pygame_utils
import random
import numbers_solver
from main_menu import Modes, Difficulty
from stats import StatsScene


_DEFAULT_FONT_NAME = "Lucinda"
_DEFAULT_FONT_SIZE = 96
_SMALLER_FONT_SIZE = 64
_OPERATOR_FONT_SIZE = 128
_DEFAULT_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _DEFAULT_FONT_SIZE)
_OPERATOR_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _OPERATOR_FONT_SIZE)
_SMALLER_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _SMALLER_FONT_SIZE)
_DEFAULT_TEXT_COLOR = (255, 255, 255)
_DEFAULT_BACKGROUND_COLOR = (64, 64, 64)

_OPERATOR_NUM_TO_TEXT = {
    0: "+",
    1: "-",
    2: "×",
    3: "÷"
}

_OPERATOR_NUM_TO_FUNC = {
    0: lambda x, y: x + y,
    1: lambda x, y: x - y,
    2: lambda x, y: x * y,
    3: lambda x, y: x / y
}


class GameScene(pygame_utils.Scene):
    def __init__(self, returned_values):
        super().__init__(returned_values)
        self._return_values["username"] = returned_values["username"]
        if "numbers" in returned_values:
            self._numbers, self._target = returned_values["numbers"]
            self._solution = returned_values.get("solution", None)
        else:
            self._numbers, self._target, self._solution = generate_numbers()
        self._original_numbers = self._numbers.copy()
        mode = returned_values["mode"]
        if mode == Modes.STOPWATCH:
            self._timer = 0
            self._difficulty = -1
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
        elif mode == Modes.MULTIPLAYER:
            self._timer = 0
            self._difficulty = -1
        else:
            raise ValueError("Invalid mode")
        self._timer_direction = -1 if mode == Modes.TIME_LIMIT else 1
        self._timer_started = False

        self._target_text = _DEFAULT_FONT.render(f"Target: {self._target}", True, _DEFAULT_TEXT_COLOR)
        self._target_text_rect = self._target_text.get_rect(center=(400, 150))

        self._generate_number_buttons()
        self._operation_buttons = [
            pygame_utils.Button(pygame.rect.Rect(80, 325, 100, 100), _OPERATOR_FONT, "+", _DEFAULT_TEXT_COLOR, _DEFAULT_BACKGROUND_COLOR),
            pygame_utils.Button(pygame.rect.Rect(260, 325, 100, 100), _OPERATOR_FONT, "-", _DEFAULT_TEXT_COLOR, _DEFAULT_BACKGROUND_COLOR),
            pygame_utils.Button(pygame.rect.Rect(440, 325, 100, 100), _OPERATOR_FONT, "×", _DEFAULT_TEXT_COLOR, _DEFAULT_BACKGROUND_COLOR),
            pygame_utils.Button(pygame.rect.Rect(620, 325, 100, 100), _OPERATOR_FONT, "÷", _DEFAULT_TEXT_COLOR, _DEFAULT_BACKGROUND_COLOR),
        ]
        self._current_expression: list[int, int, int] = []
        self._update_expression_text()

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
        timer_text = _DEFAULT_FONT.render(f"{self._timer // 1000} Seconds", True, _DEFAULT_TEXT_COLOR)
        timer_rect = timer_text.get_rect(center=(400, 50))
        screen.blit(timer_text, timer_rect)
        screen.blit(self._target_text, self._target_text_rect)
        for button in self._number_buttons:
            button.draw(screen) 
        for button in self._operation_buttons:
            button.draw(screen)
        screen.blit(self._expression_text, self._expression_text_rect)
        
        
    def _generate_number_buttons(self):
        self._number_buttons = []
        num_count = len(self._numbers)
        mid_point = (num_count-1)/2
        for i, num in enumerate(self._numbers):
            centre = (400 + (i - mid_point) * (125 + 25 * (6-num_count)), 225)
            left, top = centre[0] - 50, centre[1]
            button_rect = pygame.rect.Rect(left, top, 100, 100)
            button = pygame_utils.Button(button_rect,
                                         text=str(num),
                                         font=_DEFAULT_FONT,
                                         text_color=_DEFAULT_TEXT_COLOR,
                                         background_color=_DEFAULT_BACKGROUND_COLOR
                                         )
            self._number_buttons.append(button)


    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if len(self._current_expression) == 0:
                for i, button in enumerate(self._number_buttons):
                    if button.is_intersecting(event.pos):
                        self._current_expression.append(self._numbers[i])
                        self._update_expression_text()
                        break
            elif len(self._current_expression) == 1:
                for i, button in enumerate(self._operation_buttons):
                    if button.is_intersecting(event.pos):
                        self._current_expression.append(i)
                        self._update_expression_text()
                        break
            elif len(self._current_expression) == 2:
                for i, button in enumerate(self._number_buttons):
                    if button.is_intersecting(event.pos):
                        if self._numbers[i] == self._current_expression[0] and self._numbers.count(self._current_expression[0]) == 1:
                            continue
                        if self._current_expression[1] == 3 and self._numbers[i] == 0:
                            break
                        self._current_expression.append(self._numbers[i])
                        self._update_expression_text()
                        break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                try:
                    self._current_expression.pop()
                except IndexError:
                    pass
                self._update_expression_text()
            elif event.key == pygame.K_RETURN:
                if len(self._current_expression) == 3:
                    result, success = self._evaluate_expression()
                    if success:
                        self._numbers.remove(self._current_expression[0])
                        self._numbers.remove(self._current_expression[2])
                        self._numbers.append(result)
                        self._current_expression = []
                        self._generate_number_buttons()
                        self._update_expression_text()
                        if result == self._target:
                            self._win = True
                            self._end_scene()
            elif event.key == pygame.K_ESCAPE:
                self._numbers = self._original_numbers.copy()
                self._generate_number_buttons()
                self._current_expression = []
                self._update_expression_text()

    def _update_expression_text(self):
        if len(self._current_expression) == 0:
            self._expression_text = _DEFAULT_FONT.render("", True, _DEFAULT_TEXT_COLOR)
        elif len(self._current_expression) == 1:
            self._expression_text = _DEFAULT_FONT.render(str(self._current_expression[0]), True, _DEFAULT_TEXT_COLOR)
        elif len(self._current_expression) == 2:
            num1, operation_num = self._current_expression
            self._expression_text = _DEFAULT_FONT.render(f"{num1} {_OPERATOR_NUM_TO_TEXT[operation_num]}", True, _DEFAULT_TEXT_COLOR)
        elif len(self._current_expression) == 3:
            num1, operation_num, num2 = self._current_expression
            result, success = self._evaluate_expression()
            self._expression_text = _DEFAULT_FONT.render(f"{num1} {_OPERATOR_NUM_TO_TEXT[operation_num]} {num2} = {result}", True, _DEFAULT_TEXT_COLOR)
            if not success:
                if isinstance(result, float):
                    result = round(result, 2)
                result = f"Invalid ({result})"
                self._expression_text = _SMALLER_FONT.render(f"{num1} {_OPERATOR_NUM_TO_TEXT[operation_num]} {num2} = {result}", True, _DEFAULT_TEXT_COLOR)

        else:
            raise RuntimeError("Invalid expression length")
        self._expression_text_rect = self._expression_text.get_rect(center=(400, 450))

    def _evaluate_expression(self) -> tuple[int, bool]:
        assert len(self._current_expression) == 3
        num1, operation_num, num2 = self._current_expression
        result = _OPERATOR_NUM_TO_FUNC[operation_num](num1, num2)
        if not result.is_integer() or result < 0:
            return result, False
        return int(result), True

    def _time_out(self):
        self._win = False
        self._end_scene()

    def _end_scene(self):
        self._return_values = {
            pygame_utils.ReturnValues.NEXT_SCENE: StatsScene,
            "mode": self._timer_direction,
            "difficulty": self._difficulty,
            "username": self._return_values["username"],
            "timer": self._timer,
            "win": self._win
        }
        self._ended = True

    def handle_quit(self):
        self._return_values = {
            pygame_utils.ReturnValues.NEXT_SCENE: StatsScene,
            "mode": self._timer_direction,
            "difficulty": self._difficulty,
            "username": self._return_values["username"],
            "timer": self._timer,
            "win": False
        }
        self._ended = True


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
