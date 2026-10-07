"""
Brick: a single block. Three kinds: normal, strong, unbreakable.
"""

import pygame

NORMAL = "normal"
STRONG = "strong"
UNBREAKABLE = "unbreakable"

STRONG_HITS = 3

COLOR_NORMAL = (200, 90, 90)
COLOR_UNBREAKABLE = (120, 120, 130)
# Strong bricks get lighter as they take damage
COLOR_STRONG = {3: (60, 100, 200), 2: (100, 140, 230), 1: (150, 185, 250)}


class Brick:
    def __init__(self, x, y, width, height, kind=NORMAL):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.kind = kind
        if kind == STRONG:
            self.hits_remaining = STRONG_HITS
        elif kind == UNBREAKABLE:
            self.hits_remaining = None   # never counts down
        else:
            self.hits_remaining = 1

    @property
    def breakable(self):
        return self.kind != UNBREAKABLE

    @property
    def color(self):
        if self.kind == UNBREAKABLE:
            return COLOR_UNBREAKABLE
        if self.kind == STRONG:
            return COLOR_STRONG.get(self.hits_remaining, COLOR_STRONG[1])
        return COLOR_NORMAL

    def hit(self):
        """Register a hit. Returns True if the brick is now destroyed."""
        if not self.breakable:
            return False
        self.hits_remaining -= 1
        return self.hits_remaining <= 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
