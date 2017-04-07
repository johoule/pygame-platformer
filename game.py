import pygame
import random
import copy

pygame.mixer.pre_init(22050, -16, 2, 4096)
pygame.init()

# Window settings
TITLE = "Name of Game"
WIDTH = 960
HEIGHT = 640
FPS = 60

# Colors
TRANSPARENT = (0, 0, 0, 0)
DARK_CHALKY_BLUE = (16, 86, 103)
SKY_BLUE = (87, 0, 235)
WHITE = (255, 255, 255)

# Fonts
FONT_SM = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 32)
FONT_MD = pygame.font.Font("assets/fonts/minya_nouvelle_bd.ttf", 64)
FONT_LG = pygame.font.Font("assets/fonts/thats_super.ttf", 72)

# Images
hero_img = pygame.image.load("assets/character/adventurer_walk1.png")
hero_img = pygame.transform.scale(hero_img, (64, 64))

TL = pygame.image.load("assets/tiles/top_left.png")
TM = pygame.image.load("assets/tiles/top_middle.png")
TR = pygame.image.load("assets/tiles/top_right.png")
ER = pygame.image.load("assets/tiles/end_right.png")
EL = pygame.image.load("assets/tiles/end_left.png")
TP = pygame.image.load("assets/tiles/top.png")
CN = pygame.image.load("assets/tiles/center.png")
LF = pygame.image.load("assets/tiles/lone_float.png")
SP = pygame.image.load("assets/tiles/special.png")

coin_img = pygame.image.load("assets/items/coin.png")
coin_img = pygame.transform.scale(coin_img, (64, 64))

heart_img = pygame.image.load("assets/items/bandaid.png")
heart_img = pygame.transform.scale(heart_img, (64, 64))

oneup_img = pygame.image.load("assets/items/first_aid.png")
oneup_img = pygame.transform.scale(oneup_img, (64, 64))

flag_img = pygame.image.load("assets/items/flag.png")
flag_img = pygame.transform.scale(flag_img, (64, 64))

flagpole_img = pygame.image.load("assets/items/flagpole.png")
flagpole_img = pygame.transform.scale(flagpole_img, (64, 64))

monster_img1 = pygame.image.load("assets/enemies/monster-1.png")
monster_img2 = pygame.image.load("assets/enemies/monster-2.png")
monster_img1 = pygame.transform.scale(monster_img1, (64, 64))
monster_img2 = pygame.transform.scale(monster_img2, (64, 64))
monster_images = [monster_img1, monster_img2]

bear_img1 = pygame.image.load("assets/enemies/bear-1.png")
bear_img1 = pygame.transform.scale(bear_img1, (64, 64))
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

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_SPACE


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

    def __init__(self, x, y, image):
        super().__init__(x, y, image)

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

    def apply_gravity(self, level):
        self.vy += level.gravity
    
    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx *= -1
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.vx *= -1

    def move_and_process_blocks(self, blocks):
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx *= -1
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx *= -1

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
        
    def apply_gravity(self, level):
        self.vy += level.gravity
    
    def check_world_boundaries(self, level):
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx *= -1
        elif self.rect.right > level.width:
            self.rect.right = level.width
            self.vx *= -1

    def move_and_process_blocks(self, blocks):
        reverse = False
        
        self.rect.x += self.vx
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        for block in hit_list:
            if self.vx > 0:
                self.rect.right = block.rect.left
                self.vx *= -1
            elif self.vx < 0:
                self.rect.left = block.rect.right
                self.vx *= -1

        self.rect.y += self.vy
        hit_list = pygame.sprite.spritecollide(self, blocks, False)

        reverse = True
        
        for block in hit_list:
            self.rect.bottom = block.rect.top
            self.vy = 0
            
            if self.vx > 0 and self.rect.right <= block.rect.right:
                reverse = False
                    
            elif self.vx < 0 and self.rect.left >= block.rect.left:
                reverse = False         

        if reverse:
            self.vx *= -1
    
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
    
    def __init__(self, blocks, coins, enemies, powerups, flag):
        self.blocks = blocks
        self.coins = coins
        self.enemies = enemies
        self.powerups = powerups
        self.flag = flag

        self.starting_coins = copy.deepcopy(coins)
        self.starting_enemies = copy.deepcopy(enemies)
        self.starting_powerups = copy.deepcopy(powerups)

        self.active_sprites = pygame.sprite.Group()
        self.active_sprites.add(self.coins, self.enemies, self.powerups)

        self.inactive_sprites = pygame.sprite.Group()
        self.inactive_sprites.add(blocks, flag)

        self.width, self.height = 2048, 640
        self.start_x, self.start_y = 500, 512
        
        self.completed = False
        self.gravity = 1


