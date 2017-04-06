import pygame
import random

pygame.mixer.pre_init(22050, -16, 2, 4096)
pygame.init()

# Window settings
TITLE = "Name of Game"
WIDTH = 960
HEIGHT = 640
FPS = 60

# Colors
TRANSPARENT = (0, 0, 0, 0)
SKY_BLUE = (135, 206, 235)
BLACK = (0, 0, 0)

# Fonts
FONT_SM = pygame.font.Font("assets/prstart.ttf", 16)
FONT_MD = pygame.font.Font("assets/prstart.ttf", 32)
FONT_LG = pygame.font.Font("assets/prstart.ttf", 64)

# Images
hero_img = pygame.image.load("assets/player.png")
hero_img = pygame.transform.scale(hero_img, (64, 64))

block_img = pygame.image.load("assets/block.png")
block_img = pygame.transform.scale(block_img, (64, 64))

coin_img = pygame.image.load("assets/coin.png")
coin_img = pygame.transform.scale(coin_img, (64, 64))

heart_img = pygame.image.load("assets/health_potion.png")
heart_img = pygame.transform.scale(heart_img, (64, 64))

oneup_img = pygame.image.load("assets/oneup_potion.png")
oneup_img = pygame.transform.scale(oneup_img, (64, 64))

flag_img = pygame.image.load("assets/flag.png")
flag_img = pygame.transform.scale(flag_img, (64, 64))

flagpole_img = pygame.image.load("assets/flagpole.png")
flagpole_img = pygame.transform.scale(flagpole_img, (64, 64))

monster_img = pygame.image.load("assets/monster.png")
monster_img = pygame.transform.scale(monster_img, (64, 64))

slime_img = pygame.image.load("assets/slime.png")
slime_img = pygame.transform.scale(slime_img, (64, 64))

background_img = pygame.image.load("assets/background.png")
h = background_img.get_height()
w = int(background_img.get_width() * HEIGHT / h)
background_img = pygame.transform.scale(background_img, (w, HEIGHT))

