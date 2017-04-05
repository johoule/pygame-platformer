import pygame

pygame.init()

# Window settings
WIDTH = 960
HEIGHT = 640
window = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("My Platform Game")
FPS = 60
clock = pygame.time.Clock()

# Colors
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

oneup_img = pygame.image.load("assets/oneup_potion.png")
oneup_img = pygame.transform.scale(oneup_img, (64, 64))

flag_img = pygame.image.load("assets/flag.png")
flag_img = pygame.transform.scale(flag_img, (64, 64))

flagpole_img = pygame.image.load("assets/flagpole.png")
flagpole_img = pygame.transform.scale(flagpole_img, (64, 64))

monster_img = pygame.image.load("assets/monster.png")
monster_img = pygame.transform.scale(monster_img, (64, 64))

# Sounds
music = None
jump = None
kill_enemy = None
get_coin = None
get_hit = None
die = None

# Controls
LEFT = pygame.K_LEFT
RIGHT = pygame.K_RIGHT
JUMP = pygame.K_SPACE

# Stages
START = 0
PLAYING = 1
LEVEL_COMPLETE = 2
GAME_OVER = 3

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

    def check_world_boundaries(self, world):
        world_rect = world.get_rect()
        
        if self.rect.left < world_rect.left:
            self.rect.left = world_rect.left
        elif self.rect.right > world_rect.right:
            self.rect.right = world_rect.right
    
    def process_blocks(self, blocks):
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
            self.score += coin.value
            
    def process_enemies(self, enemies):
        hit_list = pygame.sprite.spritecollide(self, enemies, False)

        if len(hit_list) > 0 and self.invincibility == 0:
            self.hearts -= 1
            self.invincibility = int(0.5 * FPS)

    def process_powerups(self, powerups):
        hit_list = pygame.sprite.spritecollide(self, powerups, True)

        for p in hit_list:
            p.apply(self)

    def check_flag(self, flag):
        hit_list = pygame.sprite.spritecollide(self, flag, False)
        
        return len(hit_list) > 0

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

    def die(self):
        print("Ouch")
    
    def update(self, level):
        self.apply_gravity(level)
        self.process_blocks(level.blocks)
        self.process_enemies(level.enemies)
        self.process_coins(level.coins)
        self.process_powerups(level.powerups)
        self.check_world_boundaries(level.world)

        level.completed = self.check_flag(level.flag)

        if self.invincibility > 0:            
            self.invincibility -= 1
 
        if self.hearts == 0:
            self.die()

        
