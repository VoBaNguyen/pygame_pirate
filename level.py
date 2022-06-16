import pygame
from tile import Tile, StaticTile, Crate, AnimatedTile, Coin, Palm
from settings import tile_size, screen_width, screen_height
from player import Player
from particle import ParticleEffect
from support import import_csv_layout, import_cut_graphics
from enemy import Enemy
from decoration import Sky, Water, Clouds


class Level:

    def __init__(self, level_data, surface):
        # Level setup
        self.display_surface = surface
        self.world_shift = -6
        self.current_x = 0

        # Dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # Player
        player_layout = import_csv_layout(level_data["player"])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout)

        # Terrain
        terrain_layout = import_csv_layout(level_data["terrain"])
        self.terrain_sprites = self.create_tile_group(
            terrain_layout, 'terrain')

        # Grass setup
        grass_layout = import_csv_layout(level_data["grass"])
        self.grass_sprites = self.create_tile_group(
            grass_layout, 'grass')

        # Crate setup
        crate_layout = import_csv_layout(level_data["crates"])
        self.crate_sprites = self.create_tile_group(
            crate_layout, 'crates')

        # Coins
        coin_layout = import_csv_layout(level_data["coins"])
        self.coin_sprites = self.create_tile_group(
            coin_layout, 'coins')

        # Foreground palms
        fg_palm_layout = import_csv_layout(level_data["fg palms"])
        self.fg_palm_sprites = self.create_tile_group(
            fg_palm_layout, 'fg palms')

        # Bg palms
        bg_palm_layout = import_csv_layout(level_data["bg palms"])
        self.bg_palm_sprites = self.create_tile_group(
            bg_palm_layout, 'bg palms')

        # Enemies
        enemy_layout = import_csv_layout(level_data["enemies"])
        self.enemy_sprites = self.create_tile_group(
            enemy_layout, 'enemies')

        # Constraints
        constraint_layout = import_csv_layout(level_data["constraints"])
        self.constraint_sprites = self.create_tile_group(
            constraint_layout, 'constraints')

        # decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0])*tile_size
        self.water = Water(screen_height-20, level_width)
        self.clouds = Clouds(400, level_width, 20)

    # Setup level graphs

    def create_tile_group(self, layout, type):
        # Import cut graphs
        terrain_tile_list = import_cut_graphics(
            'D:\\python\\pygame_pirate\\2D-Mario-style-platformer\\2 - Level\\2 - Level\\graphics\\terrain\\terrain_tiles.png')
        grass_tile_list = import_cut_graphics(
            'D:\\python\\pygame_pirate\\2D-Mario-style-platformer\\2 - Level\\2 - Level\\graphics\\decoration\\grass\\grass.png')

        sprite_group = pygame.sprite.Group()
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != "-1":
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == 'terrain':
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    elif type == 'grass':
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)

                    elif type == 'crates':
                        sprite = Crate(tile_size, x, y)

                    elif type == 'coins':
                        if val == '0':
                            sprite = Coin(
                                tile_size, x, y, "D:\\python\\pygame_pirate\\2-level\\graphics\\coins\\gold")
                        if val == '1':
                            sprite = Coin(
                                tile_size, x, y, "D:\\python\\pygame_pirate\\2-level\\graphics\\coins\\silver")

                    elif type == 'fg palms':
                        if val == '0':
                            sprite = Palm(
                                tile_size, x, y, "D:\\python\\pygame_pirate\\2-level\\graphics\\terrain\\palm_small", 38)
                        elif val == '1':
                            sprite = Palm(
                                tile_size, x, y, "D:\\python\\pygame_pirate\\2-level\\graphics\\terrain\\palm_large", 64)

                    elif type == 'bg palms':
                        sprite = Palm(
                            tile_size, x, y, "D:\\python\\pygame_pirate\\2-level\\graphics\\terrain\\palm_bg", 38)

                    elif type == 'enemies':
                        sprite = Enemy(tile_size, x, y)

                    elif type == 'constraints':
                        sprite = Tile([x, y], tile_size)

                    sprite_group.add(sprite)

        return sprite_group

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, "jump")
        self.dust_sprite.add(jump_particle_sprite)

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        # Player not on ground - But after checking vertical collision, player is now on the ground
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite.sprites():
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 18)
            else:
                offset = pygame.math.Vector2(-10, 18)
            fall_dust_particle = ParticleEffect(
                self.player.sprite.rect.midbottom - offset, "land")
            self.dust_sprite.add(fall_dust_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < screen_width/4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > screen_width - (screen_width/4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_sprites.sprites(
        ) + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (player.rect.left < self.current_x or player.direction.x >= 0):
            self.player.on_left = False
        if player.on_right and (player.rect.right < self.current_x or player.direction.x <= 0):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites(
        ) + self.crate_sprites.sprites() + self.fg_palm_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.direction.y = 0
                    player.rect.bottom = sprite.rect.top
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

        if player.on_ceiling and player.direction.y > 0:
            player.on_ceiling = False

    def player_setup(self, layout):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == "0":
                    sprite = Player(
                        (x, y), self.display_surface, self.create_jump_particles)
                    self.player.add(sprite)

                if val == "1":
                    hat_surface = pygame.image.load(
                        "D:\\python\\pygame_pirate\\2D-Mario-style-platformer\\2 - Level\\2 - Level\\graphics\\character\\hat.png").convert_alpha()
                    sprite = StaticTile(tile_size, x, y, hat_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def run(self):

        # Decoration
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # Create palm
        self.fg_palm_sprites.draw(self.display_surface)
        self.fg_palm_sprites.update(self.world_shift)

        # Create palm bg
        self.bg_palm_sprites.draw(self.display_surface)
        self.bg_palm_sprites.update(self.world_shift)

        # Enemies
        self.enemy_sprites.draw(self.display_surface)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.update(self.world_shift)

        # # Constraint
        # self.constraint_sprites.draw(self.display_surface)

        # Draw terrain layout
        self.terrain_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)

        # Crate grass
        self.crate_sprites.draw(self.display_surface)
        self.crate_sprites.update(self.world_shift)

        # Draw grass
        self.grass_sprites.draw(self.display_surface)
        self.grass_sprites.update(self.world_shift)

        # Create coin
        self.coin_sprites.draw(self.display_surface)
        self.coin_sprites.update(self.world_shift)

        # Water
        self.water.draw(self.display_surface, self.world_shift)

        # Dust particles

        # Player
        self.player.update()
        self.horizontal_movement_collision()
        self.get_player_on_ground()

        self.vertical_movement_collision()
        self.create_landing_dust()

        # Dust partice
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        self.scroll_x()
        self.goal.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.player.draw(self.display_surface)
