import pygame
import random
import sys
import pickle

# Initialize Pygame
pygame.init()

# Game window dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 40
PLAYER_SPEED = 5

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Eldoria: The Lost Artifacts")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)

# Fonts
font = pygame.font.Font(None, 36)

# Player sprite (placeholder)
player_sprite = pygame.Surface((GRID_SIZE, GRID_SIZE))
player_sprite.fill(GREEN)

# Define creature stats and types
creature_types = {
    "Fire": {"color": RED, "health": 120, "attack": 30, "defense": 20, "special": "Fireball"},
    "Water": {"color": BLUE, "health": 100, "attack": 25, "defense": 30, "special": "Water Blast"},
    "Earth": {"color": YELLOW, "health": 150, "attack": 20, "defense": 40, "special": "Rock Throw"},
    "Air": {"color": CYAN, "health": 80, "attack": 35, "defense": 15, "special": "Wind Slash"},
}

# Define Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = player_sprite
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.captures = []
        self.current_creature = None
        self.active_quest = None
        self.experience = 0
        self.level = 1
        self.stats = {"health": 100, "attack": 20, "defense": 10}
        self.items = {"bomb": False, "bow": False}  # Inventory items

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

    def gain_experience(self, amount):
        self.experience += amount
        if self.experience >= 100 * self.level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience = 0
        self.stats["health"] += 20
        self.stats["attack"] += 5
        self.stats["defense"] += 5

    def assign_quest(self, quest):
        self.active_quest = quest
        print(f"Quest started: {quest['name']}")

    def complete_quest(self):
        if self.active_quest and self.active_quest['progress'] >= self.active_quest['required']:
            self.active_quest['completed'] = True
            print(f"Quest completed: {self.active_quest['name']} - Reward: {self.active_quest['reward']}")
            self.active_quest = None

    def find_item(self, item):
        self.items[item] = True
        print(f"Item found: {item}")

# Define Creature class
class Creature(pygame.sprite.Sprite):
    def __init__(self, x, y, creature_type):
        super().__init__()
        self.creature_type = creature_type
        self.stats = creature_types[creature_type]
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(self.stats["color"])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = self.stats["health"]
        self.attack = self.stats["attack"]
        self.defense = self.stats["defense"]
        self.special = self.stats["special"]

# Define NPC class for quests
class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, name, quest):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.name = name
        self.quest = quest

    def interact(self, player):
        if not self.quest['completed']:
            player.assign_quest(self.quest)
            print(f"Interacted with {self.name} - Quest assigned: {self.quest['name']}")

# Define Treasure class
class Treasure(pygame.sprite.Sprite):
    def __init__(self, x, y, item):
        super().__init__()
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.item = item

    def interact(self, player):
        player.find_item(self.item)
        print(f"Found item: {self.item}")

# Define a function to create a map with points of interest
def draw_map():
    map_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    map_surface.fill(BLACK)
    pygame.draw.rect(map_surface, GREEN, (100, 100, 100, 100))  # Example of a treasure chest
    pygame.draw.circle(map_surface, RED, (400, 300), 50)  # Example of a danger zone
    pygame.draw.rect(map_surface, PURPLE, (200, 400, 50, 50))  # Example of a special point
    return map_surface

# Save game data
def save_game(player):
    game_data = {
        "player": {
            "x": player.rect.x,
            "y": player.rect.y,
            "level": player.level,
            "experience": player.experience,
            "stats": player.stats,
            "items": player.items,
            "captures": [creature.creature_type for creature in player.captures]
        },
        "quests": [quest for quest in quests]
    }
    with open("save_game.pkl", "wb") as f:
        pickle.dump(game_data, f)
    print("Game saved.")

# Load game data
def load_game(player):
    try:
        with open("save_game.pkl", "rb") as f:
            game_data = pickle.load(f)
            player.rect.x = game_data["player"]["x"]
            player.rect.y = game_data["player"]["y"]
            player.level = game_data["player"]["level"]
            player.experience = game_data["player"]["experience"]
            player.stats = game_data["player"]["stats"]
            player.items = game_data["player"]["items"]
            player.captures = [Creature(0, 0, creature_type) for creature_type in game_data["player"]["captures"]]
            global quests
            quests = game_data["quests"]
            print("Game loaded.")
    except FileNotFoundError:
        print("No save file found.")

