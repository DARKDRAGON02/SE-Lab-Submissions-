import math
import random

import pygame

# Edible fruit palette.
FRUIT_COLORS = [
    (230, 45, 45),   # Apple
    (245, 140, 30),  # Orange
    (160, 60, 200),  # Grape
]

# Hazard (rotten/spiked bomb) palette.
HAZARD_BODY_COLOR = (48, 56, 46)
HAZARD_SPIKE_COLOR = (120, 215, 90)
HAZARD_RING_COLOR = (95, 100, 90)
HAZARD_SPARK_COLOR = (255, 205, 60)

HAZARD_SCORE_PENALTY = 2


class Fruit:
    """A single falling item: either an edible fruit or a hazard bomb.

    Hazards are drawn as a dark spiked ball so they read clearly at a glance.
    The basket scores points for edible fruit, while catching a hazard costs a
    life -- so the player has to dodge as well as catch.
    """

    def __init__(self, screen_width, speed_bonus=0.0, hazard_chance=0.18):
        self.screen_width = screen_width
        self.is_hazard = random.random() < hazard_chance

        self.radius = 12 if self.is_hazard else 14
        self.x = random.randint(30, screen_width - 30)
        self.y = -self.radius * 2

        self.speed = random.uniform(4.0, 6.5) + speed_bonus
        if self.is_hazard:
            # Bombs are slightly quicker, making them harder to dodge.
            self.speed *= 1.1
            self.color = HAZARD_BODY_COLOR
        else:
            self.color = random.choice(FRUIT_COLORS)

    @property
    def points(self):
        """Score change applied when the basket catches this item."""
        return -HAZARD_SCORE_PENALTY if self.is_hazard else 1

    def update(self):
        self.y += self.speed

    def is_missed(self, screen_height):
        return self.y > screen_height

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def render(self, surface):
        center = (int(self.x), int(self.y))
        if self.is_hazard:
            self._render_hazard(surface, center)
        else:
            pygame.draw.circle(surface, self.color, center, self.radius)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 4), int(self.y - 4)), 3)

    def _render_hazard(self, surface, center):
        """Draw a spiked rotten bomb: spikes, charred body and a blinking fuse."""
        cx, cy = center

        for index in range(8):
            angle = index * (math.pi / 4)
            tip = (int(cx + math.cos(angle) * (self.radius + 6)),
                   int(cy + math.sin(angle) * (self.radius + 6)))
            left = (int(cx + math.cos(angle - 0.35) * (self.radius - 2)),
                    int(cy + math.sin(angle - 0.35) * (self.radius - 2)))
            right = (int(cx + math.cos(angle + 0.35) * (self.radius - 2)),
                     int(cy + math.sin(angle + 0.35) * (self.radius - 2)))
            pygame.draw.polygon(surface, HAZARD_SPIKE_COLOR, [tip, left, right])

        pygame.draw.circle(surface, HAZARD_BODY_COLOR, center, self.radius)
        pygame.draw.circle(surface, HAZARD_RING_COLOR, center, self.radius, width=2)
        pygame.draw.circle(surface, HAZARD_SPIKE_COLOR, center, max(3, self.radius // 3))

        # Blinking fuse spark hints that the bomb is live.
        if (pygame.time.get_ticks() // 150) % 2 == 0:
            pygame.draw.circle(surface, HAZARD_SPARK_COLOR, (cx, cy - self.radius - 6), 3)