class Coin(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 1


class Monster(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def update(self, level):
        pass
    
class OneUp(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.lives += 1


class Star(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

    def apply(self, character):
        character.invincibility = 4 * FPS

        
class Flag(Entity):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        self.value = 10


class Level():
    
    def __init__(self, blocks, coins, enemies, powerups, flag):
        self.blocks = blocks
        self.coins = coins
        self.enemies = enemies
        self.powerups = powerups
        self.flag = flag

        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(blocks, coins, enemies, coins, powerups, flag)

        self.world = pygame.Surface([1920, 640])
        
        self.completed = False
        self.gravity = 1

class Game():

    def __init__(self, hero, level):
        self.hero = hero
        self.level = level
        
        self.stage = START

    def display_start(self):
        line1 = FONT_LG.render("NAME OF GAME", 1, BLACK)
        line2 = FONT_SM.render("Press any key to start.", 1, BLACK)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;
        
        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;
        
        window.blit(line1, (x1, y1))
        window.blit(line2, (x2, y2))

    def display_level_complete(self):
        line1 = FONT_MD.render("Level Complete!", 1, BLACK)
        line2 = FONT_SM.render("Press 'C' to continue.", 1, BLACK)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;
        
        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;
        
        window.blit(line1, (x1, y1))
        window.blit(line2, (x2, y2))
        
    def display_end(self):
        line1 = FONT_MD.render("Game Over", 1, BLACK)
        line2 = FONT_SM.render("Press 'A' to play again.", 1, BLACK)

        x1 = WIDTH / 2 - line1.get_width() / 2;
        y1 = HEIGHT / 3 - line1.get_height() / 2;
        
        x2 = WIDTH / 2 - line2.get_width() / 2;
        y2 = y1 + line1.get_height() + 16;
        
        window.blit(line1, (x1, y1))
        window.blit(line2, (x2, y2))
    
    def display_stats(self):
        score_text = FONT_SM.render("Score: " + str(self.hero.score), 1, BLACK)
        window.blit(score_text, (32, 32))

        lives_text = FONT_SM.render("Lives: " + str(self.hero.lives), 1, BLACK)
        window.blit(lives_text, (32, 64))

        hearts_text = FONT_SM.render("Hearts: " + str(self.hero.hearts), 1, BLACK)
        window.blit(hearts_text, (32, 96))

    def calculate_offset(self):
        world_rect = self.level.world.get_rect()
        hero_rect = self.hero.rect
        
        x = -1 * hero_rect.centerx + WIDTH / 2

        if hero_rect.centerx < WIDTH / 2:
            x = 0
        elif hero_rect.centerx > world_rect.right - WIDTH / 2:
            x = -1 * world_rect.right + WIDTH

        return x, 0
                
    def play(self):  
        # game loop
        done = False

        while not done:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if self.stage == START:
                        self.stage = PLAYING
                        
                    elif self.stage == PLAYING:
                        if event.key == JUMP:
                            self.hero.jump(self.level.blocks)
                            
                    elif self.stage == LEVEL_COMPLETE:
                        pass
                            
                    elif self.stage == GAME_OVER:
                        pass
                        
            pressed = pygame.key.get_pressed()
            
            # Game logic
            if self.stage == PLAYING:
                if pressed[LEFT]:
                    self.hero.move_left()
                elif pressed[RIGHT]:
                    self.hero.move_right()
                else:
                    self.hero.stop()

                self.hero.update(self.level)

            offset_x, offset_y = self.calculate_offset()

            if self.level.completed:
                self.stage = LEVEL_COMPLETE
  
            # Drawing
            self.level.world.fill(SKY_BLUE)
            self.level.all_sprites.draw(self.level.world)

            if self.hero.invincibility % 3 < 2:
                self.level.world.blit(self.hero.image, [self.hero.rect.x, self.hero.rect.y])

            window.blit(self.level.world, [offset_x, offset_y])
            self.display_stats()

            if self.stage == START:
                self.display_start()
            elif self.stage == LEVEL_COMPLETE:
                self.display_level_complete()
            elif self.stage == GAME_OVER:
                self.display_game_over()

            # Update window
            pygame.display.update()
            clock.tick(FPS)

        # Close window on quit
        pygame.quit ()


def main():
    # Make sprites
    ''' our hero '''
    hero = Character(500, 512, hero_img)

    ''' blocks '''
    blocks = pygame.sprite.Group()
     
    for i in range(0, WIDTH * 2, 64):
        b = Block(i, 576, block_img)
        blocks.add(b)

    blocks.add(Block(192, 448, block_img))
    blocks.add(Block(256, 448, block_img))
    blocks.add(Block(320, 448, block_img))

    blocks.add(Block(448, 320, block_img))
    blocks.add(Block(512, 320, block_img))

    blocks.add(Block(1600, 512, block_img))
    blocks.add(Block(1664, 512, block_img))
    blocks.add(Block(1664, 448, block_img))

    ''' coins '''
    coins = pygame.sprite.Group()

    coins.add(Coin(256, 384, coin_img))
    coins.add(Coin(512, 256, coin_img))
    coins.add(Coin(1280, 384, coin_img))

    ''' enemies '''
    enemies = pygame.sprite.Group()

    enemies.add(Monster(832, 512, monster_img))

    ''' powerups '''
    powerups = pygame.sprite.Group()

    powerups.add(OneUp(1088, 512, oneup_img))

    ''' goal '''
    flag = pygame.sprite.Group()
    flag.add(Flag(1792, 448, flag_img))
    flag.add(Flag(1792, 512, flagpole_img))

    # Make a level
    level = Level(blocks, coins, enemies, powerups, flag)

    # Start game
    game = Game(hero, level)
    game.play()


if __name__ == "__main__":
    main()
    
