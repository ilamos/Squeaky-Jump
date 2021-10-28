import pygame
import sys
import random
import math

def clamp(val, val_min, val_max):
    return min(max(val_min, val), val_max)

class game_main():
    class game_data():
        def __init__(self):
            print("Initializing gamedata...")
            self.window_size = [300, 400]
            self.tickcount = 0
            self.last_generated = 300
            self.score = 0
            self.gamestarted = False
            self.platforms = []
        
        def tick(self):
            self.tickcount += 1

        def add_platform(self, platform):
            self.platforms.append(platform)

        def get_platforms(self):
            return self.platforms

        def get_tickcount(self):
            return self.tickcount

    class game_assets():
        def __init__(self):
            print("Initializing game assets...")
            self.duck_main = pygame.image.load("assets/duck_main.png")
            self.platform = pygame.image.load("assets/platform.png")

    class player_character():
        def __init__(self, image : pygame.Surface):
            print("Initializing character...")
            self.asset = pygame.transform.scale(image, [50, 50]) 
            self.rect = image.get_rect(left = 150, top = 225)
            self.flipped = False
            self.velocity = [0, -5]
            self.yoffset = 0

        def doVelocity(self):
            self.rect = self.rect.move(self.velocity[0], 0)
            self.yoffset += self.velocity[1]

        def clampVelocity(self):
            self.velocity = [clamp(self.velocity[0], -3, 3), clamp(self.velocity[1], -5, 50)]

        def affectVelocity(self, ind : int, amount : int):
            self.velocity[ind] += amount

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

        def bounce(self):
            self.velocity[1] = -5

            

    class input_manager():
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

    class platform():
        def __init__(self, pos, asset):
            self.pos = [pos[0] - 50, pos[1]]
            self.asset = pygame.transform.scale(asset, [50, 20])

    def generate_platform(self, amount : int, ylevel : int):
        rects = []
        for i in range(amount):
            test_rect = pygame.Rect(random.randint(30, self.gamedata.window_size[0] - 30), ylevel, 50, 20)
            overlap = False
            for cur_rect in rects:
                if cur_rect.colliderect(test_rect):
                    overlap = True
            if not overlap:
                self.gamedata.add_platform(self.platform([test_rect.x, test_rect.y], self.gameassets.platform))
            rects.append(test_rect)

    def gameloop(self):
        print("Starting game loop")
        game_tick = pygame.USEREVENT + 1
        # Game ticking, every 15 ms
        pygame.time.set_timer(game_tick, 15)
        # Main game loop
        game_running = True
        while game_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    game_running = False
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
                        self.main_character.clampVelocity()
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
                        game_running = False
                    # Drawing
                    font = pygame.font.SysFont("VerdanaBD", 30)
                    score_text = font.render("SCORE: " + str(self.gamedata.score), 1, (255, 0, 0))
                    # Player bounce and platform drawing and platform removal
                    self.game_window.fill([255, 255, 255])
                    for platform in self.gamedata.get_platforms():
                        self.game_window.blit(platform.asset, [platform.pos[0], platform.pos[1] - y_offset])
                        test_rect = pygame.Rect(platform.pos[0], platform.pos[1] - y_offset - 25, 50, 10)
                        if test_rect.colliderect(self.main_character.rect) and self.main_character.velocity[1] > 0:
                            self.main_character.bounce()
                        if test_rect.y > 500:
                            self.gamedata.platforms.remove(platform)
                    # Player character drawing
                    self.game_window.blit(pygame.transform.flip(self.main_character.asset, self.main_character.flipped, False), [self.main_character.rect[0] - 25, self.main_character.rect[1]])
                    # Non game UI
                    if not self.gamedata.gamestarted:
                        # Press space to start text
                        start_text = font.render("PRESS SPACE TO START!", 1, (255, 0, 0))
                        self.game_window.blit(start_text, (self.gamedata.window_size[0] / 2 - start_text.get_rect().width / 2, 300))
                    self.game_window.blit(score_text, (10, 10))
                    pygame.display.flip()
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    self.inputmanager.check_input(event, (event.type == pygame.KEYDOWN))
                    if event.key == pygame.K_SPACE:
                        self.gamedata.gamestarted = True
        print("Game ended")
        sys.exit()
                    

    def init_gamewindow(self):
        print("Initializing game window...")
        self.game_window = pygame.display.set_mode(self.gamedata.window_size)
        pygame.display.set_caption("Squeaky Jump")
        pygame.display.set_icon(self.gameassets.duck_main)

    def init_characters(self):
        print("Initializing game characters...")
        self.main_character = self.player_character(self.gameassets.duck_main)
        self.gamedata.add_platform(self.platform([170, 270], self.gameassets.platform))

    def __init__(self):
        print("Initializing game...")
        pygame.init()
        self.gameassets = self.game_assets()
        self.gamedata = self.game_data()
        self.inputmanager = self.input_manager()
        self.init_gamewindow()
        self.init_characters()
        self.gameloop()



game = game_main()