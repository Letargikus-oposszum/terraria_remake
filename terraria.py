import pygame
import random
import time
from opensimplex import OpenSimplex
import cProfile

    # Initialize Pygame
def main():
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
    DARK_GRAY = (16,16,16)
    GREEN = (0, 255, 0)
    DARK_GREEN = (1, 50, 32)
    MAHOGANY = (192, 64, 0)
    BROWN = (139, 69, 19)
    LIGHT_BROWN = (196, 164, 132)
    GRAY = (128, 128, 128)
    SLATE_GRAY = (47,79,79)
    BLUE = (0, 0, 255)
    BRICK_RED = (170, 74, 68)

    # Generate a seed from system time
    seed = int(time.time())
    noise = OpenSimplex(seed)

    # Terrain and object generation
    terrain = {}
    trees = {}
    chests = {}
    spawners = {}
    chestitems = []
    enemies=[]

    # Screen setup
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
    pygame.display.set_caption("Terraria-like Game")
    bg = pygame.image.load("images\\bg.jpg")
    
    starterswordimgraw = pygame.image.load("images\\StarterSword.png")
    endgamestaffimgraw = pygame.image.load("images\\EndgameStaff.png")
    lifestealswordimgraw = pygame.image.load("images\\LifeStealSword.png")
    starterswordimg = pygame.transform.scale(starterswordimgraw, (80,80))
    endgamestaffimg = pygame.transform.scale(endgamestaffimgraw, (80,80))
    lifestealswordimg = pygame.transform.scale(lifestealswordimgraw, (80,80))

    itemImgList = [starterswordimg,endgamestaffimg,lifestealswordimg]
    chest_opener = False
    moving = True
    playerinvopener = False
    selecteditemdmg = 0
    selecteditemspeed = 0
    selecteditemrange = 0
    last_attack_time_player = 0  # Initialize at the start
    ATTACK_COOLDOWN = 1000
    swinging = False
    swing_start_time = 0
    GRID_SIZE = 100
    spatial_grid = {}
    swing_duration = 200 
    
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

    class Spawner:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.width = 20
            self.height = 20
        
        def draw(self, surface, offset_x):
            pygame.draw.rect(surface, DARK_GRAY, (self.x - offset_x, self.y - self.height, self.width, self.height))


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
            self.selecteditemimg = None
            self.selecteditemdmg = selecteditemdmg
            self.selecteditemspeed = selecteditemspeed
            self.selecteditemrange = selecteditemrange         
            self.slot_count = slot_count
            self.slotindexcounter = 0
            self.slots = []

            slot_width = slot_height = 40
            padding = 5
            for i in range(slot_count):
                slot_x = x + padding + (slot_width + padding) * (i % 8)
                slot_y = y + padding + (slot_height + padding) * (i // 8)
                self.slots.append(Slot(slot_x, slot_y, slot_width, slot_height, GRAY))

            self.visible = False  # Initialize as not visible

        def show(self):
            self.visible = True

        def hide(self):
            self.visible = False

        def drawHotBar(self, h):

            slotcounter = 0
            if not self.visible:
                pygame.draw.rect(screen, WHITE, (self.x, self.y, self.w, h))
                for slot in self.slots:
                    slot.draw(GRAY, screen)
                    slotcounter += 1
                    if slotcounter == 8:
                        break
                        
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEWHEEL:
                        if event.y < 0 and self.slotindexcounter < 7:  # felfelé görgetés
                            self.slotindexcounter += 1
                        elif event.y > 0 and self.slotindexcounter > 0:  # lefelé görgetés
                            self.slotindexcounter -= 1
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            pass
                # Draw the selected slot highlight
                selected_slot = self.slots[self.slotindexcounter]
                highlight_rect = pygame.Rect(selected_slot.x, selected_slot.y, selected_slot.w, selected_slot.h)
                pygame.draw.rect(screen, SLATE_GRAY, highlight_rect, 3)  # Red color with 3 pixels thickness

                try:
                    if selected_slot.item is not None:
                        self.selecteditemimg = selected_slot.item.img
                        self.selecteditemdmg = selected_slot.item.dmg
                        self.selecteditemspeed = selected_slot.item.speed
                        self.selecteditemrange = selected_slot.item.range
                    elif selected_slot.item is None:
                        self.selecteditemimg = None
                        self.selecteditemdmg = 1
                        self.selecteditemspeed = 1
                        self.selecteditemrange = 1
                except Exception as e:
                    pass


        def draw(self, screen, dirty_rects):
            if self.visible:
                pygame.draw.rect(screen, WHITE, (self.x, self.y, self.w, self.h))
                dirty_rects.append(pygame.Rect(self.x, self.y, self.w, self.h))
                for slot in self.slots:
                    if slot.y < SCREEN_HEIGHT:  # Csak akkor rajzoljuk ki, ha a slot látható
                        slot.draw(GRAY,screen)
                        dirty_rects.append(pygame.Rect(slot.x, slot.y, slot.w, slot.h))

        def add_item(self, item, slot_index):
            if 0 <= slot_index < len(self.slots):
                self.slots[slot_index].add_item(item)
        
        def remove_item(self, slot_index):
            if 0 <= slot_index < len(self.slots):
                self.slots[slot_index].remove_item()

    class Slot:
        def __init__(self, x, y, w, h, color):
            self.x = x
            self.y = y
            self.w = w
            self.h = h
            self.color = color
            self.item = None  # Initialize as empty

        def draw(self, color, screen):
            pygame.draw.rect(screen, color, (self.x, self.y, self.w, self.h))
            if self.item:
                item_img = self.item.img
                item_img = pygame.transform.scale(item_img, (self.w, self.h))
                screen.blit(item_img, (self.x, self.y))

        def is_point_inside(self,point_x,point_y):
            return self.x <= point_x <= self.x + self.w and self.y <= point_y <= self.y+self.h
        
        def collidepoint(self, pos):
            return self.is_point_inside(pos[0], pos[1])

        def has_item(self):
            return self.item is not None

        def add_item(self, item):
            self.item = item

        def remove_item(self):
            self.item = None

    #entities
    class Entity:
        def __init__(self, x, y, hp, dmg, w, h, color, attackrange, attackspeed, movingspeed):
            self.x = x
            self.y = y
            self.hp = hp
            self.dmg = dmg
            self.w = w
            self.h = h
            self.color = color
            self.attackrange = attackrange
            self.attackspeed = attackspeed
            self.movingspeed = movingspeed
            self.vy = 0
            self.on_ground = False

        def hitbox(self):
            return pygame.Rect(self.x-terrain_offset, self.y, self.w, self.h)

        def update(self, player_x):
            pass

        def draw(self, screen, enemy_offset_x):
            pass

    class Enemy(Entity):
        def __init__(self, x, y, hp, dmg, w, h, color, attackrange, attackspeed, movingspeed):
            super().__init__(x, y, hp, dmg, w, h, color, attackrange, attackspeed, movingspeed)
            self.vy = 0
            self.last_attack_time = 0

        def attack(self, player_x, player_y):
            current_time = pygame.time.get_ticks()
            if abs(self.x - player_x) < self.attackrange and abs(self.y - player_y) < self.attackrange:
                if current_time - self.last_attack_time >= self.attackspeed * 1000:
                    self.last_attack_time = current_time
                    health_bar.hp -= 7
                    if health_bar.hp == 0:
                        exit(0)

        def update(self, player_x):
            if self.x < player_x - TILE_SIZE:
                self.x += self.movingspeed
            elif self.x > player_x + TILE_SIZE:
                self.x -= self.movingspeed
            if self.x == (player_x - TILE_SIZE) or self.x == (player_x + TILE_SIZE):
                self.attack(player_x, player_y)

            self.vy += GRAVITY
            self.y += self.vy

            on_ground = False
            for y in range(SCREEN_HEIGHT // TILE_SIZE):
                for x in range(SCREEN_WIDTH // TILE_SIZE):
                    tile_x = x + terrain_offset // TILE_SIZE
                    chunk_x = tile_x // CHUNK_SIZE
                    tile_index_x = tile_x % CHUNK_SIZE
                    if chunk_x in terrain and terrain[chunk_x][tile_index_x][y] != 0:
                        tile_rect = pygame.Rect(tile_x * TILE_SIZE - terrain_offset % TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        enemy_rect = pygame.Rect(self.x, self.y, self.w, self.h)
                        if enemy_rect.colliderect(tile_rect):
                            if self.vy > 0:
                                self.y = tile_rect.top - self.h
                                self.vy = 0
                                on_ground = True
            if not on_ground:
                self.on_ground = False
            else:
                self.on_ground = True

        def draw(self, screen):
            pygame.draw.rect(screen, self.color, (self.x - terrain_offset, self.y, self.w, self.h))

       
    def spawn_enemy():
        x = random.randint(spawner_x-10*TILE_SIZE,spawner_x+10*TILE_SIZE)
       
        y = 0  # Start at the top of the screen
        hp = 100
        dmg = 10
        w = TILE_SIZE
        h = TILE_SIZE * 2
        color = BRICK_RED
        attackrange = 50
        attackspeed = 1
        movingspeed = 2
        new_enemy = Enemy(x, y, hp, dmg, w, h, color, attackrange, attackspeed, movingspeed)
        enemies.append(new_enemy)

    #world generation
    def generate_chunk(chunk_x):
        global current_height
        chunk = [[0 for _ in range(SCREEN_HEIGHT // TILE_SIZE)] for _ in range(CHUNK_SIZE)]
        tree_list = []
        chest_list = []
        spawner_list = []
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
            if random.random() < 0.008:
                global chest_x,chest_y
                chest_x = world_x * TILE_SIZE
                chest_y = ground_height * TILE_SIZE
                chest_list.append(Chest(chest_x, chest_y))
            if random.random() < 0.006:
                global spawner_x,spawner_y
                spawner_y = ground_height * TILE_SIZE
                spawner_x =  world_x * TILE_SIZE
                spawner_list.append(Spawner(spawner_x, spawner_y))
        
        terrain[chunk_x] = chunk
        trees[chunk_x] = tree_list
        chests[chunk_x] = chest_list
        spawners[chunk_x] = spawner_list

    def get_chunk(chunk_x):
        if chunk_x not in terrain:
            generate_chunk(chunk_x)
        return terrain[chunk_x]

    #def for spawning enemies


    terrain_offset = 0
    
    # Player setup
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2
    player_vy = 0
    on_ground = False

    # Initialize inventory
    invx = 630
    invy = 5
    invw = 365
    invh = 185
    slot_count = 32
    chestinventory = Inventory(invx, invy+300, invw, invh, slot_count)

    playerinventory = Inventory(invx, invy, invw, invh, slot_count)

    # Game loop
    running = True
    clock = pygame.time.Clock()
    
    active_slot = None
    dragged_item = None




    while running:
        dirty_rects = []

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
        for chunk_x in range(first_visible_chunk - 1, last_visible_chunk + 2):
            if chunk_x in spawners:
                for spawner in spawners[chunk_x]:
                    spawner.draw(screen, terrain_offset)

        pygame.draw.rect(screen, BLUE, (player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT))
        health_bar.draw(screen)
        
        if keys[pygame.K_i]:
            spawn_enemy()

        current_time = pygame.time.get_ticks()

        if keys[pygame.K_i]:
            spawn_enemy()

        if keys[pygame.K_w] and current_time - last_attack_time_player >= ATTACK_COOLDOWN // playerinventory.selecteditemspeed:
            try: 
                    
                weapon_img = playerinventory.selecteditemimg

                mousex = pygame.mouse.get_pos()[0]
                if mousex > SCREEN_WIDTH // 2:
                    try:

                        swinging = True
                        swing_start_time = current_time

                        rotation_angle = -55  # Adjust this angle to change the swinging animation
                        rotated_weapon_img = pygame.transform.rotate(weapon_img, rotation_angle)

                        attack_rect = pygame.Rect(player_x, player_y - playerinventory.selecteditemrange * TILE_SIZE, (playerinventory.selecteditemrange * TILE_SIZE) * 2, PLAYER_HEIGHT + (playerinventory.selecteditemrange * TILE_SIZE) * 2)
                    except Exception:
                        pass
                elif mousex < SCREEN_WIDTH // 2:
                    try:
                        swinging = True
                        swing_start_time = current_time

                        rotation_angle = -125  # Adjust this angle to change the swinging animation
                        mirrored_img = pygame.transform.flip(weapon_img, False, True)
                        rotated_weapon_img = pygame.transform.rotate(mirrored_img, rotation_angle)

                        attack_rect = pygame.Rect((player_x - (playerinventory.selecteditemrange * TILE_SIZE) * 2) + TILE_SIZE, player_y - playerinventory.selecteditemrange * TILE_SIZE, (playerinventory.selecteditemrange * TILE_SIZE) * 2, PLAYER_HEIGHT + (playerinventory.selecteditemrange * TILE_SIZE) * 2)
                    except Exception:
                        pass
                enemies_to_remove = []
                for enemy in enemies:
                    if attack_rect.colliderect(enemy.hitbox()):
                        enemy.hp -= playerinventory.selecteditemdmg
                        if (not health_bar.hp >= health_bar.max_hp) and enemy.hp <= 0 and playerinventory.selecteditemdmg == 22:
                            health_bar.hp += 3
                        if enemy.hp <= 0:
                            enemies_to_remove.append(enemy)

                for enemy in enemies_to_remove:
                    enemies.remove(enemy)

                last_attack_time_player = current_time  # Reset the attack timer
            except Exception:
                pass
        # Handle the swinging animation

        if swinging:
            try:
                if current_time - swing_start_time <= swing_duration:
                    if mousex > SCREEN_WIDTH // 2:
                        screen.blit(rotated_weapon_img, (SCREEN_WIDTH // 2, player_y - PLAYER_HEIGHT))
                    elif mousex < SCREEN_WIDTH // 2:
                        screen.blit(rotated_weapon_img, ((SCREEN_WIDTH // 2)-TILE_SIZE*4.5, player_y - PLAYER_HEIGHT))
                else:
                    swinging = False  # End the swinging animation
            except Exception:
                pass

        for enemy in enemies:
            enemy.draw(screen)
            enemy.update(terrain_offset+SCREEN_WIDTH//2)



        if chest_opener:
            if not chest_filled:
                for i in range(slot_count):
                    if random.random() < 0.2:
                        sword = WeaponItem(10, 3, 2, starterswordimg)
                    elif random.random() < 0.001:
                        sword = WeaponItem(50, 8, 2, endgamestaffimg)
                    elif random.random() < 0.1:
                        sword = WeaponItem(22, 3, 3, lifestealswordimg)
                    else:
                        sword = None
                    chestinventory.add_item(sword, i)
                    chestitems.append(sword)
                chest_filled = True
            if keys[pygame.K_LSHIFT]:
                        mx,my = pygame.mouse.get_pos()

                        for slot in chestinventory.slots:#p-c
                            if slot.is_point_inside(mx,my) and slot.has_item() and not playerinventory.slots[chestinventory.slots.index(slot)].has_item():
                                playerinventory.add_item(slot.item,chestinventory.slots.index(slot))
                                chestinventory.remove_item(chestinventory.slots.index(slot))



                        for slot in playerinventory.slots:#c-p
                            if slot.is_point_inside(mx,my) and slot.has_item() and not chestinventory.slots[playerinventory.slots.index(slot)].has_item():
                                chestinventory.add_item(slot.item,playerinventory.slots.index(slot))
                                playerinventory.remove_item(playerinventory.slots.index(slot))

                                

            chestinventory.show()
            chestinventory.draw(screen,dirty_rects)
            playerinventory.show()
            playerinventory.draw(screen,dirty_rects)
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
            playerinventory.draw(screen,dirty_rects)
            moving = False
        if playerinvopener == False:
            playerinventory.hide()
            moving = True
        
        if playerinvopener == True and chest_opener == False:
            if keys[pygame.K_t]:
                        mx,my = pygame.mouse.get_pos()
                        for slot in playerinventory.slots:
                            if slot.is_point_inside(mx,my) and slot.has_item():
                                playerinventory.remove_item(playerinventory.slots.index(slot))
            #------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------
            #itemDragging-------------------------------------------------------------------------------------------------------------------------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        for num, slot in enumerate(playerinventory.slots):
                            if slot.collidepoint(event.pos):
                                active_slot = num
                                dragged_item = slot.item
                                slot.remove_item()

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        for slot in playerinventory.slots:
                            if slot.collidepoint(event.pos) and not slot.has_item():
                                slot.add_item(dragged_item)
                                dragged_item = None
                                active_slot = None
                                break
                        else:
                            # If not dropped on any slot, return the item to its original slot
                            if active_slot is not None:
                                playerinventory.slots[active_slot].add_item(dragged_item)
                                dragged_item = None
                                active_slot = None

                if dragged_item:
                    try:
                        mx, my = pygame.mouse.get_pos()
                        if dragged_item in itemImgList:
                            item_img = itemImgList[dragged_item]
                        # Itt további feltételekkel folytathatod a többi kép ellenőrzését

                        item_img = pygame.transform.scale(item_img, (40, 40))
                        screen.blit(item_img, (mx - 20, my - 20))
                    except Exception as e:
                        pass
        #------------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------
        #------------------------------------------------------------------------------------------------------------------------------------------
        #--------------------------------------------------------------------------------------------------------------------------------------
        

        
        if playerinvopener == False and chest_opener == False:
            playerinventory.drawHotBar(50)
            #print(playerinventory.selecteditemdmg)



        pygame.display.flip()
        clock.tick(90)

    pygame.quit()
if __name__ == "__main__":
    cProfile.run('main()')