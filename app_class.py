import pygame
import sys
import copy
from random import randint
from settings import *
from player_class import *
from enemy_class import *


pygame.init()
vec = pygame.math.Vector2


class App:
    def __init__(self):
        pygame.display.set_caption('Covidia - Game')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = MAZE_WIDTH//COLS
        self.cell_height = MAZE_HEIGHT//ROWS
        self.walls = []
        self.sanitizers = []
        self.masks = []
        self.enemies = []
        self.persons = []
        self.e_pos = []
        self.p_pos = None
        self.load()
        self.player = Player(self, vec(self.p_pos))
        self.make_enemies()

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == 'game over':
                self.game_over_events()
                self.game_over_update()
                self.game_over_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

############################ HELPER FUNCTIONS ##################################

    def draw_text(self, words, screen, pos, size, colour, font_name, centered=False):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(words, False, colour)
        text_size = text.get_size()
        if centered:
            pos[0] = pos[0]-text_size[0]//2
            pos[1] = pos[1]-text_size[1]//2
        screen.blit(text, pos)

    def load(self):
        # Opening walls file
        # Creating walls list with co-ords of walls
        # stored as  a vector
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == "1":
                        self.walls.append(vec(xidx, yidx))
                        self.draw_walls()
                    elif char == ".":
                        x = [False, False, False, True, False,
                             False, False, False, False, False, False]
                        if x[randint(0, len(x) - 1)]:
                            self.persons.append(vec(xidx, yidx))
                    elif char == "I":
                        self.sanitizers.append(vec(xidx, yidx))
                    elif char == "M":
                        self.masks.append(vec(xidx, yidx))
                    elif char == "P":
                        self.p_pos = [xidx, yidx]
                    elif char in ["2", "3", "4", "5"]:
                        self.e_pos.append([xidx, yidx])
                    elif char == "B":
                        pygame.draw.rect(self.screen, WHITE, (xidx*self.cell_width, yidx*self.cell_height,
                                                                  self.cell_width, self.cell_height))

    def make_enemies(self):
        for idx, pos in enumerate(self.e_pos):
            self.enemies.append(Enemy(self, vec(pos), idx))

    def draw_grid(self):
        for x in range(WIDTH//self.cell_width):
            pygame.draw.line(self.screen, GREY, (x*self.cell_width, 0),
                             (x*self.cell_width, HEIGHT))
        for x in range(HEIGHT//self.cell_height):
            pygame.draw.line(self.screen, GREY, (0, x*self.cell_height),
                             (WIDTH, x*self.cell_height))

    def draw_walls(self):
        for wall in self.walls:
            pygame.draw.rect(self.screen, RED, (wall.x*self.cell_width + TOP_BOTTOM_BUFFER//2,
                                                wall.y*self.cell_height + TOP_BOTTOM_BUFFER//2, self.cell_width, self.cell_height))

    def reset(self):
        self.player.lives = 3
        self.player.current_score = 0
        self.player.grid_pos = vec(self.player.starting_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.grid_pos = vec(enemy.starting_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.persons = []
        with open("walls.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == '.':
                        x = [False, False, False, True, False,
                             False, False, False, False, False, False]
                        if x[randint(0, len(x) - 1)]:
                            self.persons.append(vec(xidx, yidx))
        self.state = "playing"


########################### INTRO FUNCTIONS ####################################

    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.state = 'playing'

    def start_update(self):
        pass

    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PUSH SPACE BAR', self.screen, [
                       WIDTH//2, HEIGHT//2-50], START_TEXT_SIZE, (170, 132, 58), START_FONT, centered=True)
        self.draw_text('1 PLAYER ONLY', self.screen, [
                       WIDTH//2, HEIGHT//2+50], START_TEXT_SIZE, (44, 167, 198), START_FONT, centered=True)
        self.draw_text('HIGH SCORE', self.screen, [4, 0],
                       START_TEXT_SIZE, (255, 255, 255), START_FONT)
        pygame.display.update()

########################### PLAYING FUNCTIONS ##################################

    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))

    def playing_update(self):
        self.player.update()
        for enemy in self.enemies:
            enemy.update()

        for enemy in self.enemies:
            if enemy.grid_pos == self.player.grid_pos:
                if self.player.power_up:
                    enemy.return_home()
                else:
                    if not self.player.mask_on:
                        self.remove_life()

    def playing_draw(self):
        self.screen.fill(BLACK)
        self.draw_walls()
        self.draw_sanitizers()
        self.draw_masks()
        self.draw_persons()
        self.draw_text('CURRENT SCORE: {}'.format(self.player.current_score),
                       self.screen, [60, 0], 18, WHITE, START_FONT)
        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()

        pygame.display.update()

    def remove_life(self):
        self.player.lives -= 1
        if self.player.lives == 0:
            self.state = "game over"
        else:
            self.player.quarantine_time = time.time()
            self.player.quarantine()

    def draw_sanitizers(self):
        for sanitizer in self.sanitizers:
            pygame.draw.circle(self.screen, (20, 198, 222),
                               (int(sanitizer.x * self.cell_width) + self.cell_width//2+TOP_BOTTOM_BUFFER//2,
                                int(sanitizer.y * self.cell_height) + self.cell_height//2+TOP_BOTTOM_BUFFER//2), 6)

    def draw_masks(self):
        for mask in self.masks:
            pygame.draw.circle(self.screen, (170, 111, 237),
                               (int(mask.x * self.cell_width) + self.cell_width//2+TOP_BOTTOM_BUFFER//2,
                                int(mask.y * self.cell_height) + self.cell_height//2+TOP_BOTTOM_BUFFER//2), 6)

    def draw_persons(self):
        for person in self.persons:
            pygame.draw.circle(self.screen, (140, 82, 46),
                               (int(person.x * self.cell_width) + self.cell_width//2+TOP_BOTTOM_BUFFER//2,
                                int(person.y * self.cell_height) + self.cell_height//2+TOP_BOTTOM_BUFFER//2), 4)

########################### GAME OVER FUNCTIONS ################################

    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BLACK)
        quit_text = "Press the escape button to QUIT"
        again_text = "Press SPACE bar to PLAY AGAIN"
        ending_text = "GAME OVER, player loses"
        if self.player.lives > 0 and self.player.current_score > 0:
            ending_text = "Player wins, with a score of " + str(self.player.current_score)
        
        self.draw_text(ending_text, self.screen, [
                       WIDTH//2, 100],  32, RED, "arial", centered=True)
        self.draw_text(again_text, self.screen, [
                       WIDTH//2, HEIGHT//2],  36, (190, 190, 190), "arial", centered=True)
        self.draw_text(quit_text, self.screen, [
                       WIDTH//2, HEIGHT//1.5],  36, (190, 190, 190), "arial", centered=True)
        pygame.display.update()
