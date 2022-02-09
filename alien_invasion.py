# Braydon
# 07/13/2021
# Project 1, part 1 (Chapter 12: A ship that fires bullets)

# Standard imports
import sys
from time import sleep

import pygame

# Custom imports
from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien


class AlienInvasion:
    """Overall class to manage game assets and behavior"""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()

        # Create our screen with our window dimensions in a tuple.

        if self.settings.screen_fullscreen:
            # Full screen mode
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.settings.screen_width = self.screen.get_rect().width
            self.settings.screen_height = self.screen.get_rect().height
        else:
            # Window mode
            self.screen = pygame.display.set_mode((
                self.settings.screen_width, self.settings.screen_height))

        pygame.display.set_caption("Alien Invasion")

        # Create an instance to store game statistics and create scoreboard
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # Create our ship
        self.ship = Ship(self)
        # Create our bullets as a group so we can manage them all at once.
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Make the play button
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            # Check for keypress or mouse events
            self._check_events()
            if self.stats.game_active:
                # Update the ship
                self.ship.update()
                # Update the bullets
                self._update_bullets()
                # Update the aliens
                self._update_aliens()

            # Update the screen
            self._update_screen()

    # If a method name starts with an '_' character, it means that it's a
    # helper method. It does work inside the class, but isn't meant to be
    # called through an instance.
    def _check_events(self):
        """Respond to keypress and mouse events."""
        # Watch for keyboard and mouse events.
        # 'pygame.event.get()' listens for any event such as a key press
        # or mouse movement during the duration of the while loop.
        for event in pygame.event.get():
            # Check if user closes window
            if event.type == pygame.QUIT:
                sys.exit()
            # Check if the user clicks the play button. 
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            # Check if user pushes a key down
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            # Check if user releases key
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings
            self.settings.initialize_dynamic_settings()

            # Reset the stats
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # Get rid of any remaining aliens and bullets
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()

            # Hide the mouse cursor
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypress"""
        # User holds right arrow
        if event.key == pygame.K_RIGHT:
            # Start moving right on hold
            self.ship.moving_right = True
        # User holds left arrow
        elif event.key == pygame.K_LEFT:
            # Start moving left on hold
            self.ship.moving_left = True
        # User presses 'q' to quit
        elif event.key == pygame.K_q:
            # Close window
            sys.exit()
        # User presses spacebar to fire
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases"""
        # User releases right arrow
        if event.key == pygame.K_RIGHT:
            # Stop moving right upon release
            self.ship.moving_right = False
        # User releases left arrow
        if event.key == pygame.K_LEFT:
            # Stop moving upon release
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_alllowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets"""
        # Update bullet positions
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collision()

    def _check_bullet_alien_collision(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens,
                                                self.settings.destroy_bullet,
                                                True)

        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create a new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Increase level
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""

        if self.stats.ships_left > 0:
            # Decrement ships_left and update scoreboard
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            # Pause
            sleep(1)
        else:
            # Game over
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _update_aliens(self):
        """
        Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()

        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _create_fleet(self):
        """Create a fleet of aliens"""
        # Create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        # '//' is floor division. It divides two numbers and drops any
        # remainder, so we'll get an integer
        number_aliens_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height)
                             - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        # Create an alien and place it in the row.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen. """
        # Redraw the screen during each pass through the loop. Fills the
        # screen with our previously specified color.
        self.screen.fill(self.settings.bg_color)

        # After the background is filled, we want to draw the ship on the
        # screen by using ship.blitme(), so that the ship is on top of
        # the background
        self.ship.blitme()

        # Draw the bullets as the are created
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # Draw the alien
        self.aliens.draw(self.screen)

        # Draw the score information
        self.sb.show_score()

        # Draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible. It does this by
        # drawing an empty screen on each pass of the while loop, erasing
        # the old screen so only the new screen is visible. This will
        # allow us to continually update the display to show the new
        # positions of game elements and hide old ones, creating the
        # illusion of smooth movement.
        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance and run the game.
    ai = AlienInvasion()
    ai.run_game()