scenery_img = pygame.image.load("assets/forest.png")
h = scenery_img.get_height()
w = int(scenery_img.get_width() * HEIGHT / h // 2)
scenery_img = pygame.transform.scale(scenery_img, (w, HEIGHT // 2))

# Sounds
pygame.mixer.music.load("assets/theme_of_the wanderer.ogg")

JUMP_SOUND = pygame.mixer.Sound("assets/jump.wav")
COIN_SOUND = pygame.mixer.Sound("assets/pickup_coin.wav")
POWERUP_SOUND = pygame.mixer.Sound("assets/powerup.wav")
HIT_SOUND = None
DIE_SOUND = None

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_SPACE


class Entity(pygame.sprite.Sprite):

    def __init__(self, x, y, image):
        super().__init__()

        self.image = pygame.Surface([64, 64], pygame.SRCALPHA, 32)
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
            self.hearts -= 1
            self.invincibility = int(0.5 * FPS)

    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            POWERUP_SOUND.play()
            p.apply(self)

    def check_flag(self, flag):
        hit_list = pygame.sprite.spritecollide(self, flag, False)
        
        return len(hit_list) > 0

    def die(self):
        self.lives -= 1
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


class Monster(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

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
    
    def update(self, level, hero):
        distance = abs(self.rect.x - hero.rect.x)

        if distance < 2 * WIDTH:
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)       

class Slime(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

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
    
    def update(self, level, hero):
        distance = abs(self.rect.x - hero.rect.x)

        if distance < 2 * WIDTH:
            self.apply_gravity(level)
            self.move_and_process_blocks(level.blocks)
            self.check_world_boundaries(level)           

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

        
class Star(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.invincibility = 4 * FPS

        
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

        self.active_sprites = pygame.sprite.Group()
        self.active_sprites.add(coins, enemies, powerups)

        self.inactive_sprites = pygame.sprite.Group()
        self.inactive_sprites.add(blocks, flag)

        self.width = 1920
        self.height = 640
        
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
            self.scenery_layer.blit(scenery_img, [i, HEIGHT // 2])
        
        self.level.inactive_sprites.draw(self.inactive_layer)
        
        line1 = FONT_LG.render(TITLE, 1, BLACK)
        line2 = FONT_SM.render("Press any key to start.", 1, BLACK)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;
        
        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;
        
        self.splash_layer.blit(line1, (x1, y1))
        self.splash_layer.blit(line2, (x2, y2))

    def display_message(self, primary_text, secondary_text):
        line1 = FONT_MD.render(primary_text, 1, BLACK)
        line2 = FONT_SM.render(secondary_text, 1, BLACK)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;
        
        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;
        
        self.window.blit(line1, (x1, y1))
        self.window.blit(line2, (x2, y2))
    
    def update_stats(self):
        hearts_text = FONT_SM.render("Hearts: " + str(self.hero.hearts), 1, BLACK)
        lives_text = FONT_SM.render("Lives: " + str(self.hero.lives), 1, BLACK)
        score_text = FONT_SM.render("Score: " + str(self.hero.score), 1, BLACK)

        self.stats_layer.fill(TRANSPARENT)
        self.stats_layer.blit(score_text, (WIDTH - score_text.get_width() - 32, 32))
        self.stats_layer.blit(hearts_text, (32, 32))
        self.stats_layer.blit(lives_text, (32, 64))

    def calculate_offset(self):
        active_rect = self.active_layer.get_rect()
        hero_rect = self.hero.rect
        
        x = -1 * hero_rect.centerx + WIDTH / 2

        if hero_rect.centerx < WIDTH / 2:
            x = 0
        elif hero_rect.centerx > active_rect.right - WIDTH / 2:
            x = -1 * active_rect.right + WIDTH

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
                self.level.active_sprites.update(self.level, self.hero)

            if self.level.completed:
                self.stage = Game.COMPLETE

            if self.hero.lives == 0:
                self.stage = Game.GAME_OVER

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
    ''' our hero '''
    hero = Character(500, 512, hero_img)

    ''' blocks '''
    blocks = pygame.sprite.Group()
     
    for i in range(0, WIDTH * 200, 64):
        b = Block(i, 576, block_img)
        blocks.add(b)

    blocks.add(Block(192, 448, block_img))
    blocks.add(Block(256, 448, block_img))
    blocks.add(Block(320, 448, block_img))

    blocks.add(Block(448, 320, block_img))
    blocks.add(Block(512, 320, block_img))
    
    blocks.add(Block(792, 448, block_img))
    blocks.add(Block(896, 320, block_img))

    blocks.add(Block(1024, 196, block_img))
    blocks.add(Block(1088, 196, block_img))
    blocks.add(Block(1152, 196, block_img))
    blocks.add(Block(1216, 196, block_img))
    blocks.add(Block(1280, 196, block_img))

    blocks.add(Block(1536, 512, block_img))
    blocks.add(Block(1600, 448, block_img))
    blocks.add(Block(1600, 512, block_img))
    blocks.add(Block(1664, 384, block_img))
    blocks.add(Block(1664, 448, block_img))
    blocks.add(Block(1664, 512, block_img))

    ''' coins '''
    coins = pygame.sprite.Group()

    coins.add(Coin(256, 320, coin_img))
    
    coins.add(Coin(1024, 384, coin_img))
    coins.add(Coin(1152, 384, coin_img))
    coins.add(Coin(1280, 384, coin_img))

    ''' enemies '''
    enemies = pygame.sprite.Group()

    enemies.add(Monster(512, 256, monster_img))
    enemies.add(Monster(832, 512, monster_img))
    enemies.add(Slime(1152, 128, slime_img))

    for i in range(200):
        r = random.randint(3000, 50000)
        enemies.add(Monster(r, 512, monster_img))
        
    ''' powerups '''
    powerups = pygame.sprite.Group()

    powerups.add(OneUp(448, 256, oneup_img))
    powerups.add(Heart(1152, 128, heart_img))

    ''' goal '''
    flag = pygame.sprite.Group()
    flag.add(Flag(1856, 320, flag_img))
    flag.add(Flag(1856, 384, flagpole_img))
    flag.add(Flag(1856, 448, flagpole_img))
    flag.add(Flag(1856, 512, flagpole_img))

    # Make a level
    level = Level(blocks, coins, enemies, powerups, flag)

    # Start game
    game = Game(hero)
    game.start(level)
    game.loop()


if __name__ == "__main__":
    main()
    
