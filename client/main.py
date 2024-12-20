import pygame
import pygame_utils
from name_entry import NameEntryScene

DEFAULT_FONT_NAME = "Lucinda"
DEFAULT_FONT_SIZE = 52
DEFAULT_FONT = pygame.font.SysFont(DEFAULT_FONT_NAME, DEFAULT_FONT_SIZE)
DEFAULT_TEXT_COLOR = (255, 255, 255)
DEFAULT_SCREEN_SIZE = (800, 600)
DEFAULT_BACKGROUND_COLOR = (64, 64, 64)


if __name__ == "__main__":
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # set cwd to the directory of this file
    pygame.init()
    __scene_handler = pygame_utils.SceneHandler(title = "Countdown Numbers Game")  # please dont use this anywhere else <3
    __scene_handler.set_scene(NameEntryScene())    
    __scene_handler.run()
    pygame.quit()
