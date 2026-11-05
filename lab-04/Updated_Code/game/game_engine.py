import math

import pygame

from game.basket import Basket
from game.fruit import Fruit
from game.particles import ParticleSystem


class GameEngine:
    # --- Difficulty tuning -------------------------------------------------
    SPAWN_DELAY = 750         # starting gap between spawns (ms)
    MIN_SPAWN_DELAY = 260     # fastest the spawner is allowed to get
    SPAWN_DELAY_STEP = 70     # ms shaved off the gap per difficulty level
    SPEED_STEP = 0.5          # extra fall speed granted per level
    MAX_SPEED_BONUS = 4.5     # cap so the game never becomes unplayable
    SCORE_PER_LEVEL = 5       # catches needed to climb one difficulty level
    BASE_HAZARD_CHANCE = 0.12 # chance a spawn is a bomb at level 0
    HAZARD_CHANCE_STEP = 0.03 # extra bomb chance per level
    MAX_HAZARD_CHANCE = 0.35

    START_LIVES = 3
    GROUND_HEIGHT = 25

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.basket = Basket(width, height)
        self.fruits = []
        self.particles = ParticleSystem()

        self.score = 0
        self.lives = self.START_LIVES
        self.spawn_delay = self.SPAWN_DELAY
        self.last_spawn_time = pygame.time.get_ticks()
        self.game_state = "PLAYING"

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_small = pygame.font.SysFont(None, 20)

    # --- Dynamic difficulty (Task 3) ---------------------------------------
    @property
    def level(self):
        """Difficulty step derived from the current score (0 = easiest)."""
        return self.score // self.SCORE_PER_LEVEL

    @property
    def current_spawn_delay(self):
        """Spawn gap shrinks as the score climbs, floored at MIN_SPAWN_DELAY."""
        delay = self.spawn_delay - self.level * self.SPAWN_DELAY_STEP
        return max(self.MIN_SPAWN_DELAY, delay)

    @property
    def speed_bonus(self):
        """Extra fall speed handed to every newly spawned item."""
        return min(self.level * self.SPEED_STEP, self.MAX_SPEED_BONUS)

    @property
    def hazard_chance(self):
        """Bombs show up more often as the run gets harder."""
        chance = self.BASE_HAZARD_CHANCE + self.level * self.HAZARD_CHANCE_STEP
        return min(chance, self.MAX_HAZARD_CHANCE)

    @property
    def ground_y(self):
        return self.height - self.GROUND_HEIGHT

    def handle_event(self, event):
        if self.game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()

    def update(self):
        # Splash droplets keep animating even while the Game Over banner is up.
        self.particles.update(self.height)

        if self.game_state != "PLAYING":
            return

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.basket.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.basket.move_right()

        self._spawn_item()

        basket_rect = self.basket.rect
        for fruit in self.fruits[:]:
            fruit.update()

            if basket_rect.colliderect(fruit.rect):
                self._handle_catch(fruit, basket_rect)
            elif fruit.is_missed(self.height):
                self._handle_miss(fruit)

            if self.game_state == "GAME_OVER":
                break  # stop simulating this frame once the run has ended

    def _spawn_item(self):
        """Spawn a fruit (0.75s baseline) whenever the delay has elapsed."""
        now = pygame.time.get_ticks()
        if now - self.last_spawn_time < self.current_spawn_delay:
            return

        self.last_spawn_time = now

        hazard_chance = self.hazard_chance
        if self.fruits and self.fruits[-1].is_hazard:
            hazard_chance = 0.0  # never punish with two bombs back to back

        self.fruits.append(
            Fruit(self.width, speed_bonus=self.speed_bonus, hazard_chance=hazard_chance)
        )

    def _handle_catch(self, fruit, basket_rect):
        """Basket caught an item: edible fruit scores, bombs cost a life (Task 2)."""
        if fruit.is_hazard:
            self._lose_life()
            self.score = max(0, self.score - abs(fruit.points))
            self.particles.burst(fruit.x, basket_rect.top, fruit.color, count=24, speed=7.5)
        else:
            self.score += fruit.points
            self.particles.burst(fruit.x, basket_rect.top, fruit.color, count=18, speed=6.0)

        if fruit in self.fruits:
            self.fruits.remove(fruit)

    def _handle_miss(self, fruit):
        """Item splattered on the floor: fruit costs a life, bombs were dodged (Task 1)."""
        self.particles.burst(
            fruit.x,
            self.ground_y,
            fruit.color,
            count=16,
            speed=6.5,
            direction=-math.pi / 2,  # splash upwards off the ground
        )

        if not fruit.is_hazard:
            self._lose_life()

        if fruit in self.fruits:
            self.fruits.remove(fruit)

    def _lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.game_state = "GAME_OVER"

    def reset(self):
        self.basket = Basket(self.width, self.height)
        self.fruits.clear()
        self.particles.clear()
        self.score = 0
        self.lives = self.START_LIVES
        self.spawn_delay = self.SPAWN_DELAY
        self.last_spawn_time = pygame.time.get_ticks()
        self.game_state = "PLAYING"

    def render(self, screen):
        screen.fill((28, 32, 40))

        ground_y = self.ground_y
        pygame.draw.rect(screen, (45, 50, 60), (0, ground_y, self.width, self.GROUND_HEIGHT))

        self.basket.render(screen)
        for fruit in self.fruits:
            fruit.render(screen)
        self.particles.render(screen)  # splash droplets sit on top of the fruit

        score_surf = self.font_medium.render(f"Score: {self.score}", True, (255, 220, 80))
        screen.blit(score_surf, (25, 20))

        lives_surf = self.font_medium.render(f"Lives: {self.lives}", True, (240, 80, 80))
        screen.blit(lives_surf, (self.width - lives_surf.get_width() - 25, 20))

        level_surf = self.font_small.render(
            f"Level {self.level + 1}  |  Dodge the spiked bombs!", True, (150, 220, 140)
        )
        screen.blit(level_surf, (self.width // 2 - level_surf.get_width() // 2, 24))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 190))
            screen.blit(overlay, (0, 0))

            over_surf = self.font_big.render("GAME OVER", True, (235, 70, 70))
            screen.blit(over_surf, (self.width // 2 - over_surf.get_width() // 2, self.height // 2 - 40))

            final_surf = self.font_medium.render(f"Final Score: {self.score}", True, (255, 255, 255))
            screen.blit(final_surf, (self.width // 2 - final_surf.get_width() // 2, self.height // 2 + 10))

            restart_surf = self.font_medium.render("Press [R] to Play Again", True, (200, 200, 200))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 50))