import pygame
import time
from settings import *
vec = pygame.math.Vector2


class Player:
    def __init__(self, app, pos):
        self.app = app
        self.starting_pos = [pos.x, pos.y]
        self.grid_pos = pos
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(1, 0)
        self.stored_direction = None
        self.power_up_time = 0
        self.able_to_move = True
        self.mask_on = False
        self.temp_masks = []
        self.mask_on_time = 0
        self.mask_count = 0
        self.temp_sanitizers = []
        self.restore_sanitizer = True
        self.sanitizer_count = 0
        self.current_score = 0
        self.quarantine_time = 0
        self.quarantine_check = False
        self.power_up = False
        self.speed = 1
        self.lives = 3

    def update(self):
        if self.sanitizer_count == 2:
            print('drawing sanitizer')
            self.app.sanitizers.append(self.temp_sanitizers[0])
            self.temp_sanitizers.remove(self.temp_sanitizers[0])
            self.app.draw_sanitizers()
            self.sanitizer_count = 1

        if self.mask_count == 2:
            self.app.masks.append(self.temp_masks[0])
            self.temp_masks.remove(self.temp_masks[0])
            self.app.draw_masks()
            self.mask_count = 1

        if self.quarantine_check:
            if time.time() - self.quarantine_time > 5:
                self.quarantine_check = False
                self.grid_pos = vec(self.starting_pos)
                self.pix_pos = self.get_pix_pos()
                self.direction *= 0
        else:
            if self.able_to_move:
                self.pix_pos += self.direction*self.speed
            
            if self.time_to_move():
                if self.stored_direction != None:
                    self.direction = self.stored_direction
                self.able_to_move = self.can_move()

            # Setting grid position in reference to pix pos
            self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                                self.app.cell_width//2)//self.app.cell_width+1
            self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                                self.app.cell_height//2)//self.app.cell_height+1
            
            if self.on_mask():
                self.wear_mask()

            if self.on_person():
                self.eat_person()

            if self.on_sanitizer():
                self.use_sanitizer()
                self.power_up_time = time.time()

            if time.time() - self.power_up_time > 5:
                self.power_up = False
                self.app.enemies[0].personality = 'speedy'
                self.app.enemies[1].personality = 'random'
                self.app.enemies[2].personality = 'random'
                self.speed = 1

            if time.time() - self.mask_on_time > 5:
                self.mask_on = False
                self.speed = 1

    def draw(self):
        color = PLAYER_COLOUR

        if self.power_up:
            color = (20, 198, 222)
        elif self.mask_on:
            color = (170, 111, 237)
        elif self.quarantine_check:
            color = PLAYER_QUARANTINE_TIME

        pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (int(
            self.pix_pos.x), int(self.pix_pos.y)), self.app.cell_width//2-2)
        
        # Drawing player lives
        for x in range(self.lives):
            pygame.draw.circle(self.app.screen, PLAYER_COLOUR,
                               (30 + 20*x, HEIGHT - 15), 7)


    def on_person(self):
        if self.grid_pos in self.app.persons:
            if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def on_sanitizer(self):
        if self.grid_pos in self.app.sanitizers:
            if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def on_mask(self):
        if self.grid_pos in self.app.masks:
            if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def wear_mask(self):
        if self.mask_count != 2:
            self.mask_count += 1

        self.temp_masks.append(self.app.masks[self.app.masks.index(self.grid_pos)])
        self.app.masks.remove(self.grid_pos)
        self.mask_on = True
        self.mask_on_time = time.time()
        self.speed = 2

    def eat_person(self):
        self.app.persons.remove(self.grid_pos)
        self.current_score += 50
        if self.app.persons == []:
            self.app.state = 'game over'

    def use_sanitizer(self):
        if self.sanitizer_count != 2:
            self.sanitizer_count += 1
        
        self.speed = 2
        self.temp_sanitizers.append(self.app.sanitizers[self.app.sanitizers.index(self.grid_pos)])
        self.app.sanitizers.remove(self.grid_pos)
        self.power_up = True

        for enemy in self.app.enemies:
            if not enemy.return_flag:
                enemy.personality = 'scared'

    def move(self, direction):
        self.stored_direction = direction

    def get_pix_pos(self):
        return vec((self.grid_pos[0]*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2,
                   (self.grid_pos[1]*self.app.cell_height) +
                   TOP_BOTTOM_BUFFER//2+self.app.cell_height//2)

    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True

    def can_move(self):
        for wall in self.app.walls:
            if vec(self.grid_pos + self.direction) == wall:
                return False
        return True

    def quarantine(self):
        self.grid_pos = vec(80, HEIGHT / 2)
        self.pix_pos = vec(80, HEIGHT / 2)
        self.quarantine_check = True

        for enemy in self.app.enemies:
            if not enemy.return_flag:
                enemy.personality = 'random'
