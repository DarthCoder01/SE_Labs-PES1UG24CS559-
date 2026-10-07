"""
GameEngine: owns the paddle, ball, bricks, lives, and score.

Task 2: 3 lives, game over, restart with R.
Task 3: normal / strong / unbreakable bricks.
Task 4: score with a combo multiplier.
"""

import pygame

from game.paddle import Paddle
from game.ball import Ball
from game.brick import Brick, NORMAL, STRONG, UNBREAKABLE
from game.collision import handle_ball_brick_collision
from game.renderer import WIDTH, HEIGHT

BRICK_ROWS = 4
BRICK_COLS = 8
BRICK_WIDTH = 68
BRICK_HEIGHT = 22
BRICK_GAP = 6
BRICK_TOP_MARGIN = 50
STARTING_LIVES = 3

POINTS_PER_BRICK = 100
MAX_MULTIPLIER = 10


class GameEngine:
    def __init__(self):
        self._new_game()

    def _new_game(self):
        self.paddle = Paddle(x=WIDTH / 2, y=HEIGHT - 30)
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)
        self.bricks = self._build_bricks()
        self.lives = STARTING_LIVES
        self.game_over = False
        self.score = 0
        self.combo = 0          # bricks destroyed in a row without missing

    @property
    def multiplier(self):
        return min(1 + self.combo, MAX_MULTIPLIER)

    @staticmethod
    def _kind_for(row, col):
        if row == 1 and col in (0, BRICK_COLS - 1):
            return UNBREAKABLE      # one on each edge of row 2
        if row == 0:
            return STRONG           # whole top row takes 3 hits
        return NORMAL

    def _build_bricks(self):
        bricks = []
        total_width = BRICK_COLS * (BRICK_WIDTH + BRICK_GAP) - BRICK_GAP
        start_x = (WIDTH - total_width) / 2
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = start_x + col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_TOP_MARGIN + row * (BRICK_HEIGHT + BRICK_GAP)
                bricks.append(Brick(x, y, BRICK_WIDTH, BRICK_HEIGHT, self._kind_for(row, col)))
        return bricks

    def _reset_ball(self):
        self.ball = Ball(x=WIDTH / 2, y=HEIGHT - 50)

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        dx = 0
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.paddle.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.paddle.speed
        self.paddle.move(dx, WIDTH)

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self._new_game()

    def update(self):
        if self.game_over:
            return

        self.ball.update()
        self.ball.bounce_off_walls(WIDTH)

        if self.ball.get_rect().colliderect(self.paddle.get_rect()) and self.ball.vy > 0:
            self.ball.bounce_off_paddle(self.paddle.get_rect())

        for brick in self.bricks:
            if handle_ball_brick_collision(self.ball, brick):
                if brick.hit():                 # True only when destroyed
                    # Score at the current multiplier, then grow the combo
                    self.score += POINTS_PER_BRICK * self.multiplier
                    self.combo += 1
                    self.bricks.remove(brick)   # safe: we break right after
                break

        if self.ball.is_below(HEIGHT):
            self.combo = 0                      # missing the ball resets the combo
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self._reset_ball()

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.paddle, self.ball, self.bricks)
        breakable_left = sum(1 for b in self.bricks if b.breakable)
        renderer.draw_text(surface, font, f"Bricks: {breakable_left}", (10, 10))
        renderer.draw_text(surface, font, f"Score: {self.score}", (180, 10))
        renderer.draw_text(surface, font, f"Combo: x{self.multiplier}", (360, 10))
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (WIDTH - 110, 10))
        if self.game_over:
            renderer.draw_banner(surface, font, "GAME OVER - Press R to restart")
