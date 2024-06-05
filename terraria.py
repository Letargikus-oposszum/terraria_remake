import pygame
import random
import time
from opensimplex import OpenSimplex

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 20
CHUNK_SIZE = 20
PLAYER_WIDTH = TILE_SIZE
PLAYER_HEIGHT = TILE_SIZE * 2
GRAVITY = 0.3
JUMP_STRENGTH = 8

# Colors
WHITE = (255, 255, 255)
GRAY_RGBA = (128, 128, 128, 128)
GREEN = (0, 255, 0)
DARK_GREEN = (1, 50, 32)
MAHOGANY = (192, 64, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (196, 164, 132)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)

# Generate a seed from system time
seed = int(time.time())
noise = OpenSimplex(seed)

# Terrain and object generation
terrain = {}
trees = {}
chests = {}

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Terraria-like Game")
bg = pygame.image.load("images\\bg.jpg")
chest_opener = False
moving = True
playerinvopener = False

# HealthBar class
class HealthBar:
    def __init__(self, x, y, w, h, max_hp):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.hp = max_hp
        self.max_hp = max_hp
    
    def draw(self, surface):
        ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, "red", (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, "green", (self.x, self.y, self.w * ratio, self.h))

health_bar = HealthBar(5, 5, 200, 20, 100)

#objects
class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 80
    
    def draw(self, surface, offset_x):
        pygame.draw.rect(surface, MAHOGANY, (self.x - offset_x, self.y - self.height, self.width, self.height))
        pygame.draw.rect(surface, DARK_GREEN, (self.x - offset_x - TILE_SIZE, self.y - TILE_SIZE * 2.5 - self.height, self.width + TILE_SIZE * 2, self.height + TILE_SIZE / 2))

class Chest:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
    
    def draw(self, surface, offset_x):
        pygame.draw.rect(surface, LIGHT_BROWN, (self.x - offset_x, self.y - self.height, self.width, self.height))

#items
class WeaponItem:
    def __init__(self,dmg,speed,attackRange,img):
        self.dmg = dmg
        self.speed = speed
        self.range = attackRange
        self.img = img

#inventory
class Inventory:
    def __init__(self, x, y, w, h, slot_count):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.slot_count = slot_count
        self.slots = []

        slot_width = slot_height = 40
        padding = 5
        for i in range(slot_count):
            slot_x = x + padding + (slot_width + padding) * (i % 8)
            slot_y = y + padding + (slot_height + padding) * (i // 8)
            self.slots.append(Slot(slot_x, slot_y, slot_width, slot_height))

        self.visible = False  # Initialize as not visible

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def draw(self, screen):
        if self.visible:
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.w, self.h))
            for slot in self.slots:
                slot.draw(screen)
    
    def add_item(self, item, slot_index):
        if 0 <= slot_index < len(self.slots):
            self.slots[slot_index].add_item(item)
    
    def remove_item(self, slot_index):
        if 0 <= slot_index < len(self.slots):
            self.slots[slot_index].remove_item()

class Slot:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.item = None  # Initialize as empty

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.w, self.h))
        if self.item:
            # Draw item image
            item_img = pygame.image.load(self.item.img)
            item_img = pygame.transform.scale(item_img, (self.w, self.h))
            screen.blit(item_img, (self.x, self.y))

    def is_point_inside(self,point_x,point_y):
        return self.x <= point_x <= self.x + self.w and self.y <= point_y <= self.y+self.h

    def has_item(self):
        return self.item is not None

    def add_item(self, item):
        self.item = item

    def remove_item(self):
        self.item = None

#list
#weaponlist = [WeaponItem(10,2,3,"images\\StarterSword.png"),WeaponItem(50,8,20,"images\\EndgameStaff.png"),WeaponItem(20,3,2,"images\\LifeStealSword.png")]