# Main menu function
def main_menu():
    while True:
        screen.fill(WHITE)
        title_text = font.render("Eldoria: The Lost Artifacts", True, BLACK)
        start_text = font.render("Press 'S' to Start New Game", True, BLACK)
        load_text = font.render("Press 'L' to Load Game", True, BLACK)
        quit_text = font.render("Press 'Q' to Quit", True, BLACK)
        
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(load_text, (SCREEN_WIDTH // 2 - load_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return "start"
                elif event.key == pygame.K_l:
                    return "load"
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()

# Define main function
def main():
    global quests
    quests = []

    # Show main menu
    menu_choice = main_menu()

    # Create player and NPCs
    player = Player(100, 100)
    npc = NPC(300, 300, "Elder", {"name": "Find the Lost Artifact", "progress": 0, "required": 1, "completed": False, "reward": "Gold"})
    treasure = Treasure(500, 500, "Mystic Stone")

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player, npc, treasure)
    
    # Map surface
    map_surface = draw_map()
    
    encounter = False

    if menu_choice == "load":
        load_game(player)

    # Main game loop
    running = True
    while running:
        screen.fill(WHITE)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update(keys)
        
        # Check if player interacts with NPC
        if pygame.sprite.collide_rect(player, npc):
            npc.interact(player)

        # Check if player interacts with Treasure
        if pygame.sprite.collide_rect(player, treasure):
            treasure.interact(player)

        # Random encounter with a wild creature
        if random.random() < 0.05 and not encounter:
            current_creature = Creature(300, 300, random.choice(list(creature_types.keys())))
            encounter = True
            battle(current_creature, player)

        # Draw the map and player
        screen.blit(map_surface, (0, 0))
        all_sprites.draw(screen)
        
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    pygame.quit()
    sys.exit()

# Battle function
def battle(wild_creature, player):
    battle_active = True
    player_creature = Creature(0, 0, "Fire")  # Placeholder
    player.current_creature = player_creature
    player_turn = True
    battle_log = []

    while battle_active:
        screen.fill(WHITE)
        battle_text = font.render(f"A wild {wild_creature.creature_type} appeared!", True, BLACK)
        screen.blit(battle_text, (50, 50))

        player_stats = font.render(f"Your {player_creature.creature_type} - HP: {player_creature.health}", True, GREEN)
        wild_stats = font.render(f"Wild {wild_creature.creature_type} - HP: {wild_creature.health}", True, RED)
        screen.blit(player_stats, (50, 100))
        screen.blit(wild_stats, (50, 150))

        for i, log in enumerate(battle_log):
            log_text = font.render(log, True, BLACK)
            screen.blit(log_text, (50, 200 + (i * 30)))

        if player_turn:
            action_text = font.render("Press 'A' to attack or 'C' to capture!", True, BLACK)
            screen.blit(action_text, (50, SCREEN_HEIGHT // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                battle_active = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and player_turn:
                if event.key == pygame.K_a:
                    damage = max(0, player_creature.attack - wild_creature.defense)
                    wild_creature.health -= damage
                    battle_log.append(f"Your {player_creature.creature_type} attacked for {damage} damage!")
                    player_turn = False

                elif event.key == pygame.K_c:
                    capture_chance = random.random()
                    if capture_chance < 0.5:
                        battle_log.append(f"You captured the {wild_creature.creature_type}!")
                        player.captures.append(wild_creature)
                        battle_active = False
                    else:
                        battle_log.append("Capture failed!")
                    player_turn = False

        if not player_turn and wild_creature.health > 0:
            pygame.time.delay(500)
            damage = max(0, wild_creature.attack - player_creature.defense)
            player_creature.health -= damage
            battle_log.append(f"The wild {wild_creature.creature_type} attacked for {damage} damage!")
            player_turn = True

        if player_creature.health <= 0:
            battle_log.append(f"Your {player_creature.creature_type} fainted!")
            battle_active = False
        elif wild_creature.health <= 0:
            battle_log.append(f"Wild {wild_creature.creature_type} fainted!")
            battle_active = False
            if player.active_quest and not player.active_quest['completed']:
                player.active_quest['progress'] += 1
                player.complete_quest()
                player.gain_experience(50)

        pygame.display.flip()

if __name__ == "__main__":
    main()
