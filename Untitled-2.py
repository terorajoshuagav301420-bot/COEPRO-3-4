
import pygame
import random  
import math  

pygame.init()

# Library of the game's constants
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
dark_green = (0, 100, 0)
red = (200, 0, 0)          
orange = (255, 140, 0)     
gold = (255, 215, 0)
light_green = (0, 255, 100)
blue = (50, 150, 255)
dark_blue = (30, 100, 200)

width = 600
height = 800

# --- GLOBAL DIMENSIONS ---
PLATFORM_W = 150
PLATFORM_H = 190
BOOSTER_W = 40
BOOSTER_H = 30

# Game variables
X = 200
Y = 400  
score = 0  

# Platforms 
platforms = [
    [200, 600, PLATFORM_W, PLATFORM_H, "intact", 50], 
    [50, 400, PLATFORM_W, PLATFORM_H, "intact", -1], 
    [350, 200, PLATFORM_W, PLATFORM_H, "intact", -1],
    [150, 0, PLATFORM_W, PLATFORM_H, "intact", -1], 
    [380, -200, PLATFORM_W, PLATFORM_H, "intact", -1], 
    [200, -400, PLATFORM_W, PLATFORM_H, "intact", -1]
]
y_change = 0
x_change = 0
player_speed = 5
jump = False

# Flags for dynamic progression events
projectiles_cleared_at_100 = False

# --- PHYSICS VARIABLES FOR REALISTIC LANDING ---
is_crouching = False
crouch_timer = 0
CROUCH_DURATION = 6  

# --- BOOSTER STATE VARIABLES ---
is_boosting = False
booster_timer = 0
BOOSTER_DURATION = 120  
booster_speed = 14      

# --- GAME STATE ---
game_state = "MENU"  # Can be "MENU", "GAME", "SETTINGS", "LOAD_GAME"

print("Welcome to the game of Doodle jump! \n")

# --- IMAGE LOADING SECTION ---
try:
    img_original = pygame.image.load(r"C:\Users\PC\Downloads\DOODLE JUMP FROG(latest).png")
except pygame.error:
    img_original = pygame.Surface((150, 150), pygame.SRCALPHA)
    pygame.draw.circle(img_original, (34, 139, 34), (75, 75), 60) 

img_normal = pygame.transform.scale(img_original, (150, 150))
img_squished = pygame.transform.scale(img_original, (150, 125)) 

img_boosting_visual = img_normal.copy()
img_boosting_visual.fill((255, 100, 0, 150), special_flags=pygame.BLEND_RGBA_MULT)

try:
    platform_img = pygame.image.load(r"C:\Users\PC\Downloads\lates log drawing.png")
except pygame.error:
    platform_img = pygame.Surface((PLATFORM_W, PLATFORM_H))
    platform_img.fill(dark_green)
platform_img = pygame.transform.scale(platform_img, (PLATFORM_W, PLATFORM_H))

try:
    broken_platform_img = pygame.image.load(r"C:\Users\PC\Downloads\broken_log-removebg-preview.png")
