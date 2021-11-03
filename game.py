import pygame
import sys
import random
import math
import json

class game_main():
    # Game data class, stores game data
    class game_data():
        def __init__(self):
            print("Initializing gamedata...")
            self.window_size = [300, 400]
            self.tickcount = 0
            self.data_file = "data.json"
            self.last_generated = 300
            self.score = 0
            self.highscore = 0
            self.gamestarted = False
            self.file_data = {}
            self.platforms = []
        
        def load_data(self):
            print("Loading saved gamedata...")
            file = open(self.data_file, "r")
            # Loading JSON data into the filedata
            try:
                self.file_data = json.loads(file.read())
            except ValueError:
                print("[ERROR] Failed to load JSON data while loading saved gamedata")
                return
            
            try:
                self.highscore = self.file_data["highscore"]
            except KeyError:
                print("[WARNING] Failed to load highscore")

        def save_data(self):
            print("Saving gamedata...")
            file = open(self.data_file, "w")
            data = {
                "highscore": self.highscore,
            }
            data_json = json.dumps(data)
            file.write(data_json)
            
            

        def tick(self):
            self.tickcount += 1

        def add_platform(self, platform):
            self.platforms.append(platform)

        def get_platforms(self):
            return self.platforms

        def get_tickcount(self):
            return self.tickcount

    # Game asset class, stores all game assets used
    class game_assets():
        def __init__(self):
            print("Initializing game assets...")
            self.duck_main = pygame.image.load("assets/duck_main.png")
            self.platform = pygame.image.load("assets/platform.png")
            self.platform_d = pygame.image.load("assets/platform_d.png")

    # Main player character class, stores all player data
    class player_character():
        def __init__(self, image : pygame.Surface):
            print("Initializing character...")
            self.asset = pygame.transform.scale(image, [50, 50]) 
            self.rect = image.get_rect(left = 150, top = 225)
            self.flipped = False
            self.velocity = [0, -5]
            self.yoffset = 0

        # Applyig current player velocity to position
        def doVelocity(self):
            self.rect = self.rect.move(self.velocity[0], 0)
            self.yoffset += self.velocity[1]

        # Clamping velocity
        def clampVelocity(self, parent):
            self.velocity = [parent.clamp(self.velocity[0], -3, 3), parent.clamp(self.velocity[1], -5, 50)]

        # Function to modify velocity from outside class
        def affectVelocity(self, ind : int, amount : int):
            self.velocity[ind] += amount

        # Adding "Gravity" to velocity
        def doGravity(self):
            # Left/Right speed decrease
            if self.velocity[0] > 0:
                self.velocity[0] -= 1
                self.flipped = False
            elif self.velocity[0] < 0:
                self.velocity[0] += 1
                self.flipped = True
            # Downwards gravity
            self.velocity[1] += 0.3

        # Function for when player hits a platform and jumps
        def bounce(self):
            self.velocity[1] = -5

            
    # Input manager class, gets called on input events and stores key class
    class input_manager():
        # Simple input key class used to keep track of active keys
        class input_key():
            def __init__(self):
                self.active = False

            def set(self, state : bool):
                self.active = state

        def __init__(self):
            print("Initializing input manager...")
            self.left_arrow = self.input_key()
            self.right_arrow = self.input_key()
        def check_input(self, event : pygame.event, down : bool):
            #print("Checking for input keys")
            if event.key == pygame.K_LEFT:
                self.left_arrow.set(down)
            elif event.key == pygame.K_RIGHT:
                self.right_arrow.set(down)
    
    # Basic platform class
    class platform():
        def __init__(self, pos, asset, destr):
            self.pos = [pos[0] - 50, pos[1]]
            self.destr = destr
            self.asset = pygame.transform.scale(asset, [50, 20])

    # Platform generation function
    def generate_platform(self, amount : int, ylevel : int):
        rects = []
        for i in range(amount):
            test_rect = pygame.Rect(random.randint(30, self.gamedata.window_size[0] - 30), ylevel, 50, 20)
            overlap = False
            for cur_rect in rects:
                if cur_rect.colliderect(test_rect):
                    overlap = True
            if not overlap:
                destructible = (random.randint(1, 6) == 1)
                if destructible:
                    self.gamedata.add_platform(self.platform([test_rect.x, test_rect.y], self.gameassets.platform_d, True))
                else: 
                    self.gamedata.add_platform(self.platform([test_rect.x, test_rect.y], self.gameassets.platform, False))
            rects.append(test_rect)

    # Utility clamping function
    def clamp(self, val, val_min, val_max):
        return min(max(val_min, val), val_max)

    # Main game loop function
    def gameloop(self):
        print("Starting game loop")
        game_tick = pygame.USEREVENT + 1
        # Game ticking, every 15 ms
        pygame.time.set_timer(game_tick, 15)
        # Main game loop
        self.game_running = True
        while self.game_running:
            for event in pygame.event.get():
                # Event checks
                if event.type == pygame.QUIT: 
                    self.game_running = False
                elif event.type == game_tick:
                    self.gamedata.tick()
                    # Only run when game is started
                    if self.gamedata.gamestarted:
                        # Left/Right player movement
                        if self.inputmanager.left_arrow.active:
                            self.main_character.affectVelocity(0, -1)
                        elif self.inputmanager.right_arrow.active:
                            self.main_character.affectVelocity(0, 1)
                        self.main_character.doVelocity()
                        if (self.gamedata.get_tickcount() % 2):
                            self.main_character.doGravity()
                        self.main_character.clampVelocity(self)
                    # Screen offset
                    y_offset = self.main_character.yoffset
                    # Platform generation
                    if self.gamedata.last_generated - y_offset > 50:
                        cur_gen = self.gamedata.last_generated - 90
                        if self.gamedata.score > 50:
                            self.generate_platform(1, cur_gen)
                        else:
                            self.generate_platform(2, cur_gen)
                        self.gamedata.last_generated = cur_gen
                    # Score calculation
                    cur_score = -round(y_offset / 100)
                    if self.gamedata.score < cur_score:
                        self.gamedata.score = cur_score
                    # Death check
                    if cur_score + 5 < self.gamedata.score:
                        self.game_running = False
                    # Highscore check
                    if self.gamedata.score > self.gamedata.highscore:
                        self.gamedata.highscore = self.gamedata.score
                    # Drawing
                    font = pygame.font.SysFont("VerdanaBD", 30)
                    score_text = font.render("SCORE: " + str(self.gamedata.score), 1, (255, 0, 0))
                    highscore_text = font.render("HIGHSCORE: " + str(self.gamedata.highscore), 1, (255, 0, 0))
                    # Player bounce and platform drawing and platform removal
                    self.game_window.fill([255, 255, 255])
                    for platform in self.gamedata.get_platforms():
                        self.game_window.blit(platform.asset, [platform.pos[0], platform.pos[1] - y_offset])
                        test_rect = pygame.Rect(platform.pos[0], platform.pos[1] - y_offset - 25, 50, 10)
                        if test_rect.colliderect(self.main_character.rect) and self.main_character.velocity[1] > 0:
                            self.main_character.bounce()
                            if platform.destr:
                                self.gamedata.platforms.remove(platform)
                        if test_rect.y > 500:
                            self.gamedata.platforms.remove(platform)
                    # Player character drawing
                    self.game_window.blit(pygame.transform.flip(self.main_character.asset, self.main_character.flipped, False), [self.main_character.rect[0] - 25, self.main_character.rect[1]])
                    # Non game UI
                    if not self.gamedata.gamestarted:
                        # Press space to start text
                        start_text = font.render("PRESS SPACE TO START!", 1, (255, 0, 0))
                        self.game_window.blit(start_text, (self.gamedata.window_size[0] / 2 - start_text.get_rect().width / 2, 300))
                    self.game_window.blit(highscore_text, (10, 30))
                    self.game_window.blit(score_text, (10, 10))
                    pygame.display.flip()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.inputmanager.check_input(event, (event.type == pygame.KEYDOWN))
                    if event.key == pygame.K_SPACE:
                        self.gamedata.gamestarted = True
        print("Game ended")
        self.gamedata.save_data()
        sys.exit()
                    
    # Game window initialization
    def init_gamewindow(self):
        print("Initializing game window...")
        self.game_window = pygame.display.set_mode(self.gamedata.window_size)
        pygame.display.set_caption("Squeaky Jump")
        pygame.display.set_icon(self.gameassets.duck_main)

    # Initialize game characters and starter platform
    def init_characters(self):
        print("Initializing game characters...")
        self.main_character = self.player_character(self.gameassets.duck_main)
        self.gamedata.add_platform(self.platform([170, 270], self.gameassets.platform, False))
    
    # Main game initialization
    def __init__(self):
        print("Initializing game...")
        pygame.init()
        self.gameassets = self.game_assets()
        self.gamedata = self.game_data()
        self.inputmanager = self.input_manager()
        self.init_gamewindow()
        self.init_characters()
        self.gamedata.load_data()
        self.gameloop()



game = game_main()