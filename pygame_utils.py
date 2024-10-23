import pygame
import enum

pygame.font.init()
_DEFAULT_SCREEN_SIZE = (800, 600)
_DEFAIULT_FONT_NAME = "Lucinda"
_DEFAULT_FONT_SIZE = 52
_DEFAULT_FONT = pygame.font.SysFont(_DEFAIULT_FONT_NAME, _DEFAULT_FONT_SIZE)


def load_image(path: str, size: tuple[int, int]) -> pygame.surface.Surface:
    image = pygame.image.load(path)
    try:
        image = pygame.transform.smoothscale(image, size)
    except ValueError:
        image = pygame.transform.scale(image, size)
    return image

_TRANSPARENT_PIXEL = load_image("assets/transparent_pixel.png", (1, 1))


class ReturnValues(enum.Enum):
    NEXT_SCENE = "next_scene"


class Scene:
    def __init__(self, **kwargs):
        self._ended = False
        self._return_values = dict()
    
    def update(self, dt: int):
        raise NotImplementedError("Subclasses must implement method 'update'")

    def draw(self, screen: pygame.Surface):
        raise NotImplementedError("Subclasses must implement method 'draw'")

    def handle_event(self, event: pygame.event.Event):
        raise NotImplementedError("Subclasses must implement method 'handle_event'")
    
    def end_scene(self):
        self._ended = True
    
    def has_ended(self):
        return self._ended
    
    def get_return_values(self):
        return self._return_values
    

class SceneHandler:
    def __init__(self,
                 screen_size: tuple[int, int] = _DEFAULT_SCREEN_SIZE,
                 title: str = "",
                 icon_path: str = ""
                 ):
        self._screen = pygame.display.set_mode(screen_size)
        if title:
            pygame.display.set_caption(title)
        if icon_path:
            icon = load_image(icon_path, (32, 32))
            pygame.display.set_icon(icon)
        self._clock = pygame.time.Clock()
        self._running = True
        self._current_scene = None

    def run(self):
        if self._current_scene is None:
            raise RuntimeError("No scene has been set to run")
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    self._current_scene.handle_event(event)
            
            dt = self._clock.tick(60)
            self._current_scene.update(dt)
            if self._current_scene.has_ended():
                self._handle_scene_end()

            self._current_scene.draw(self._screen)

            pygame.display.flip()

    def set_scene(self, scene: Scene):
        self._current_scene = scene

    def _handle_scene_end(self):
        assert self._current_scene is not None

        return_values = self._current_scene.get_return_values()
        next_scene_type = return_values.get(ReturnValues.NEXT_SCENE, None)
        if next_scene_type is None:
            self._running = False
            return
        next_scene = next_scene_type(**return_values)
        assert isinstance(next_scene, Scene)
        self.set_scene(next_scene)


class Button(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.rect.Rect,
                 font: pygame.font.Font = _DEFAULT_FONT,
                 text: str = "",
                 text_color: tuple[int, int, int] = (255, 255, 255),
                 background_color: tuple[int, int, int] = (0, 0, 0),
                 image: pygame.surface.Surface = _TRANSPARENT_PIXEL
                 ):
        super().__init__()
        self._rect = rect
        self._text_color = text_color
        self._background_color = background_color

        self._font = font
        self._text = text

        self._image = image

    def draw(self, screen: pygame.surface.Surface):
        screen.fill(self._background_color, self._rect)
        screen.blit(self._image, self._rect.topleft)
        text_surface = self._font.render(self._text, True, self._text_color)
        screen.blit(text_surface, text_surface.get_rect(center=self._rect.center))

    def is_intersecting(self, point: tuple[int, int]) -> bool:
        return self._rect.collidepoint(point)
    
    def set_text(self, text: str):
        self._text = text

    def set_font(self, font: pygame.font.Font):
        self._font = font

    def set_text_color(self, color: tuple[int, int, int]):
        self._text_color = color

    def set_background_color(self, color: tuple[int, int, int]):
        self._background_color = color

    def set_image(self, image: pygame.surface.Surface):
        self._image = image

    def set_rect(self, rect: pygame.rect.Rect):
        self._rect = rect

