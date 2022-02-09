# Braydon
# 07/19/2021
# Project 1, part 2 (Aliens!)


class GameStats:
    """Track statistics for Alien invasion."""

    def __init__(self, ai_game):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()

        # High score should never be reset
        self.high_score = 0
        self.level = 1

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit

        # Reset the score
        self.score = 0

        # Start the game in an inactive state
        self.game_active = False