except pygame.error:
    broken_platform_img = pygame.Surface((PLATFORM_W, PLATFORM_H), pygame.SRCALPHA)
    pygame.draw.rect(broken_platform_img, gray, (0, 0, PLATFORM_W, PLATFORM_H // 3))
broken_platform_img = pygame.transform.scale(broken_platform_img, (PLATFORM_W, PLATFORM_H))

# 1. Gameplay Background Image
try:
    bg_img = pygame.image.load(r"C:\Users\PC\Downloads\background.png")
except pygame.error:
    bg_img = pygame.Surface((width, height))
    bg_img.fill((100, 149, 237))  
bg_img = pygame.transform.scale(bg_img, (width, height))

# 2. Front Page Menu Background Image
try:
    menu_bg_img = pygame.image.load(r"C:\Users\PC\Downloads\title page_bg.png") 
except pygame.error:
    menu_bg_img = pygame.Surface((width, height))
    menu_bg_img.fill((24, 38, 28))  # Fallback to a dark muddy swamp green
menu_bg_img = pygame.transform.scale(menu_bg_img, (width, height))

# 3. New Custom Image Title Logo
try:
    title_img = pygame.image.load(r"C:\Users\PC\Downloads\front_page-removebg-preview.png") 
    title_img = pygame.transform.scale(title_img, (450, 250)) # Perfectly sized for menu header
except pygame.error:
    title_img = None 


fps = 70
font = pygame.font.SysFont("Arial", 30)
title_font = pygame.font.SysFont("Arial", 45, bold=True)
button_font = pygame.font.SysFont("Arial", 25, bold=True)
timer = pygame.time.Clock()

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Swampy Jumper")


class Enemy:
    def __init__(self):
        self.width = 80
        self.height = 40
        self.x = random.randint(0, width - self.width)
        self.y = 40  
        self.speed = 4
        self.direction = 1  
        self.throw_cooldown = 100 
        
    def update(self, projectiles_list):
        self.x += self.speed * self.direction
        if self.x <= 0 or self.x >= width - self.width:
            self.direction *= -1
            
        if self.throw_cooldown > 0:
            self.throw_cooldown -= 1 
        else:
            src_x = self.x + self.width // 2
            src_y = self.y + self.height // 2
            angle = math.radians(random.randint(45, 135))
            projectiles_list.append(Projectile(src_x, src_y, angle))
            self.throw_cooldown = random.randint(240, 360)  

    def draw(self, surface):
        pygame.draw.rect(surface, red, (self.x, self.y, self.width, self.height), border_radius=5)

class Projectile:
    def __init__(self, x, y, angle):
        self.size = 20
        self.x = x - self.size // 2
        self.y = y
        self.base_speed = 6.5  
        self.vx = self.base_speed * math.cos(angle)
        self.vy = self.base_speed * math.sin(angle)

    def update(self, scroll_speed, world_change):
        self.x += self.vx
        self.y += self.vy
        self.y += scroll_speed
        if Y <= 400 and world_change < 0:
            self.y -= world_change

    def draw(self, surface):
        pygame.draw.rect(surface, orange, (self.x, self.y, self.size, self.size))


def check_collision(rect_list, jump):
    global X, Y, y_change, is_crouching, crouch_timer, is_boosting, booster_timer
    
    if is_boosting or is_crouching:
        return jump

    fall_margin = max(10, y_change + 2)
    player_feet_y = Y + 100
    player_feet = pygame.Rect(X + 45, player_feet_y - fall_margin, 10, fall_margin)
    
    for i in range(len(rect_list)):
        if i < len(platforms) and platforms[i][4] == "intact":
            target_landing_surface = platforms[i][1] + 15
            
            if rect_list[i].colliderect(player_feet) and not jump and y_change > 0:
                if (player_feet_y - y_change) <= target_landing_surface + 10:
                    
                    if len(platforms[i]) > 5 and platforms[i][5] != -1:
                        booster_x = platforms[i][0] + platforms[i][5]
                        booster_y = target_landing_surface - BOOSTER_H
                        booster_rect = pygame.Rect(booster_x, booster_y, BOOSTER_W, BOOSTER_H)
                        
                        if player_feet.colliderect(booster_rect):
                            is_boosting = True
                            booster_timer = BOOSTER_DURATION
                            platforms[i][5] = -1  
                            break

                    Y = target_landing_surface - 60
                    y_change = 0
                    is_crouching = True
                    crouch_timer = CROUCH_DURATION
                    break
    return jump

def update_player(y_position):
    global jump_height, gravity, y_change, jump, score, player_speed, is_crouching, crouch_timer, is_boosting, booster_timer
    
    if score >= 100:
        jump_height = 17.5  
        gravity = 0.5    
        player_speed = 8  
    else:
        jump_height = 15.5
        gravity = 0.42
        player_speed = 6
    
    if is_boosting:
        y_change = -booster_speed
        booster_timer -= 1
        if booster_timer % 10 == 0:
            score += 1
        if booster_timer <= 0:
            is_boosting = False
            y_change = 0 
        y_position += y_change
        return y_position

    if is_crouching:
        crouch_timer -= 1
        if crouch_timer <= 0:
            is_crouching = False
            jump = True
        else:
            return y_position 
            
    if jump:
        y_change = -jump_height
        jump = False
        
    y_position += y_change   
    y_change += gravity
    return y_position
  
def update_platforms(platforms_list, y_position, change):
    global score  

    auto_scroll_speed = 2 if score >= 100 else 1
    for platform in platforms_list:
        platform[1] += auto_scroll_speed

    if y_position <= 400 and change < 0:
        for platform in platforms_list:
            platform[1] -= change

    if len(platforms_list) > 0:
        highest_y = min(platform[1] for platform in platforms_list)
    else:
        highest_y = 0

    for i in range(len(platforms_list)):
        if platforms_list[i][1] > height:
            if score >= 100:
                new_y = highest_y - random.randint(180, 220) 
            elif 30 <= score < 100:
                new_y = highest_y - random.randint(100, 150)
            else:
                new_y = highest_y - random.randint(200, 250) 

            new_x = random.randint(0, width - PLATFORM_W)
            booster_state = random.randint(0, PLATFORM_W - BOOSTER_W) if random.random() < 0.20 else -1
            
            platforms_list[i] = [new_x, new_y, PLATFORM_W, PLATFORM_H, "intact", booster_state]
            highest_y = new_y
            score += 1  

    return platforms_list                        


def draw_button(text, x, y, w, h, normal_color, hover_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        pygame.draw.rect(screen, hover_color, (x, y, w, h), border_radius=10)
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, normal_color, (x, y, w, h), border_radius=10)
        
    text_surf = button_font.render(text, True, white)
    text_rect = text_surf.get_rect(center=((x + w/2), (y + h/2)))
    screen.blit(text_surf, text_rect)
    return False


running = True
boss_enemy = Enemy()
falling_blocks = [] 

while running:
    timer.tick(fps)
    
    # -------------------------------------------------------------
    # STATE 1: MAIN MENU
    # -------------------------------------------------------------
    if game_state == "MENU":
        # Draw dynamic Front Page Menu background
        screen.blit(menu_bg_img, (0, 0)) 
        
        # Draw the image title logo if available, else use text fallback
        if title_img:
            screen.blit(title_img, (width // 2 - 225, 40)) 
        else:
            fallback_text = title_font.render("Swampy Jumper", True, white)
            fallback_rect = fallback_text.get_rect(center=(width // 2, 150))
            screen.blit(fallback_text, fallback_rect)
        
        # Decorative Frog Drawing on the Main Page
        screen.blit(img_normal, (width // 2 - 75, 270))
        
        # Render Balanced Buttons
        if draw_button("START GAME", 200, 460, 200, 50, dark_green, light_green):
            game_state = "GAME"
            pygame.time.delay(150) 
            
        if draw_button("LOAD GAME", 200, 530, 200, 50, blue, dark_blue):
            game_state = "LOAD_GAME"
            pygame.time.delay(150)
            
        if draw_button("SETTINGS", 200, 600, 200, 50, gray, black):
            game_state = "SETTINGS"
            pygame.time.delay(150)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # -------------------------------------------------------------
    # STATE 2: SETTINGS SUB-MENU
    # -------------------------------------------------------------
    elif game_state == "SETTINGS":
        screen.blit(menu_bg_img, (0, 0))
        info_text = title_font.render("Settings Menu", True, white)
        screen.blit(info_text, info_text.get_rect(center=(width // 2, 200)))
        
        desc_text = font.render("Configure game rules or options here.", True, white)
        screen.blit(desc_text, desc_text.get_rect(center=(width // 2, 350)))
        
        if draw_button("BACK TO MENU", 200, 500, 200, 50, red, orange):
            game_state = "MENU"
            pygame.time.delay(150)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # -------------------------------------------------------------
    # STATE 3: LOAD GAME SUB-MENU
    # -------------------------------------------------------------
    elif game_state == "LOAD_GAME":
        screen.blit(menu_bg_img, (0, 0))
        info_text = title_font.render("Saved Profile", True, white)
        screen.blit(info_text, info_text.get_rect(center=(width // 2, 200)))
        
        desc_text = font.render("No saved sessions discovered.", True, white)
        screen.blit(desc_text, desc_text.get_rect(center=(width // 2, 350)))
        
        if draw_button("BACK TO MENU", 200, 500, 200, 50, red, orange):
            game_state = "MENU"
            pygame.time.delay(150)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # -------------------------------------------------------------
    # STATE 4: THE MAIN ACTIVE GAME CYCLE
    # -------------------------------------------------------------
    elif game_state == "GAME":
        # Draw Gameplay specific background
        screen.blit(bg_img, (0, 0)) 
        
        score_text = font.render(f"Score: {score}", True, black)
        screen.blit(score_text, (10, 10))
        
        if 30 <= score < 100:
            boss_enemy.update(falling_blocks)
            boss_enemy.draw(screen)
        elif score >= 100 and not projectiles_cleared_at_100:
            falling_blocks.clear()
            projectiles_cleared_at_100 = True
        
        if is_boosting:
            screen.blit(img_boosting_visual, (X, Y + 25))
        elif is_crouching:
            screen.blit(img_squished, (X, Y + 25))
        else:
            screen.blit(img_normal, (X, Y))
            
        blocks = []
        for i in range(len(platforms)):
            if platforms[i][4] == "intact":
                screen.blit(platform_img, (platforms[i][0], platforms[i][1]))
                if len(platforms[i]) > 5 and platforms[i][5] != -1:
                    b_x = platforms[i][0] + platforms[i][5]
                    b_y = platforms[i][1] + 15 - BOOSTER_H  
                    pygame.draw.rect(screen, light_green, (b_x, b_y, BOOSTER_W, BOOSTER_H), border_radius=3)
                    pygame.draw.rect(screen, gold, (b_x + 5, b_y + 3, BOOSTER_W - 10, BOOSTER_H - 6), border_radius=2)
            else:
                screen.blit(broken_platform_img, (platforms[i][0], platforms[i][1]))
                
            block = pygame.Rect(platforms[i][0], platforms[i][1] + 15, platforms[i][2], 25)
            blocks.append(block)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        keys = pygame.key.get_pressed()
        x_change = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            x_change = -player_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            x_change = player_speed
                    
        X += x_change
        if X < -75: X = width
        elif X > width: X = -75
        
        jump = check_collision(blocks, jump)       
        
        auto_scroll_speed = 2 if score >= 100 else 1
        Y += auto_scroll_speed
        Y = update_player(Y)
        
        if Y < 400 and y_change < 0:
            Y = 400
            
        platforms = update_platforms(platforms, Y, y_change)
        player_rect = pygame.Rect(X + 45, Y + 30, 60, 95)  
        projectiles_to_remove = []
        
        for projectile in falling_blocks:
            projectile.update(auto_scroll_speed, y_change)
            projectile.draw(screen)
            proj_rect = pygame.Rect(projectile.x, projectile.y, projectile.size, projectile.size)
            
            for platform in platforms:
                if platform[4] == "intact":
                    plat_rect = pygame.Rect(platform[0], platform[1] + 15, platform[2], 25)
                    if proj_rect.colliderect(plat_rect):
                        platform[4] = "broken"  
                        if len(platform) > 5:
                            platform[5] = -1 
                        projectiles_to_remove.append(projectile)
                        break
            
            if proj_rect.colliderect(player_rect) and not is_boosting:
                print("\n=================================")
                print(f"GAME OVER! You were hit by a block!")
                print(f"Your Final Score: {score}")
                print("=================================\n")
                running = False
                
            if (projectile.y > height or projectile.y < -50 or 
                projectile.x < -50 or projectile.x > width + 50):
                projectiles_to_remove.append(projectile)
                
        for proj in projectiles_to_remove:
            if proj in falling_blocks:
                falling_blocks.remove(proj)
        
        if Y > height:
            print(f"Game Over! Fell off the screen. Final Score: {score}")  
            running = False

    pygame.display.flip()

pygame.quit()