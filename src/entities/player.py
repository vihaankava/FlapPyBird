from enum import Enum
from itertools import cycle

import pygame

from ..utils import GameConfig, clamp
from .entity import Entity
from .floor import Floor
from .pipe import Pipe, Pipes


class PlayerMode(Enum):
    SHM = "SHM"
    NORMAL = "NORMAL"
    CRASH = "CRASH"
    PIPE_DEATH = "PIPE_DEATH"  # New mode for pipe death animation


class Player(Entity):
    def __init__(self, config: GameConfig) -> None:
        image = config.images.player[0]
        x = int(config.window.width * 0.2)
        y = int((config.window.height - image.get_height()) / 2)
        super().__init__(config, image, x, y)
        self.min_y = -2 * self.h
        self.max_y = config.window.viewport_height - self.h * 0.75
        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0
        self.crashed = False
        self.crash_entity = None
        self.pipe_death_progress = 0  # Track progress of pipe death animation
        self.pipe_death_target = None  # Store the pipe we're entering
        self.auto_play = True  # Enable auto-play by default
        self.set_mode(PlayerMode.SHM)

    def set_mode(self, mode: PlayerMode) -> None:
        self.mode = mode
        if mode == PlayerMode.NORMAL:
            self.reset_vals_normal()
            self.config.sounds.wing.play()
        elif mode == PlayerMode.SHM:
            self.reset_vals_shm()
        elif mode == PlayerMode.CRASH:
            self.stop_wings()
            self.config.sounds.hit.play()
            if self.crash_entity == "pipe":
                self.config.sounds.die.play()
            self.reset_vals_crash()
        elif mode == PlayerMode.PIPE_DEATH:
            self.stop_wings()
            self.config.sounds.hit.play()
            self.config.sounds.die.play()
            self.reset_vals_pipe_death()

    def reset_vals_normal(self) -> None:
        self.vel_x = 0  # player's velocity along X axis
        self.vel_y = -9  # player's velocity along Y axis
        self.max_vel_y = 10  # max vel along Y, max descend speed
        self.min_vel_y = -8  # min vel along Y, max ascend speed
        self.acc_y = 1  # players downward acceleration

        self.rot = 80  # player's current rotation
        self.vel_rot = -3  # player's rotation speed
        self.rot_min = -90  # player's min rotation angle
        self.rot_max = 20  # player's max rotation angle

        self.flap_acc = -9  # players speed on flapping
        self.flapped = False  # True when player flaps

    def reset_vals_shm(self) -> None:
        self.vel_y = 1  # player's velocity along Y axis
        self.max_vel_y = 4  # max vel along Y, max descend speed
        self.min_vel_y = -4  # min vel along Y, max ascend speed
        self.acc_y = 0.5  # players downward acceleration

        self.rot = 0  # player's current rotation
        self.vel_rot = 0  # player's rotation speed
        self.rot_min = 0  # player's min rotation angle
        self.rot_max = 0  # player's max rotation angle

        self.flap_acc = 0  # players speed on flapping
        self.flapped = False  # True when player flaps

    def reset_vals_crash(self) -> None:
        self.acc_y = 2
        self.vel_y = 7
        self.max_vel_y = 15
        self.vel_rot = -8
        # Keep the X velocity from collision
        if hasattr(self, 'vel_x'):
            self.x += self.vel_x

    def reset_vals_pipe_death(self) -> None:
        self.vel_x = 0
        self.vel_y = 0
        self.acc_y = 0
        self.vel_rot = 0
        self.rot = 0
        self.pipe_death_progress = 0

    def update_image(self):
        self.frame += 1
        if self.frame % 5 == 0:
            self.img_idx = next(self.img_gen)
            self.image = self.config.images.player[self.img_idx]
            self.w = self.image.get_width()
            self.h = self.image.get_height()

    def tick_shm(self) -> None:
        if self.vel_y >= self.max_vel_y or self.vel_y <= self.min_vel_y:
            self.acc_y *= -1
        self.vel_y += self.acc_y
        self.y += self.vel_y

    def tick_normal(self) -> None:
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False

        # Auto-flap if needed
        if self.should_flap(self.config.pipes):
            self.flap()

        self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
        self.rotate()

    def tick_crash(self) -> None:
        if self.min_y <= self.y <= self.max_y:
            self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
            # Move with pipe if it was a pipe collision
            if self.crash_entity == "pipe" and hasattr(self, 'vel_x'):
                self.x += self.vel_x
            # rotate only when it's a pipe crash and bird is still falling
            if self.crash_entity != "floor":
                self.rotate()

        # player velocity change
        if self.vel_y < self.max_vel_y:
            self.vel_y += self.acc_y

    def tick_pipe_death(self) -> None:
        if self.pipe_death_progress < 100:
            # Calculate target position inside pipe
            target_x = self.pipe_death_target.x + self.pipe_death_target.w / 2
            target_y = self.pipe_death_target.y + self.pipe_death_target.h / 2
            
            # Move bird towards center of pipe
            self.x += (target_x - self.x) * 0.1
            self.y += (target_y - self.y) * 0.1
            
            # Shrink bird as it enters pipe
            scale = 1 - (self.pipe_death_progress / 100)
            self.w = int(self.image.get_width() * scale)
            self.h = int(self.image.get_height() * scale)
            
            self.pipe_death_progress += 2
        else:
            # After animation completes, switch to normal crash mode
            self.set_mode(PlayerMode.CRASH)

    def rotate(self) -> None:
        self.rot = clamp(self.rot + self.vel_rot, self.rot_min, self.rot_max)

    def draw(self) -> None:
        self.update_image()
        if self.mode == PlayerMode.SHM:
            self.tick_shm()
        elif self.mode == PlayerMode.NORMAL:
            self.tick_normal()
        elif self.mode == PlayerMode.CRASH:
            self.tick_crash()
        elif self.mode == PlayerMode.PIPE_DEATH:
            self.tick_pipe_death()

        self.draw_player()

    def draw_player(self) -> None:
        rotated_image = pygame.transform.rotate(self.image, self.rot)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        self.config.screen.blit(rotated_image, rotated_rect)

    def stop_wings(self) -> None:
        self.img_gen = cycle([self.img_idx])

    def flap(self) -> None:
        if self.y > self.min_y:
            self.vel_y = self.flap_acc
            self.flapped = True
            self.rot = 80
            self.config.sounds.wing.play()

    def crossed(self, pipe: Pipe) -> bool:
        return pipe.cx <= self.cx < pipe.cx - pipe.vel_x

    def collided(self, pipes: Pipes, floor: Floor) -> bool:
        """returns True if player collides with floor or pipes."""

        # if player crashes into ground
        if self.collide(floor):
            self.crashed = True
            self.crash_entity = "floor"
            self.config.game_over.show_scary_animation()
            return True

        for pipe in pipes.upper:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                self.config.game_over.show_scary_animation()
                return True
        for pipe in pipes.lower:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                self.config.game_over.show_scary_animation()
                return True

        return False

    def get_next_pipe(self, pipes: Pipes) -> tuple[Pipe, Pipe]:
        """Get the next pipe pair that the player hasn't passed yet"""
        for upper_pipe, lower_pipe in zip(pipes.upper, pipes.lower):
            if upper_pipe.x + upper_pipe.w > self.x:
                return upper_pipe, lower_pipe
        return None, None

    def should_flap(self, pipes: Pipes) -> bool:
        """Determine if the player should flap based on position and upcoming pipes"""
        if not self.auto_play or self.mode != PlayerMode.NORMAL:
            return False

        upper_pipe, lower_pipe = self.get_next_pipe(pipes)
        if not upper_pipe or not lower_pipe:
            return False

        # Calculate the center of the gap
        gap_center_y = upper_pipe.y + upper_pipe.h + (lower_pipe.y - (upper_pipe.y + upper_pipe.h)) / 2

        # Calculate predicted position after current velocity
        predicted_y = self.y + self.vel_y * 2

        # Flap if we're below the gap center and moving down, or if we're falling too fast
        return (predicted_y > gap_center_y and self.vel_y > 0) or self.vel_y > 8
