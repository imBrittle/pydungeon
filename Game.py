# Game
from pdb import Restart
import pygame, sys, time, math, numpy, random
from pygame.locals import *

pygame.init()

pygame.display.set_caption('Dungeon Crawler')

screen_width = 1920
screen_height = 1080
screenRect = pygame.Rect(0, 0, screen_width, screen_height)

screen = pygame.display.set_mode((screen_width, screen_height))

font = pygame.font.Font(None, 20)

fps = 60
target_fps = 240
clock = pygame.time.Clock()

tile_size = 60

def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def BuildWorld(size):
    world = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]]

class Panel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        image = pygame.image.load('img/panel.png').convert()
        self.image = pygame.transform.scale(image, (360, 1080))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y

class World():
    def __init__(self, data):
        self.tile_list = []

        # Load Images
        dirt_bg_img = pygame.image.load('img/dirt_bg.png').convert()
        self.dirt_bg = pygame.transform.scale(dirt_bg_img, (1620, 1080))
        stone_bricks_img = pygame.image.load('img/stone_bricks.png').convert()
        dirt_img = pygame.image.load('img/dirt.png').convert()

        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(stone_bricks_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                col_count += 1
            row_count += 1

    def draw(self):
        screen.blit(self.dirt_bg, (0, 0))
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            # pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, name, maxHealth, damage):
        image = pygame.image.load('img/player.png').convert_alpha()
        self.original_image = pygame.transform.scale(image, (64, 64))
        self.image = pygame.transform.scale(image, (64, 64))
        self.rect = self.image.get_rect()
        self.isAlive = True
        self.update_time = pygame.time.get_ticks()
        self.VelocityX = 0
        self.VelocityY = 0
        self.x = x
        self.y = y
        self.rect.x = self.x
        self.rect.y = self.y
        self.position = self.x + (self.rect.width / 2), self.y + (self.rect.height / 2)
        self.velocityDiminish = 0.5
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.objectCollide = False
        # Stats
        self.name = name
        self.maxHealth = maxHealth
        self.health = maxHealth
        self.damage = damage
        self.scroll = []
        self.start_scroll = self.scroll
        self.speed = 1
        self.maxSpeed = 8
        self.fragments = 0
        self.stars = 0

    def keyPress(self, keys):
        if keys[pygame.K_a]:
            self.VelocityX -= self.speed
            # print("Left")
        if keys[pygame.K_d]:
            self.VelocityX += self.speed
            # print("Right")
        if keys[pygame.K_w]:
            self.VelocityY -= self.speed
            # print("Up")
        if keys[pygame.K_s]:
            self.VelocityY += self.speed
            # print("Down")
        if keys[pygame.K_q]:
            pass
            print("Ability 1")
        if keys[pygame.K_e]:
            pass
            print("Signature")
        if keys[pygame.K_c]:
            pass
            print("Ability 2")
        if keys[pygame.K_x]:
            pass
            print("Ultimate")

    def Update(self):
        if self.health <= 0:
            self.isAlive = False

        # Character Movement
        if self.VelocityX > self.maxSpeed:
            self.VelocityX = self.maxSpeed
        if self.VelocityX < -self.maxSpeed:
            self.VelocityX = -self.maxSpeed
        if self.VelocityY > self.maxSpeed:
            self.VelocityY = self.maxSpeed
        if self.VelocityY < -self.maxSpeed:
            self.VelocityY = -self.maxSpeed

        self.x += self.VelocityX
        self.y += self.VelocityY

        if self.VelocityX > 0:
            self.VelocityX -= self.velocityDiminish
        if self.VelocityX < 0:
            self.VelocityX += self.velocityDiminish
        if self.VelocityY > 0:
            self.VelocityY -= self.velocityDiminish
        if self.VelocityY < 0:
            self.VelocityY += self.velocityDiminish

        # Angle
        mx, my = pygame.mouse.get_pos()
        rel_x, rel_y = mx - self.x, my - self.y
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, int(angle) + 270)
        self.rect = self.image.get_rect(center=self.position)

        # Collision
        for tile in world.tile_list:
            if tile[1].colliderect(self.rect):
                self.VelocityX = 0
                self.VelocityY = 0
                self.objectCollide = True

        self.rect.x = self.x
        self.rect.y = self.y

        screen.blit(self.image, (self.x, self.y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('img/enemy.png').convert_alpha()
        self.original_image = pygame.transform.scale(image, (64, 64))
        self.image = pygame.transform.scale(image, (64, 64))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x
        self.rect.y = self.y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.position = self.x + (self.rect.width / 2), self.y + (self.rect.height / 2)
        self.animationStage = 0
        # Stats
        self.speed = 0
        self.health = 3
        self.damage = 1
        self.shootTimer = 0
    def Update(self, px, py):
        rel_x, rel_y = px - self.x, py - self.y
        self.angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, int(self.angle))
        self.rect = self.image.get_rect(center=self.position)
        self.x += math.cos(-self.angle) * self.speed
        self.y += math.sin(-self.angle) * self.speed
        self.rect.x = self.x
        self.rect.y = self.y
    def Shoot(self, enemyBullets, px, py):
        self.shootTimer += 1
        if self.shootTimer >= 60 and len(enemyBullets) < 1000:  # Bullet Cap
            enemyBullets.append(EnemyProjectile(round(self.x+self.width//2), round(self.y + self.height//2), 6, (255, 100, 100), 90, px + 32, py + 32)) 
            self.shootTimer = 0

class Fragment(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('img/fragment.png').convert_alpha()
        self.image = pygame.transform.scale(image, (64, 64))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x
        self.rect.y - self.y

class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        image = pygame.image.load('img/star.png').convert_alpha()
        self.image = pygame.transform.scale(image, (64, 64))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = self.x
        self.rect.y - self.y

class Projectile(object):
    def __init__(self, x, y, radius, color, direction):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.direction = direction
        self.vel = 16
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)
        mx, my = pygame.mouse.get_pos()
        rel_x, rel_y = mx - self.x, my - self.y
        self.angle = math.atan2(rel_y, rel_x)
    def Draw(self,win):
        pygame.draw.circle(win, self.color, (self.x,self.y), self.radius)
    def Update(self):
        self.x += math.cos(self.angle) * self.vel
        self.y += math.sin(self.angle) * self.vel
        self.rect.x = self.x
        self.rect.y = self.y

class EnemyProjectile(object):
    def __init__(self, x, y, radius, color, direction, px, py):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.direction = direction
        self.vel = 16
        self.rect = pygame.Rect(self.x, self.y, self.radius, self.radius)
        rel_x, rel_y = px - self.x, py - self.y
        self.angle = math.atan2(rel_y, rel_x)
    def Draw(self,win):
        pygame.draw.circle(win, self.color, (self.x,self.y), self.radius)
    def Update(self):
        self.x += math.cos(self.angle) * self.vel
        self.y += math.sin(self.angle) * self.vel
        self.rect.x = self.x
        self.rect.y = self.y
        
world_data = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

world = World(world_data)

def Game():
    fragmentCount = 0
    starCount = 0

    panel = Panel(1560, 0)
    player = Player(300, 300, 'Player', 1000, 1)
    enemy1 = Enemy(random.randint(200, 1400), random.randint(200, 800))
    fragment1 = Fragment(500, 500)
    star1 = Star(700, 700)

    enemies = [enemy1]
    fragments = [fragment1]
    stars = [star1]
    bullets = []
    enemyBullets = []

    keyCooldown = 0
    shootTimer = 0

    debug = False

    run = True
    while run:
        clock.tick(fps)

        # Game Updates
        screen.fill((0, 0, 0))

        world.draw()

        for s in stars:
            if s in stars:
                if s.rect.colliderect(player.rect):
                    player.stars += 1
                    stars.pop(stars.index(s))
                screen.blit(s.image, (s.x, s.y))

        for f in fragments:
            if f in fragments:
                if f.rect.colliderect(player.rect):
                    player.fragments += 1
                    fragments.pop(fragments.index(f))
                screen.blit(f.image, (f.x, f.y))

        for o in enemies:
            if o in enemies:
                o.Update(player.x, player.y)
                o.Shoot(enemyBullets, player.x, player.y)
                screen.blit(o.image, (o.x, o.y))
            else: 
                pass

        keys = pygame.key.get_pressed()
        if player.isAlive == True:
            player.keyPress(keys)
            player.Update()
            player.rect.clamp_ip(screenRect)

        for bullet in bullets:
            bullet.Draw(screen)
        for bullet in enemyBullets:
            bullet.Draw(screen)

        screen.blit(panel.image, (panel.x, panel.y)) # Side Panel: Must be drawn last

        keyCooldown += 1

        # Input
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        if keys[K_i] and keyCooldown > 20:
            keyCooldown = 0
            if debug == False:
                debug = True
            else:
                debug = False
        if keys[pygame.K_SPACE]:
            if shootTimer >= 30 and len(bullets) < 1000:  # Bullet Cap
                bullets.append(Projectile(round(player.x+player.width//2), round(player.y + player.height//2), 6, (255, 255, 255), 90)) 
                shootTimer = 0

        mx, my = pygame.mouse.get_pos()

        if player.x > 1560:
            player.x = -60
            player.rect.x = -60
        if player.x < -60:
            player.x = 1560
            player.rect.x = 1560
        if player.y > 1140:
            player.y = -60
            player.rect.y = -60
        if player.y < -60:
            player.y = 1140
            player.rect.y = 1140

        # Projectiles        
        for bullet in bullets:
            if 0 < bullet.x < 1920 and 0 < bullet.y < 1080:
                for o in enemies:
                    if bullet.rect.colliderect(o.rect):
                        bullets.pop(bullets.index(bullet))
                        o.health -= player.damage
                        if o.health <= 0:
                            enemies.pop(enemies.index(o))
                        else:
                            pass
                bullet.Update()
            else:
                bullets.pop(bullets.index(bullet))
        shootTimer += 1
        for bullet in enemyBullets:
            if 0 < bullet.x < 1920 and 0 < bullet.y < 1080:
                for o in enemies:
                    if bullet.rect.colliderect(player.rect):
                        enemyBullets.pop(enemyBullets.index(bullet))
                        player.health -= o.damage
                        if o.health <= 0:
                            player.pop(player.index(o))
                        else:
                            pass
                bullet.Update()
            else:
                enemyBullets.pop(enemyBullets.index(bullet))

        # Identifiers
        if debug == True:
            draw_text(f'Player: {player.x, player.y}', font, (255, 200, 255), screen, player.x, player.y - 20)
            draw_text(f'Star: {star1.x, star1.y}', font, (255, 255, 0), screen, star1.x, star1.y - 20)
            for o in enemies:
                draw_text(f'Enemy: {o.x, o.y}', font, (255, 0, 0), screen, o.x, o.y - 20)
            draw_text(f'Fragment: {fragment1.x, fragment1.y}', font, (0, 255, 255), screen, fragment1.x, fragment1.y - 20)
            for bullet in bullets:
                draw_text(f'Bullet: {round(bullet.x, 2), round(bullet.y, 2)}', font, (255, 255, 255), screen, bullet.x, bullet.y - 20)
            for bullet in enemyBullets:
                draw_text(f'Enemy Bullet: {round(bullet.x, 2), round(bullet.y, 2)}', font, (255, 100, 100), screen, bullet.x, bullet.y - 20)
            draw_text(f'FPS: {round(clock.get_fps(), 2)}', font, (255, 255, 255), screen, 10, 10)
            draw_text(f'MouseCoords = {mx}, {my}', font, (255, 255, 255), screen, 1500, 10)
            draw_text(f'Fragments = {player.fragments}', font, (255, 255, 255), screen, 1500, 30)
            draw_text(f'Stars = {player.stars}', font, (255, 255, 255), screen, 1500, 50)
            draw_text(f'playerCoords = {player.x}, {player.y}', font, (255, 255, 255), screen, 1500, 70)
            draw_text(f'playerRect = {player.rect.x}, {player.rect.y}', font, (255, 255, 255), screen, 1500, 90)
            draw_text(f'playerCollide = {player.objectCollide}', font, (255, 255, 255), screen, 1500, 110)
        
        pygame.display.update()
Game()