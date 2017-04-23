#!/usr/bin/env python3

import pygame
import random
import json
import copy
import sys

pygame.mixer.pre_init(22050, -16, 2, 4096)
pygame.init()

# Window settings
TITLE = "Name of Game"
WIDTH = 960
HEIGHT = 640
FPS = 60
GRID_SIZE = 64

# Colors
TRANSPARENT = (0, 0, 0, 0)
DARK_CHALKY_BLUE = (16, 86, 103)
SKY_BLUE = (87, 0, 235)
WHITE = (255, 255, 255)

# Fonts
FONT_SM = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 32)
FONT_MD = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 64)
FONT_LG = pygame.font.Font("assets/fonts/thats_super.ttf", 72)

def load_image(file_path):
    img = pygame.image.load(file_path)
    img = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))

    return img

# Images
hero_img = load_image("assets/character/adventurer_walk1.png")

block_images = {"TL": load_image("assets/tiles/top_left.png"),
                "TM": load_image("assets/tiles/top_middle.png"),
                "TR": load_image("assets/tiles/top_right.png"),
                "ER": load_image("assets/tiles/end_right.png"),
                "EL": load_image("assets/tiles/end_left.png"),
                "TP": load_image("assets/tiles/top.png"),
                "CN": load_image("assets/tiles/center.png"),
                "LF": load_image("assets/tiles/lone_float.png"),
                "SP": load_image("assets/tiles/special.png")}

coin_img = load_image("assets/items/coin.png")
heart_img = load_image("assets/items/bandaid.png")
oneup_img = load_image("assets/items/first_aid.png")
flag_img = load_image("assets/items/flag.png")
flagpole_img = load_image("assets/items/flagpole.png")

monster_img1 = load_image("assets/enemies/monster-1.png")
monster_img2 = load_image("assets/enemies/monster-2.png")
monster_images = [monster_img1, monster_img2]

bear_img1 = load_image("assets/enemies/bear-1.png")
bear_img2 = pygame.transform.flip(bear_img1, 1, 0)
bear_images = [bear_img1, bear_img2]

background_img = pygame.image.load("assets/backgrounds/mountains.png")
h = background_img.get_height()
w = int(background_img.get_width() * HEIGHT / h)
background_img = pygame.transform.scale(background_img, (w, HEIGHT))

scenery_img = pygame.image.load("assets/backgrounds/forest.png")
h = scenery_img.get_height()
w = int(scenery_img.get_width() * HEIGHT / h)
scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT))

# Sounds
pygame.mixer.music.load("assets/sounds/theme_of_the wanderer.ogg")

JUMP_SOUND = pygame.mixer.Sound("assets/sounds/jump.wav")
COIN_SOUND = pygame.mixer.Sound("assets/sounds/pickup_coin.wav")
POWERUP_SOUND = pygame.mixer.Sound("assets/sounds/powerup.wav")
HURT_SOUND = pygame.mixer.Sound("assets/sounds/hurt.ogg")
DIE_SOUND = pygame.mixer.Sound("assets/sounds/death.wav")
LEVELUP_SOUND = pygame.mixer.Sound("assets/sounds/level_up.wav")
GAMEOVER_SOUND = pygame.mixer.Sound("assets/sounds/game_over.wav")


class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        size = [image.get_width(), image.get_height()]

        self.image = pygame.Surface(size, pygame.SRCALPHA, 32)
        self.image.blit(image, [0, 0])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Block(Entity):

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Character(Entity):

    def __init__(self, image):
        super().__init__(0, 0, image)

        self.speed = 5
        self.jump_power = 20

        self.vx = 0
        self.vy = 0

        self.score = 0
        self.lives = 3
        self.hearts = 3
        self.max_hearts = 3
        self.invincibility = 0

    def apply_gravity(self, level):
        self.vy += level.gravity

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > level.width:
            self.rect.right = level.width

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx = 0
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx = 0

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def process_coins(self, coins):
        hit_list = pygame.sprite.spritecollide(self, coins, True)

        for coin in hit_list:
            COIN_SOUND.play()
            self.score += coin.value

    def process_enemies(self, enemies):
        hit_list = pygame.sprite.spritecollide(self, enemies, False)

        if len(hit_list) > 0 and self.invincibility == 0:
            HURT_SOUND.play()
            self.hearts -= 1
            self.invincibility = int(0.5 * FPS)

    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            POWERUP_SOUND.play()
            p.apply(self)

    def check_flag(self, flag):
        hit_list = pygame.sprite.spritecollide(self, flag, False)

        got_it = len(hit_list) > 0

        if got_it:
            LEVELUP_SOUND.play()

        return got_it

    def die(self):
        self.lives -= 1

        if self.lives > 0:
            DIE_SOUND.play()
        else:
            GAMEOVER_SOUND.play()

    def respawn(self, level):
        self.rect.x = level.start_x
        self.rect.y = level.start_y
        self.hearts = self.max_hearts

    def update_status(self):
        if self.hearts == 0:
            self.die()
        if self.invincibility > 0:
            self.invincibility -= 1

    def move_left(self):
        self.vx = -self.speed

    def move_right(self):
        self.vx = self.speed

    def stop(self):
        self.vx = 0

    def jump(self, blocks):
        self.rect.y += 1

        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        if len(hit_list) > 0:
            self.vy = -1 * self.jump_power
            JUMP_SOUND.play()

        self.rect.y -= 1

    def update(self, level):
        self.apply_gravity(level)
        self.move_and_process_blocks(level.blocks)
        self.check_world_boundaries(level)

        self.process_enemies(level.enemies)
        self.process_coins(level.coins)
        self.process_powerups(level.powerups)

        self.update_status()

        level.completed = self.check_flag(level.flag)

