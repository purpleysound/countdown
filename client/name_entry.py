import pygame
import pygame_utils
from main_menu import MainMenuScene

_DEFAULT_FONT_NAME = "Lucinda"
_DEFAULT_FONT_SIZE = 96
_DEFAULT_FONT = pygame.font.SysFont(_DEFAULT_FONT_NAME, _DEFAULT_FONT_SIZE)
_DEFAULT_TEXT_COLOR = (255, 255, 255)
_DEFAULT_BACKGROUND_COLOR = (64, 64, 64)

class NameEntryScene(pygame_utils.Scene):
    def __init__(self, returned_values={}):
        super().__init__(returned_values)
        self._name = ""

        self._title_text = _DEFAULT_FONT.render("Countdown", True, _DEFAULT_TEXT_COLOR)
        self._title_text_rect = self._title_text.get_rect(center=(400, 50))

        self._enter_text = _DEFAULT_FONT.render("Enter your name:", True, _DEFAULT_TEXT_COLOR)
        self._enter_text_rect = self._enter_text.get_rect(center=(400, 200))

        self._update_name_text()

        self._press_enter_text = _DEFAULT_FONT.render("Press enter to start", True, _DEFAULT_TEXT_COLOR)
        self._press_enter_text_rect = self._press_enter_text.get_rect(center=(400, 500))

    def _update_name_text(self):
        self._name_text = _DEFAULT_FONT.render(self._name, True, _DEFAULT_TEXT_COLOR)
        self._name_text_rect = self._name_text.get_rect(center=(400, 350))

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(_DEFAULT_BACKGROUND_COLOR)
        screen.blit(self._title_text, self._title_text_rect)
        screen.blit(self._enter_text, self._enter_text_rect)
        screen.blit(self._name_text, self._name_text_rect)
        screen.blit(self._press_enter_text, self._press_enter_text_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self._name = self._name[:-1]
            elif event.key == pygame.K_RETURN:
                self._end_scene()
            else:
                self._name += event.unicode
            self._update_name_text()

    def _end_scene(self):
        if self._name == "":
            return
        self._return_values = {pygame_utils.ReturnValues.NEXT_SCENE: MainMenuScene,
                               "username": self._name}
        self._ended = True

