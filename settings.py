# Braydon
# 07/13/2021
# Project 1, part 1 (Chapter 12: A ship that fires bullets)


class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_fullscreen = False
        self.screen_width = 1200
        self.screen_height = 600
        # Set the background color (Red, Green, Blue)
        self.bg_color = (230, 230, 230)

        # Ship settings
        self.ship_image = 'images/ship.bmp'
        self.ship_limit = 3

        # Bullet settings
        self.bullet_width = 10
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_alllowed = 3
        self.destroy_bullet = True

        # Alien settings
        self.alien_image = 'images/alien.bmp'
        self.fleet_drop_speed = 10

        # How quickly the game speeds up
        self.speedup_scale = 1.1

        # How quickly the alien point values increase
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 0.25
        # Fleet direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1

        # Scoring
        self.alien_points = 50

    def increase_speed(self):
        """Increases speed settings and alien point value."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
