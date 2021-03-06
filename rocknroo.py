# coding=utf-8
import pyglet
import arcade
import os
import time
import math

'''
    2019 © rocknroo.com
'''

SCREEN_TITLE = "ROCK & R.O.O."
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 720

MAP_HEIGHT = 2560
MAP_WIDTH = 6400

SPRITE_SCALING = .5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * SPRITE_SCALING)

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN_TOP = 256
VIEWPORT_MARGIN_BOTTOM = 256
VIEWPORT_RIGHT_MARGIN = 512
VIEWPORT_LEFT_MARGIN = 512

# Physics
MOVEMENT_SPEED = 4
JUMP_SPEED = 16
GRAVITY = 1
LASER_SPEED = 20


def read_sprite_list(grid, sprite_list):
    for row in grid:
        for grid_location in row:
            if grid_location.tile is not None:
                tile_sprite = arcade.Sprite(grid_location.tile.source, SPRITE_SCALING)
                tile_sprite.center_x = grid_location.center_x * SPRITE_SCALING
                tile_sprite.center_y = grid_location.center_y * SPRITE_SCALING
                # print(f"{grid_location.tile.source} -- ({tile_sprite.center_x:4}, {tile_sprite.center_y:4})")
                sprite_list.append(tile_sprite)


class MyGame(arcade.Window):
    """ Main application class. This is the where all core game aspects are outlined in order to be created and used as they are needed. Any other class is a helper/property of MyGame """

    def __init__(self):
        """
            Initializer
            """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=False)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        # Sprite lists
        self.my_map = None
        self.background_list = None
        self.wall_list = None
        self.platform_list = None
        self.laser_list = None

        # Menu resources
        self.pause_menu = None

        # Prepare player & player_team
        self.player = None
        self.player_facing_direction = "right"
        self.player_team = None
        self.player_list = None

        # Prepare NPC's
        self.npc_list = None
        self.tiki_sprite = None
        self.coin_list = None
        self.ice_list = None

        # Gravity & Collision
        self.physics_engine = None

        # Scoring, Status, Upgrade, Bonus, and Experience info
        self.score = 0
        self.trees_saved = 0

        # Viewport(viewable area within window)
        self.view_left = 0
        self.view_bottom = 0

        # Game state info
        self.game_over = False
        self.paused_state = False
        self.previously_paused = False

        # Framerate & Time
        self.last_time = None
        self.frame_count = 0
        self.fps_message = None

        # Background sounds (MUSIC)
        self.music_player = None
        self.level_music = None
        self.pause_menu_music = None
        self.game_over_music = None

        # Game sounds (SFX)
        self.collect_coin_sound = None
        self.jump_sound = None
        self.wall_hit_sound = None
        self.ice_hit_sound = None
        self.gun_sound = None

        # Static Graphics menu, buttons, mini-map, etc.
        self.menu_mask = None
        self.paused_mask = None

        '''
        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_status = False
        '''

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        # do not use is_static=True for animated sprites
        self.player_list = arcade.SpriteList()
        self.npc_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(is_static=True)
        self.platform_list = arcade.SpriteList(is_static=True)
        self.background_list = arcade.SpriteList(is_static=True)
        self.coin_list = arcade.SpriteList()
        self.ice_list = arcade.SpriteList()
        self.laser_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player = arcade.AnimatedWalkingSprite()

        character_scale = .5
        self.player.stand_right_textures = []
        self.player.stand_right_textures.append(arcade.load_texture("images/rock_stand_right.png",
                                                                    scale=character_scale))
        self.player.stand_left_textures = []
        self.player.stand_left_textures.append(arcade.load_texture("images/rock_stand_left.png",
                                                                   scale=character_scale))

        self.player.walk_right_textures = []

        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_001.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_002.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_003.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_004.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_005.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_006.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_007.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_008.png", scale=character_scale))
        self.player.walk_right_textures.append(
            arcade.load_texture("images/rock_walk_right_009.png", scale=character_scale))

        self.player.walk_left_textures = []

        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_001.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_002.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_003.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_004.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_005.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_006.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_007.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_008.png", scale=character_scale))
        self.player.walk_left_textures.append(
            arcade.load_texture("images/rock_walk_left_009.png", scale=character_scale))

        self.player.texture_change_distance = 20

        # Read in the tiled map
        map_name = "NLA-testLvL5.tmx"
        self.my_map = arcade.read_tiled_map(map_name, SPRITE_SCALING)

        # Grab the layer of items we can't move through
        map_array = self.my_map.layers_int_data["Walls"]

        # Calculate the right edge of the my_map in pixels
        self.end_of_map = len(map_array[0]) * GRID_PIXEL_SIZE
        self.player.boundary_left = 128
        self.player.boundary_right = self.end_of_map - 128

        # Starting position of the player
        self.player.center_x = 384
        self.player.center_y = 768
        self.player.scale = 0.5

        self.player_list.append(self.player)

        # --- Background ---
        read_sprite_list(self.my_map.layers["Background"], self.background_list)
        # --- Walls ---
        read_sprite_list(self.my_map.layers["Walls"], self.wall_list)
        # --- Platforms ---
        read_sprite_list(self.my_map.layers["Platforms"], self.platform_list)
        # --- Static NPC's ---
        read_sprite_list(self.my_map.layers["NPC"], self.npc_list)
        # --- Ice ---
        read_sprite_list(self.my_map.layers["Ice"], self.ice_list)
        # --- Coins ---
        read_sprite_list(self.my_map.layers["Coins"], self.coin_list)
        for coin in self.coin_list:
            coin.angle = 0
            coin.change_angle = 5

        # --- Other stuff

        # Set the background color
        if self.my_map.backgroundcolor:
            arcade.set_background_color(self.my_map.backgroundcolor)

        # Set the image to be used for the texture of the menu/map overlay
        self.menu_mask = arcade.load_texture("images/background_mask3.png")

        # Set the image to be used for the texture of the menu/map overlay
        self.paused_mask = arcade.load_texture("images/paused_mask.png")

        # Apply gravity/ physics to sprites
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,
                                                             self.platform_list,
                                                             gravity_constant=GRAVITY)

        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        self.game_over = False

        # Background sounds (MUSIC)
        self.music_player = pyglet.media.Player()
        self.level_music = pyglet.media.load("sounds/music.wav")
        self.pause_menu_music = pyglet.media.load("sounds/paused.wav")
        self.game_over_music = pyglet.media.load("sounds/gameover1.wav")

        # Game sounds (SFX)
        self.collect_coin_sound = arcade.load_sound("sounds/coin1.wav")
        self.jump_sound = arcade.load_sound("sounds/jump1.wav")
        self.wall_hit_sound = arcade.load_sound("sounds/hit4.wav")
        self.ice_hit_sound = arcade.load_sound("sounds/hit2.wav")
        self.gun_sound = arcade.sound.load_sound("sounds/laser1.wav")

    def on_draw(self):
        """
        Render the screen.
        """
        self.frame_count += 1

        # This command has to happen before we start drawing
        arcade.start_render()

        if not self.paused_state:
            # Draw all the sprites.
            self.background_list.draw()
            self.wall_list.draw()
            self.platform_list.draw()
            self.ice_list.draw()
            self.coin_list.draw()
            self.npc_list.draw()
            self.player_list.draw()
            self.laser_list.draw()
        elif self.paused_state:
            self.background_list.draw()
            self.wall_list.draw()
            self.platform_list.draw()
            self.ice_list.draw()
            self.coin_list.draw()
            # Draw the paused menu texture
            arcade.draw_texture_rectangle(self.view_left + (SCREEN_WIDTH // 2), self.view_bottom + (SCREEN_HEIGHT // 2),
                                          530.0, 292.0, self.paused_mask)

        # Draw the background texture
        arcade.draw_texture_rectangle(self.view_left + (SCREEN_WIDTH // 2), self.view_bottom + (SCREEN_HEIGHT // 2),
                                      SCREEN_WIDTH, SCREEN_HEIGHT, self.menu_mask)

        if self.last_time and self.frame_count % 60 == 0:
            fps = 1.0 / (time.time() - self.last_time) * 60
            self.fps_message = f"FPS: {fps:5.0f}"

        if self.fps_message:
            arcade.draw_text(self.fps_message, self.view_left + 10, self.view_bottom + 40, arcade.color.BLACK, 14)

        if self.frame_count % 60 == 0:
            self.last_time = time.time()

        # Put the text on the screen.
        # Adjust the text position based on the view port so that we don't
        # scroll the text too.
        coins_collected = self.score
        output = f"Coins: {coins_collected}"
        arcade.draw_text(output, self.view_left + 400, self.view_bottom + 675, arcade.color.BLACK, 16)

        trees_saved = self.trees_saved
        output = f"Trees Saved: {trees_saved}"
        arcade.draw_text(output, self.view_left + 500, self.view_bottom + 675, arcade.color.BLACK, 16)

        # SHOW player (left,bottom) for debug
        """
        x_pos_output = self.player._get_left()
        output = f"X: {x_pos_output}"
        arcade.draw_text(output, self.view_left + 600, self.view_bottom + 550, arcade.color.BLACK, 16)

        y_pos_output = self.player._get_bottom()
        output = f"X: {y_pos_output}"
        arcade.draw_text(output, self.view_left + 600, self.view_bottom + 500, arcade.color.BLACK, 16)
        """

        if self.game_over:
            arcade.draw_text("Game Over", self.view_left + 200, self.view_bottom + 200, arcade.color.BLACK, 30)

    def on_key_press(self, key, modifiers):
        """

        """
        if key == arcade.key.ESCAPE:
            if self.paused_state == True:
                self.paused_state = False
                self.previously_paused = False
                self.music_player.queue(self.current_music_source)
                self.music_player.next_source()
                self.music_player.seek(self.current_music_time)
                self.music_player.play()
            elif self.paused_state == False:
                self.paused_state = True
        if not self.paused_state:
            if key == arcade.key.W:
                if self.physics_engine.can_jump():
                    self.player.change_y = JUMP_SPEED
                    arcade.play_sound(self.jump_sound)
            elif key == arcade.key.A:
                self.player.change_x = -MOVEMENT_SPEED
                self.player_facing_direction = "left"
            elif key == arcade.key.D:
                self.player.change_x = MOVEMENT_SPEED
                self.player_facing_direction = "right"
            # Boundary checks and player position reset for boundary encounter
            if self.player._get_left() <= self.player.boundary_left:
                self.player.change_x = 0
            elif self.player._get_right() >= self.player.boundary_right:
                self.player.change_x = 0

    def on_key_release(self, key, modifiers):
        """

        """
        if key == arcade.key.A or key == arcade.key.D:
            self.player.change_x = 0
        elif key == arcade.key.W:
            self.player.change_y = 0

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse moves.
        """
        if not self.paused_state:
            # Create a laser pulse
            if button == arcade.MOUSE_BUTTON_LEFT:
                arcade.play_sound(self.gun_sound)
                laser = arcade.Sprite("images/laser1t.png", scale=SPRITE_SCALING)

                laser.textures.append(arcade.load_texture("images/laser2t.png", scale=SPRITE_SCALING))
                laser.textures.append(arcade.load_texture("images/laser3t.png", scale=SPRITE_SCALING))
                laser.textures.append(arcade.load_texture("images/laser4t.png", scale=SPRITE_SCALING))
                laser.textures.append(arcade.load_texture("images/laser5t.png", scale=SPRITE_SCALING))

                # Position the laser pulse at the player's current location
                # ADD feature to account for player's facing direction and the destination
                # eg the player should only be able to fire in front of themselves and not behind
                start_x = self.player.center_x
                start_y = self.player.center_y
                laser.center_x = start_x
                laser.center_y = start_y

                # Get from the mouse the destination location for the laser pulse
                # IMPORTANT! If you have a scrolling screen, you will also need
                # to add in self.view_bottom and self.view_left.
                dest_x = x + self.view_left
                dest_y = y + self.view_bottom

                # Do math to calculate how to get the laser pulse to the destination.
                # Calculation the angle in radians between the start points
                # and end points. This is the angle the laser pulse will travel.
                x_diff = dest_x - start_x
                y_diff = dest_y - start_y
                angle = math.atan2(y_diff, x_diff)

                # Angle the laser pulse sprite so it doesn't look like it is flying
                # sideways.
                laser.angle = math.degrees(angle)
                '''print(f"Laser angle: {laser.angle:.2f}")
                print(f"X: {dest_x:.2f}")
                print(f"Y: {dest_y:.2f}")'''

                # Taking into account the angle, calculate our change_x
                # and change_y. Velocity is how fast the laser pulse travels.
                laser.change_x = math.cos(angle) * LASER_SPEED
                laser.change_y = math.sin(angle) * LASER_SPEED

                # Add the laser pulse to the appropriate lists
                self.laser_list.append(laser)

    def update(self, delta_time):
        """ Movement and game logic """

        # Game state eg. new, save, paused, game over, cut scene
        if self.game_over:
            self.music_player.queue(self.game_over_music)
            self.music_player.next_source()
            self.music_player.play()
        if self.paused_state:
            if self.previously_paused:
                if not self.music_player.playing:
                    self.music_player.queue(self.pause_menu_music)
                    self.music_player.play()
            elif not self.previously_paused:
                self.music_player.pause()
                self.current_music_time = self.music_player.time
                self.current_music_source = self.music_player.source
                self.music_player.queue(self.pause_menu_music)
                self.music_player.next_source()
                self.music_player.play()
                self.previously_paused = True
        if not self.game_over and not self.paused_state:
            # Call update to move the sprite
            # If using a physics engine, call update on it instead of the sprite
            # list.
            self.physics_engine.update()
            # Call update on all sprites
            self.laser_list.update()
            self.laser_list.update_animation()
            self.ice_list.update()
            self.player_list.update()
            self.coin_list.update()
            self.player_list.update_animation()
            if not self.music_player.playing:
                self.music_player.queue(self.level_music)
                self.music_player.play()

        # Boundary checks and player position reset for boundary encounter
        if self.player._get_left() <= self.player.boundary_left:
            self.player._set_left(self.player.boundary_left + 16)
            arcade.play_sound(self.wall_hit_sound)
        elif self.player._get_right() >= self.player.boundary_right:
            self.player._set_right(self.player.boundary_right - 16)
            arcade.play_sound(self.wall_hit_sound)

        coins_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coins_hit:
            coin.kill()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        # Loop through each laser pulse
        for laser in self.laser_list:
            # Check this laser pulse to see if it hit an iced tree
            laser_ice_hit_list = arcade.check_for_collision_with_list(laser, self.ice_list)
            # If it did, get rid of the laser pulse
            if len(laser_ice_hit_list) > 0:
                # For every iced tree we hit, add to the score and remove the ice
                for ice in laser_ice_hit_list:
                    laser.kill()
                    ice.kill()
                    arcade.play_sound(self.ice_hit_sound)
                    self.trees_saved += 1
            # Check this laser pulse to see if it hit a platform
            laser_platform_hit_list = arcade.check_for_collision_with_list(laser, self.platform_list)
            if len(laser_platform_hit_list) > 0:
                laser.kill()
            # Check this laser pulse to see if it hit a wall
            laser_wall_hit_list = arcade.check_for_collision_with_list(laser, self.wall_list)
            if len(laser_wall_hit_list) > 0:
                laser.kill()
            # If the laser pulse flies off-screen, remove it.
            if laser.bottom > self.height + self.view_bottom or laser.bottom < self.view_bottom or laser.left > self.view_left + self.width or laser.left < self.view_left:
                laser.kill()

        # --- Manage Scrolling ---

        # View port tracking
        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_LEFT_MARGIN
        if self.player.left < left_bndry:
            self.view_left -= left_bndry - self.player.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - VIEWPORT_RIGHT_MARGIN
        if self.player.right > right_bndry:
            self.view_left += self.player.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN_TOP
        if self.player.top > top_bndry:
            self.view_bottom += self.player.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN_BOTTOM
        if self.player.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player.bottom
            changed = True

        # Check if we need to scroll.
        if changed:
            self.view_left = int(self.view_left)
            self.view_bottom = int(self.view_bottom)
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