class Coin(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 1

class Bear(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images = images

        self.vx = -2
        self.vy = 0

    def reverse(self):
        self.vx *= -1

    def apply_gravity(self, level):
        self.vy += level.gravity

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vy > 0:
                self.rect.bottom = block.rect.top
                self.vy = 0
            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

    def update_image(self):
        self.image.fill(TRANSPARENT)

        if self.vx < 0:
            self.image.blit(self.images[0], [0, 0])
        else:
            self.image.blit(self.images[1], [0, 0])

    def update(self, level, hero):
        distance = abs(self.rect.x - hero.rect.x)

        if distance < 2 * WIDTH:
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.update_image()

class Monster(Entity):
    def __init__(self, x, y, images):
        super().__init__(x, y, images[0])

        self.images = images

        self.vx = -2
        self.vy = 0

        self.ticks = 0
        self.current = 0

    def reverse(self):
        self.vx *= -1

    def apply_gravity(self, level):
        self.vy += level.gravity

    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.reverse()
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.reverse()

    def move_and_process_blocks(self, blocks):
        reverse = False

        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.reverse()
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.reverse()

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True

        for block in hit_list:
            if self.vy >= 0:
                self.rect.bottom = block.rect.top
                self.vy = 0

                if self.vx > 0 and self.rect.right <= block.rect.right:
                    reverse = False

                elif self.vx < 0 and self.rect.left >= block.rect.left:
                    reverse = False

            elif self.vy < 0:
                self.rect.top = block.rect.bottom
                self.vy = 0

        if reverse:
            self.reverse()

    def update_image(self):
        if self.ticks == 0:
            self.image.fill(TRANSPARENT)
            self.image.blit(self.images[self.current], [0, 0])
            self.current = (self.current + 1) % len(self.images)

        self.ticks = (self.ticks + 1) % (FPS / 3)

    def update(self, level, hero):
        distance = abs(self.rect.x - hero.rect.x)

        if distance < 2 * WIDTH:
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)
            self.update_image()

class OneUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.lives += 1

class Heart(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.hearts += 1
        character.hearts = max(character.hearts, character.max_hearts)

class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

class Level():

    def __init__(self):
        self.blocks = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.flag = pygame.sprite.Group()

    def load(self, file_path):
        with open(file_path, 'r') as f:
            data = f.read()

        map_data = json.loads(data)

        self.width, self.height = map_data['width'] * GRID_SIZE, map_data['height'] * GRID_SIZE

        self.start_x, self.start_y = map_data['start'][0] * GRID_SIZE, map_data['start'][1] * GRID_SIZE

        for item in map_data['blocks']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = block_images[item[2]]
            self.blocks.add(Block(x, y, img))

        for item in map_data['coins']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.coins.add(Coin(x, y, coin_img))

        for item in map_data['bears']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.enemies.add(Bear(x, y, bear_images))

        for item in map_data['monsters']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.enemies.add(Monster(x, y, monster_images))

        for item in map_data['oneups']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            img = oneup_img
            self.powerups.add(OneUp(x, y, img))

        for item in map_data['hearts']:
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE
            self.powerups.add(Heart(x, y, heart_img))

        for i, item in enumerate(map_data['flag']):
            x, y = item[0] * GRID_SIZE, item[1] * GRID_SIZE

            if i == 0:
                img = flag_img
            else:
                img = flagpole_img

            self.flag.add(Flag(x, y, img))

        self.background_img = None
        self.scenery_img = None

        self.gravity = map_data['gravity']

        self.completed = False

    def reset(self):
        pass

class Game():

    START = 0
    PLAYING = 1
    PAUSED = 2
    COMPLETE = 3
    GAME_OVER = 4

    def __init__(self, levels):
        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.levels = levels

        self.stage = Game.START
        self.done = False
        self.current_level = 0

    def start(self):
        self.level = Level()
        self.level.load(self.levels[self.current_level])

        self.hero = Character(hero_img)

        self.hero.rect.x, self.hero.rect.y = self.level.start_x, self.level.start_y

        self.active_sprites = pygame.sprite.Group()
        self.inactive_sprites = pygame.sprite.Group()

        self.active_sprites.add(self.level.coins, self.level.enemies, self.level.powerups)
        self.inactive_sprites.add(self.level.blocks, self.level.flag)

        self.background_layer = pygame.Surface([self.level.width, self.level.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([self.level.width, self.level.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([self.level.width, self.level.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([self.level.width, self.level.height], pygame.SRCALPHA, 32)
        self.foreground_layer = None
        self.stats_layer = pygame.Surface([WIDTH, HEIGHT], pygame.SRCALPHA, 32)

        for i in range(0, self.level.width, background_img.get_width()):
            self.background_layer.blit(background_img, [i, 0])

        for i in range(0, self.level.width, scenery_img.get_width()):
            self.scenery_layer.blit(scenery_img, [i, 0])

        self.inactive_sprites.draw(self.inactive_layer)

    def reset_level(self):
        pass

    def advance_level(self):
        pass

    def display_splash(self, surface):
        line1 = FONT_LG.render(TITLE, 1, DARK_CHALKY_BLUE)
        line2 = FONT_SM.render("Press any key to start.", 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_message(self, surface, primary_text, secondary_text):
        line1 = FONT_MD.render(primary_text, 1, WHITE)
        line2 = FONT_SM.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;

        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;

        surface.blit(line1, (x1, y1))
        surface.blit(line2, (x2, y2))

    def display_stats(self, surface):
        hearts_text = FONT_SM.render("Hearts: " + str(self.hero.hearts), 1, WHITE)
        lives_text = FONT_SM.render("Lives: " + str(self.hero.lives), 1, WHITE)
        score_text = FONT_SM.render("Score: " + str(self.hero.score), 1, WHITE)

        surface.blit(score_text, (WIDTH - score_text.get_width() - 32, 32))
        surface.blit(hearts_text, (32, 32))
        surface.blit(lives_text, (32, 64))

    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.done = True

            elif event.type == pygame.KEYDOWN:
                if self.stage == Game.START:
                    self.stage = Game.PLAYING

                    pygame.mixer.music.play(-1)

                elif self.stage == Game.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self.hero.jump(self.level.blocks)

                elif self.stage == Game.COMPLETE:
                    pass

                elif self.stage == Game.GAME_OVER:
                    pass

        pressed = pygame.key.get_pressed()

        if self.stage == Game.PLAYING:
            if pressed[pygame.K_LEFT]:
                self.hero.move_left()
            elif pressed[pygame.K_RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()

    def update(self):
        if self.stage == Game.PLAYING:
            self.hero.update(self.level)
            self.level.enemies.update(self.level, self.hero)

        if self.level.completed:
            self.stage = Game.COMPLETE
            pygame.mixer.music.stop()
        elif self.hero.lives == 0:
            self.stage = Game.GAME_OVER
            pygame.mixer.music.stop()
        elif self.hero.hearts == 0:
            self.hero.respawn(self.level)

    def draw(self):
        offset_x, offset_y = self.calculate_offset()

        self.active_layer.fill(TRANSPARENT)
        self.active_sprites.draw(self.active_layer)

        if self.hero.invincibility % 3 < 2:
            self.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

        self.window.blit(self.background_layer, [offset_x / 3, offset_y])
        self.window.blit(self.scenery_layer, [offset_x / 2, offset_y])
        self.window.blit(self.inactive_layer, [offset_x, offset_y])
        self.window.blit(self.active_layer, [offset_x, offset_y])
        self.display_stats(self.window)

        if self.stage == Game.START:
            self.display_splash(self.window)
        elif self.stage == Game.PAUSED:
            pass
        elif self.stage == Game.COMPLETE:
            self.display_message(self.window, "Level Complete", "Press 'C' to continue.")
        elif self.stage == Game.GAME_OVER:
            self.display_message(self.window, "Game Over", "Press 'R' to restart.")

        pygame.display.flip()

    def loop(self):
        while not self.done:
            self.process_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

def main():
    # Levels
    levels = ["level-1.json"]

    # Start game
    game = Game(levels)
    game.start()
    game.loop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
