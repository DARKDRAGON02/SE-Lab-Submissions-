"""Lightweight splash particle effects for Fruit Catcher.

Catching a fruit -- or watching one splatter on the ground -- spawns a short
lived burst of tiny circular droplets that match the item's color.  Everything
is plain pygame drawing, so the effect stays cheap inside a 60 FPS loop.
"""

import math
import random

import pygame


class Particle:
    """A single circular droplet that flies outwards, falls and shrinks away."""

    GRAVITY = 0.32
    DRAG = 0.97

    def __init__(self, x, y, color, velocity, radius, lifetime):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.vx, self.vy = velocity
        self.start_radius = radius
        self.radius = radius
        self.lifetime = max(1, lifetime)
        self.age = 0

    @property
    def alive(self):
        return self.age < self.lifetime

    @property
    def progress(self):
        """0.0 right after the burst, 1.0 once the droplet is spent."""
        return self.age / self.lifetime

    def kill(self):
        self.age = self.lifetime

    def update(self, floor_y=None):
        self.age += 1
        self.vy += self.GRAVITY
        self.vx *= self.DRAG
        self.x += self.vx
        self.y += self.vy

        # Shrink as the droplet fades so the burst visually "dries out".
        self.radius = max(1, int(round(self.start_radius * (1.0 - self.progress))))

        # Droplets that fall well below the floor are finished immediately.
        if floor_y is not None and self.y > floor_y + 40:
            self.kill()

    def render(self, surface):
        if not self.alive:
            return
        fade = 1.0 - 0.6 * self.progress
        color = tuple(int(channel * fade) for channel in self.color)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)


class ParticleSystem:
    """Owns every live droplet, updating and drawing them in a single pass."""

    MAX_PARTICLES = 500

    def __init__(self):
        self.particles = []

    def burst(self, x, y, color, count=16, speed=6.0, direction=None):
        """Emit `count` droplets of `color` from (x, y).

        When `direction` (in radians) is given the burst is sprayed into a cone
        instead of a full circle -- the floor splatter uses this to fire
        upwards, while a basket catch bursts in every direction.
        """
        if len(self.particles) >= self.MAX_PARTICLES:
            return

        for _ in range(count):
            if len(self.particles) >= self.MAX_PARTICLES:
                break  # hard cap keeps long runs from slowing down

            if direction is None:
                angle = random.uniform(0.0, math.tau)
            else:
                angle = direction + random.uniform(-0.85, 0.85)

            magnitude = random.uniform(speed * 0.25, speed)
            velocity = (math.cos(angle) * magnitude, math.sin(angle) * magnitude)

            self.particles.append(
                Particle(
                    x + random.uniform(-4, 4),
                    y + random.uniform(-4, 4),
                    color,
                    velocity,
                    random.randint(2, 5),
                    random.randint(16, 34),
                )
            )

    def update(self, floor_y=None):
        for particle in self.particles[:]:
            particle.update(floor_y)
            if not particle.alive:
                self.particles.remove(particle)

    def render(self, surface):
        for particle in self.particles:
            particle.render(surface)

    def clear(self):
        self.particles.clear()

    def __len__(self):
        return len(self.particles)