class Game():

    START = 0
    PLAYING = 1
    COMPLETE = 2
    GAME_OVER = 3

    def __init__(self, hero):
        self.hero = hero

        self.window = pygame.display.set_mode([WIDTH, HEIGHT])
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.stage = Game.START
        self.running = True
        
    def start(self, level):
        self.level = level
        self.hero.respawn(self.level)
        
        self.background_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)
        self.scenery_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)
        self.inactive_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)
        self.active_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)
        self.foreground_layer = None
        self.stats_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)
        self.splash_layer = pygame.Surface([level.width, level.height], pygame.SRCALPHA, 32)

        for i in range(0, level.width, background_img.get_width()):
            self.background_layer.blit(background_img, [i, 0])
        
        for i in range(0, level.width, scenery_img.get_width()):
            self.scenery_layer.blit(scenery_img, [i, 0])
        
        self.level.inactive_sprites.draw(self.inactive_layer)
        
        line1 = FONT_LG.render(TITLE, 1, DARK_CHALKY_BLUE)
        line2 = FONT_SM.render("Press any key to start.", 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;
        
        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;
        
        self.splash_layer.blit(line1, (x1, y1))
        self.splash_layer.blit(line2, (x2, y2))

    def display_message(self, primary_text, secondary_text):
        line1 = FONT_MD.render(primary_text, 1, WHITE)
        line2 = FONT_SM.render(secondary_text, 1, WHITE)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;
        
        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;
        
        self.window.blit(line1, (x1, y1))
        self.window.blit(line2, (x2, y2))
    
    def update_stats(self):
        hearts_text = FONT_SM.render("Hearts: " + str(self.hero.hearts), 1, WHITE)
        lives_text = FONT_SM.render("Lives: " + str(self.hero.lives), 1, WHITE)
        score_text = FONT_SM.render("Score: " + str(self.hero.score), 1, WHITE)

        self.stats_layer.fill(TRANSPARENT)
        self.stats_layer.blit(score_text, (WIDTH - score_text.get_width() - 32, 32))
        self.stats_layer.blit(hearts_text, (32, 32))
        self.stats_layer.blit(lives_text, (32, 64))

    def calculate_offset(self):
        x = -1 * self.hero.rect.centerx + WIDTH / 2

        if self.hero.rect.centerx < WIDTH / 2:
            x = 0
        elif self.hero.rect.centerx > self.level.width - WIDTH / 2:
            x = -1 * self.level.width + WIDTH

        return x, 0

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.stage == Game.START:
                    self.stage = Game.PLAYING

                    pygame.mixer.music.play(-1)
                    
                elif self.stage == Game.PLAYING:
                    if event.key == JUMP:
                        JUMP_SOUND.play()
                        self.hero.jump(self.level.blocks)
                        
                elif self.stage == Game.COMPLETE:
                    pass
                        
                elif self.stage == Game.GAME_OVER:
                    pass
                    
        pressed = pygame.key.get_pressed()
        
        if self.stage == Game.PLAYING:
            if pressed[LEFT]:
                self.hero.move_left()
            elif pressed[RIGHT]:
                self.hero.move_right()
            else:
                self.hero.stop()
        
    def loop(self):
        while self.running:
            # Event handling
            self.process_input()

            # Game Logic
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

            self.update_stats()
            
            # Drawing
            offset_x, offset_y = self.calculate_offset()

            self.active_layer.fill(TRANSPARENT)
            self.level.active_sprites.draw(self.active_layer)

            if self.hero.invincibility % 3 < 2:
                self.active_layer.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

            self.window.blit(self.background_layer, [offset_x / 3, offset_y])
            self.window.blit(self.scenery_layer, [offset_x / 2, offset_y])
            self.window.blit(self.inactive_layer, [offset_x, offset_y])
            self.window.blit(self.active_layer, [offset_x, offset_y])
            self.window.blit(self.stats_layer, [0, 0])

            if self.stage == Game.START:
                self.window.blit(self.splash_layer, [0, 0])
            elif self.stage == Game.COMPLETE:
                self.display_message("Level Complete", "Press 'C' to continue.")
            elif self.stage == Game.GAME_OVER:
                self.display_message("Game Over", "Press 'R' to restart.")

            # Update window
            pygame.display.update()
            self.clock.tick(FPS)

        # Close window on quit
        pygame.quit ()


def main():
    # Make sprites
    ''' hero '''
    hero = Character(500, 512, hero_img)

    ''' blocks '''
    blocks = pygame.sprite.Group()
     
    for i in range(0, WIDTH * 100, 64):
        b = Block(i, 576, TM)
        blocks.add(b)

    blocks.add(Block(192, 448, EL))
    blocks.add(Block(256, 448, TM))
    blocks.add(Block(320, 448, ER))

    blocks.add(Block(448, 320, EL))
    blocks.add(Block(512, 320, ER))
    
    blocks.add(Block(792, 448, LF))
    blocks.add(Block(896, 320, LF))

    blocks.add(Block(1024, 192, EL))
    blocks.add(Block(1088, 192, TM))
    blocks.add(Block(1152, 192, TM))
    blocks.add(Block(1216, 192, TM))
    blocks.add(Block(1280, 192, ER))

    blocks.add(Block(1536, 512, TL))
    blocks.add(Block(1600, 448, TL))
    blocks.add(Block(1600, 512, CN))
    blocks.add(Block(1664, 384, TP))
    blocks.add(Block(1664, 448, CN))
    blocks.add(Block(1664, 512, CN))

    ''' coins '''
    coins = pygame.sprite.Group()

    coins.add(Coin(256, 320, coin_img))
    
    coins.add(Coin(1024, 384, coin_img))
    coins.add(Coin(1152, 384, coin_img))
    coins.add(Coin(1280, 384, coin_img))

    ''' enemies '''
    enemies = pygame.sprite.Group()

    enemies.add(Bear(512, 256, bear_images))
    enemies.add(Bear(832, 512, bear_images))
    enemies.add(Monster(1152, 128, monster_images))

    for i in range(200):
        r = random.randint(3000, 50000)
        enemies.add(Monster(r, 512, monster_images))
        
    ''' powerups '''
    powerups = pygame.sprite.Group()

    powerups.add(OneUp(448, 256, oneup_img))
    powerups.add(Heart(1152, 128, heart_img))

    ''' goal '''
    flag = pygame.sprite.Group()
    flag.add(Flag(1920, 320, flag_img))
    flag.add(Flag(1920, 384, flagpole_img))
    flag.add(Flag(1920, 448, flagpole_img))
    flag.add(Flag(1920, 512, flagpole_img))

    # Make a level
    level = Level(blocks, coins, enemies, powerups, flag)

    # Start game
    game = Game(hero)
    game.start(level)
    game.loop()


if __name__ == "__main__":
    main()
    