def generate_chunk(chunk_x):
    chunk = [[0 for _ in range(SCREEN_HEIGHT // TILE_SIZE)] for _ in range(CHUNK_SIZE)]
    tree_list = []
    chest_list = []
    for x in range(CHUNK_SIZE):
        world_x = chunk_x * CHUNK_SIZE + x
        noise_value = noise.noise2(world_x * 0.04, 0.04) # Changed noise2d to noise2
        ground_height = int((noise_value+1) / 2*(SCREEN_HEIGHT // TILE_SIZE - 1))
        for y in range(ground_height, SCREEN_HEIGHT // TILE_SIZE):
            if y < ground_height + 1:
                chunk[x][y] = 1  # Grass
            elif y < ground_height + 4:
                chunk[x][y] = 2  # Dirt
            else:
                chunk[x][y] = 3  # Stone

        # Place a tree with a 10% chance
        if random.random() < 0.05:
            tree_x = world_x * TILE_SIZE
            tree_y = ground_height * TILE_SIZE
            tree_list.append(Tree(tree_x, tree_y))
        if random.random() < 0.005:
            global chest_x,chest_y
            chest_x = world_x * TILE_SIZE
            chest_y = ground_height * TILE_SIZE
            chest_list.append(Chest(chest_x, chest_y))
    
    terrain[chunk_x] = chunk
    trees[chunk_x] = tree_list
    chests[chunk_x] = chest_list

def get_chunk(chunk_x):
    if chunk_x not in terrain:
        generate_chunk(chunk_x)
    return terrain[chunk_x]

terrain_offset = 0

# Player setup
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_vy = 0
on_ground = False

# Initialize inventory
invx = 300
invy = 350
invw = 365
invh = 185
slot_count = 32
chestinventory = Inventory(invx, invy, invw, invh, slot_count)  # Example instance creation

playerinventory = Inventory(invx, invy-300, invw, invh, slot_count)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_a] and moving:
        terrain_offset -= 4

    if keys[pygame.K_RIGHT] or keys[pygame.K_d] and moving:
        terrain_offset += 4
    
    if keys[pygame.K_LEFT] or keys[pygame.K_a] and keys[pygame.K_LSHIFT] and moving:
        terrain_offset -= 5
    
    if keys[pygame.K_RIGHT] or keys[pygame.K_d] and keys[pygame.K_LSHIFT] and moving:
        terrain_offset += 5

    if keys[pygame.K_SPACE] and on_ground:
        player_vy = -JUMP_STRENGTH
        on_ground = False

    player_vy += GRAVITY
    player_y += player_vy

    first_visible_chunk = terrain_offset // (CHUNK_SIZE * TILE_SIZE)
    last_visible_chunk = (terrain_offset + SCREEN_WIDTH) // (CHUNK_SIZE * TILE_SIZE)
    for chunk_x in range(first_visible_chunk - 1, last_visible_chunk + 2):
        get_chunk(chunk_x)

    on_ground = False
    if player_y + PLAYER_HEIGHT > SCREEN_HEIGHT:
        player_y = SCREEN_HEIGHT - PLAYER_HEIGHT
        player_vy = 0
        on_ground = True
    else:
        for y in range(SCREEN_HEIGHT // TILE_SIZE):
            for x in range(SCREEN_WIDTH // TILE_SIZE):
                tile_x = x + terrain_offset // TILE_SIZE
                chunk_x = tile_x // CHUNK_SIZE
                tile_index_x = tile_x % CHUNK_SIZE
                if chunk_x in terrain and terrain[chunk_x][tile_index_x][y] != 0:
                    tile_rect = pygame.Rect(tile_x * TILE_SIZE - terrain_offset, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
                    if player_rect.colliderect(tile_rect):
                        if player_vy > 0:
                            player_y = tile_rect.top - PLAYER_HEIGHT
                            player_vy = 0
                            on_ground = True

    if player_y < 0:
        player_y = 0
    if player_y + PLAYER_HEIGHT > SCREEN_HEIGHT:
        player_y = SCREEN_HEIGHT - PLAYER_HEIGHT

    screen.blit(bg, (0, 0))
    
    for y in range(SCREEN_HEIGHT // TILE_SIZE):
        for x in range(SCREEN_WIDTH // TILE_SIZE):
            tile_x = x + terrain_offset // TILE_SIZE
            chunk_x = tile_x // CHUNK_SIZE
            tile_index_x = tile_x % CHUNK_SIZE
            if chunk_x in terrain:
                if terrain[chunk_x][tile_index_x][y] == 1:
                    pygame.draw.rect(screen, GREEN, (x * TILE_SIZE - terrain_offset % TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif terrain[chunk_x][tile_index_x][y] == 2:
                    pygame.draw.rect(screen, BROWN, (x * TILE_SIZE - terrain_offset % TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                elif terrain[chunk_x][tile_index_x][y] == 3:
                    pygame.draw.rect(screen, GRAY, (x * TILE_SIZE - terrain_offset % TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for chunk_x in range(first_visible_chunk - 1, last_visible_chunk + 2):
        if chunk_x in trees:
            for tree in trees[chunk_x]:
                tree.draw(screen, terrain_offset)
    for chunk_x in range(first_visible_chunk - 1, last_visible_chunk + 2):
        if chunk_x in chests:         
            global chest
            for chest in chests[chunk_x]:
                chest.draw(screen, terrain_offset)
                chest_screen_x = chest.x - terrain_offset
                if pygame.mouse.get_pressed()[0] and (pygame.mouse.get_pos()[1] <= chest.y + 1 and pygame.mouse.get_pos()[1] >= chest.y - 17) and (pygame.mouse.get_pos()[0] <= chest_screen_x + 20 and pygame.mouse.get_pos()[0] >= chest_screen_x + 2):
                    chest_opener = True
                    chest_filled = False

    pygame.draw.rect(screen, BLUE, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
    health_bar.draw(screen)

    if chest_opener:
        if not chest_filled:
            for i in range(slot_count):
                if random.random() < 0.2:
                    sword = WeaponItem(10, 2, 3, "images\\StarterSword.png")
                elif random.random() < 0.001:
                    sword = WeaponItem(50, 8, 20, "images\\EndgameStaff.png")
                elif random.random() < 0.1:
                    sword = WeaponItem(20, 3, 2, "images\\LifeStealSword.png")
                else:
                    sword = None
                chestinventory.add_item(sword, i)
            chest_filled = True
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx,my = pygame.mouse.get_pos()
                    for slot in chestinventory.slots:
                        if slot.is_point_inside(mx,my) and slot.has_item():
                            playerinventory.add_item(slot.item,chestinventory.slots.index(slot))
                            chestinventory.remove_item(chestinventory.slots.index(slot))
                    for slot in playerinventory.slots:
                        if slot.is_point_inside(mx,my) and slot.has_item():
                            chestinventory.add_item(slot.item,playerinventory.slots.index(slot))
                            playerinventory.remove_item(playerinventory.slots.index(slot))

        chestinventory.show()
        chestinventory.draw(screen)
        playerinventory.show()
        playerinventory.draw(screen)
        moving = False

        if keys[pygame.K_ESCAPE]:
            chest_opener = False
            moving = True
            playerinventory.hide()
            chestinventory.hide()
            chest_filled = False

    if keys[pygame.K_e]:
        playerinvopener = True
    if keys[pygame.K_ESCAPE]:
        playerinvopener = False
        
    if playerinvopener == True:
        playerinventory.show()
        playerinventory.draw(screen)
    if playerinvopener == False:
        playerinventory.hide()
    
    if playerinvopener == True and chest_opener == False:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    mx,my = pygame.mouse.get_pos()
                    for slot in playerinventory.slots:
                        if slot.is_point_inside(mx,my) and slot.has_item():
                            playerinventory.remove_item(playerinventory.slots.index(slot))
    

    if health_bar.hp == 0:
        exit(0)

    pygame.display.flip()
    clock.tick(90)

pygame.quit()
