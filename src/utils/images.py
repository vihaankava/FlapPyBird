import random
import os
from typing import List, Tuple

import pygame
from PIL import Image, ImageDraw

from .constants import BACKGROUNDS, PIPES, PLAYERS


class Images:
    numbers: List[pygame.Surface]
    game_over: pygame.Surface
    welcome_message: pygame.Surface
    base: pygame.Surface
    background: pygame.Surface
    player: Tuple[pygame.Surface]
    pipe: Tuple[pygame.Surface]

    def __init__(self) -> None:
        # Create assets directory if it doesn't exist
        os.makedirs("assets/sprites", exist_ok=True)
        
        # Generate scary face and monkey sprites if they don't exist
        if not os.path.exists("assets/sprites/scary_face.png"):
            self.generate_scary_face()
        if not os.path.exists("assets/sprites/monkey0.png"):
            self.generate_monkey_sprites()

        self.numbers = list(
            (
                pygame.image.load(f"assets/sprites/{num}.png").convert_alpha()
                for num in range(10)
            )
        )

        # game over sprite
        self.game_over = pygame.image.load(
            "assets/sprites/gameover.png"
        ).convert_alpha()
        # welcome_message sprite for welcome screen
        self.welcome_message = pygame.image.load(
            "assets/sprites/message.png"
        ).convert_alpha()
        # base (ground) sprite
        self.base = pygame.image.load("assets/sprites/base.png").convert_alpha()
        self.randomize()

    def generate_scary_face(self):
        # Create a 200x200 image with a scary face
        img = Image.new('RGBA', (200, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw scary face
        # Red eyes
        draw.ellipse((50, 50, 90, 90), fill='red')
        draw.ellipse((110, 50, 150, 90), fill='red')
        # Angry eyebrows
        draw.line((40, 40, 80, 30), fill='black', width=5)
        draw.line((120, 30, 160, 40), fill='black', width=5)
        # Frowning mouth
        draw.arc((60, 100, 140, 160), 0, 180, fill='red', width=5)
        # Blood dripping from mouth
        for i in range(3):
            draw.line((90 + i*10, 160, 90 + i*10, 180), fill='red', width=3)
        
        img.save("assets/sprites/scary_face.png")

    def generate_monkey_sprites(self):
        # Generate monkey sprites
        for i in range(3):
            img = Image.new('RGBA', (34, 24), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Brown body
            draw.ellipse((2, 2, 32, 22), fill='#8B4513')  # Brown color
            
            # Face features
            # Eyes
            eye_y = 8 if i == 0 else 7 if i == 1 else 8  # Different positions for animation
            draw.ellipse((10, eye_y, 14, eye_y + 4), fill='black')
            draw.ellipse((20, eye_y, 24, eye_y + 4), fill='black')
            
            # Mouth
            if i == 0:  # Up flap
                draw.arc((12, 12, 22, 18), 0, 180, fill='black', width=1)
            elif i == 1:  # Mid flap
                draw.line((12, 15, 22, 15), fill='black', width=1)
            else:  # Down flap
                draw.arc((12, 12, 22, 18), 180, 360, fill='black', width=1)
            
            # Ears
            draw.ellipse((0, 4, 6, 10), fill='#8B4513')
            draw.ellipse((28, 4, 34, 10), fill='#8B4513')
            
            img.save(f"assets/sprites/monkey{i}.png")

    def randomize(self):
        # select random background sprites
        rand_bg = random.randint(0, len(BACKGROUNDS) - 1)
        # select random pipe sprites
        rand_pipe = random.randint(0, len(PIPES) - 1)

        self.background = pygame.image.load(BACKGROUNDS[rand_bg]).convert()
        
        # Use monkey sprites instead of bird
        self.player = (
            pygame.image.load("assets/sprites/monkey0.png").convert_alpha(),
            pygame.image.load("assets/sprites/monkey1.png").convert_alpha(),
            pygame.image.load("assets/sprites/monkey2.png").convert_alpha(),
        )
        
        self.pipe = (
            pygame.transform.flip(
                pygame.image.load(PIPES[rand_pipe]).convert_alpha(),
                False,
                True,
            ),
            pygame.image.load(PIPES[rand_pipe]).convert_alpha(),
        )
