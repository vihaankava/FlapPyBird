from ..utils import GameConfig
from .entity import Entity
import pygame


class GameOver(Entity):
    def __init__(self, config: GameConfig) -> None:
        super().__init__(
            config=config,
            image=config.images.game_over,
            x=(config.window.width - config.images.game_over.get_width()) // 2,
            y=int(config.window.height * 0.2),
        )
        self.scary_face = pygame.image.load("assets/sprites/scary_face.png").convert_alpha()
        self.scary_face = pygame.transform.scale(self.scary_face, (200, 200))
        self.scary_face_alpha = 0
        self.show_scary_face = False
        self.scary_face_timer = 0

    def tick(self) -> None:
        super().tick()
        if self.show_scary_face:
            self.scary_face_timer += 1
            if self.scary_face_timer < 30:  # Fade in
                self.scary_face_alpha = min(255, self.scary_face_alpha + 10)
            elif self.scary_face_timer > 90:  # Fade out
                self.scary_face_alpha = max(0, self.scary_face_alpha - 10)
            
            if self.scary_face_timer > 120:  # Reset after animation
                self.show_scary_face = False
                self.scary_face_timer = 0
                self.scary_face_alpha = 0

    def draw(self) -> None:
        super().draw()
        if self.show_scary_face:
            # Draw scary face in center of screen
            self.scary_face.set_alpha(self.scary_face_alpha)
            x = (self.config.window.width - self.scary_face.get_width()) // 2
            y = (self.config.window.height - self.scary_face.get_height()) // 2
            self.config.screen.blit(self.scary_face, (x, y))

    def show_scary_animation(self) -> None:
        self.show_scary_face = True
        self.scary_face_timer = 0
        self.scary_face_alpha = 0
