import pygame
import pygame_utils
import enum

_DEFAULT_FONT_NAME = "Lucinda"
_DEFAULT_FONT_SIZE = 72
_DEFAULT_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _DEFAULT_FONT_SIZE)
_DEFAULT_TEXT_COLOR = (255, 255, 255)
_DEFAULT_BACKGROUND_COLOR = (64, 64, 64)
_SECONDARY_BACKGROUND_COLOR = (32, 32, 32)
_GREEN = (34, 177, 76)
_RED = (237, 28, 36)
_AMBER = (255, 127, 39)
_DARK_RED = (136, 0, 21)


class Modes(enum.Enum):
    TIME_LIMIT = "time_limit"
    STOPWATCH = "stopwatch"


class Difficulty(enum.Enum):
    EASY = 0
    MEDIUM = 1
    HARD = 2


class MainMenuScene(pygame_utils.Scene):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._title = _DEFAULT_FONT.render("Countdown", True, _DEFAULT_TEXT_COLOR)
        self._title_rect = self._title.get_rect(center=(400, 50))
        
        self._time_limit_button = pygame_utils.Button(
            pygame.rect.Rect(75, 125, 250, 175),
            text = "Time Limit",
            background_color = _SECONDARY_BACKGROUND_COLOR,
        )
        self._stopwatch_button = pygame_utils.Button(
            pygame.rect.Rect(475, 125, 250, 175),
            text="Stopwatch",
            background_color = _RED,
        )

        self._time_option_buttons = [  # blend into the background, get set when time limit is selected
            pygame_utils.Button(
                pygame.rect.Rect(25, 350, 225, 100),
                background_color=_DEFAULT_BACKGROUND_COLOR
            ),
            pygame_utils.Button(
                pygame.rect.Rect(275, 350, 250, 100),
                background_color=_DEFAULT_BACKGROUND_COLOR
            ),
            pygame_utils.Button(
                pygame.rect.Rect(550, 350, 225, 100),
                background_color=_DEFAULT_BACKGROUND_COLOR
            ),
        ]

        self._mode = Modes.STOPWATCH
        self._difficulty = Difficulty.EASY

        self._to_start_text = _DEFAULT_FONT.render("Press Enter to Start", True, _DEFAULT_TEXT_COLOR)
        self._to_start_rect = self._to_start_text.get_rect(center=(400, 525))


    def update(self, dt: int):
        pass

    def draw(self, screen: pygame.Surface):
        screen.fill(_DEFAULT_BACKGROUND_COLOR)
        screen.blit(self._title, self._title_rect)
        self._time_limit_button.draw(screen)
        self._stopwatch_button.draw(screen)
        for button in self._time_option_buttons:
            button.draw(screen)
        screen.blit(self._to_start_text, self._to_start_rect)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._end_scene()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self._time_limit_button.is_intersecting(event.pos):
                self._set_mode(Modes.TIME_LIMIT)
            if self._stopwatch_button.is_intersecting(event.pos):
                self._set_mode(Modes.STOPWATCH)
            for i, button in enumerate(self._time_option_buttons):
                if button.is_intersecting(event.pos):
                    self._difficulty = Difficulty(i)

    def _set_mode(self, mode: Modes):
        self._mode = mode
        if mode == Modes.TIME_LIMIT:
            self._time_limit_button.set_background_color(_RED)
            self._stopwatch_button.set_background_color(_SECONDARY_BACKGROUND_COLOR)
            for i, button in enumerate(self._time_option_buttons):
                button.set_background_color((_GREEN, _AMBER, _DARK_RED)[i])
                button.set_text(f"{('Easy', 'Medium', 'Hard')[i]} - {90 - 30 * i}s")

        elif mode == Modes.STOPWATCH:
            self._time_limit_button.set_background_color(_SECONDARY_BACKGROUND_COLOR)
            self._stopwatch_button.set_background_color(_RED)
            for i, button in enumerate(self._time_option_buttons):
                button.set_background_color(_DEFAULT_BACKGROUND_COLOR)
                button.set_text("")
    
        else:
            raise ValueError(f"Invalid mode: {mode}")
        
    def _end_scene(self):
        self._return_values = {
            # pygame_utils.ReturnValues.NEXT_SCENE: GameScene,
            "mode": self._mode,
            "difficulty": self._difficulty,
        }
        self._ended = True
