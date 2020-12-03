import pygame
import random
from settings import *

vec = pygame.math.Vector2


class Enemy:
    def __init__(self, app, pos, number):
        self.app = app
        self.grid_pos = pos
        self.starting_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.radius = int(self.app.cell_width//2.3)
        self.number = number
        self.colour = self.set_colour()
        self.return_flag = False
        self.direction = vec(0, 0)
        self.personality = self.set_personality()
        self.target = None
        self.speed = 1
        self.left_cage = False

    def update(self):
        if self.return_flag:
            self.target = vec(11, 14)
        else:
            self.target = self.set_target()

        if self.on_person():
            self.eat_person()
        
        if self.personality == 'random' and self.direction == vec(0,0):
            self.direction = vec(0,-1)

        if self.target != self.grid_pos:
            self.pix_pos += self.direction * self.speed
            if self.time_to_move():
                self.move()
        elif self.return_flag and self.target == self.grid_pos:
            self.return_flag = False
            self.personality = 'speedy' 

        # Setting grid position in reference to pix position
        self.grid_pos[0] = (self.pix_pos[0]-TOP_BOTTOM_BUFFER +
                            self.app.cell_width//2)//self.app.cell_width+1
        self.grid_pos[1] = (self.pix_pos[1]-TOP_BOTTOM_BUFFER +
                            self.app.cell_height//2)//self.app.cell_height+1

    def draw(self):
        color = self.colour
        if self.return_flag:
            color = (13, 24,150)
        elif self.personality == 'scared':
            color = (235, 235, 235)
        
        pygame.draw.circle(self.app.screen, color,
                        (int(self.pix_pos.x), int(self.pix_pos.y)), self.radius)

    def set_target(self):
        if self.personality == "speedy":
            return self.app.player.grid_pos
        else:
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(1, 1)
            if self.app.player.grid_pos[0] > COLS//2 and self.app.player.grid_pos[1] < ROWS//2:
                return vec(1, ROWS-2)
            if self.app.player.grid_pos[0] < COLS//2 and self.app.player.grid_pos[1] > ROWS//2:
                return vec(COLS-2, 1)
            else:
                return vec(COLS-2, ROWS-2)

    def time_to_move(self):
        if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
            if self.direction == vec(1, 0) or self.direction == vec(-1, 0) or self.direction == vec(0, 0):
                return True
        if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
            if self.direction == vec(0, 1) or self.direction == vec(0, -1) or self.direction == vec(0, 0):
                return True
        return False

    def move(self):
        if self.personality == "random":
            if self.left_cage:
                self.direction = self.get_random_direction()
            else:
                if self.grid_pos == vec(10,11):
                    self.left_cage = True
                else:
                    self.direction = self.get_path_direction(vec(10,11))
        if self.personality == "slow":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "speedy":
            self.direction = self.get_path_direction(self.target)
        if self.personality == "scared":
            self.direction = self.get_path_direction(self.target)

    def get_path_direction(self, target):
        next_cell = self.find_next_cell_in_path(target)
        xdir = next_cell[0] - self.grid_pos[0]
        ydir = next_cell[1] - self.grid_pos[1]
        return vec(xdir, ydir)

    def on_person(self):
        if self.grid_pos in self.app.persons:
            if int(self.pix_pos.x+TOP_BOTTOM_BUFFER//2) % self.app.cell_width == 0:
                if self.direction == vec(1, 0) or self.direction == vec(-1, 0):
                    return True
            if int(self.pix_pos.y+TOP_BOTTOM_BUFFER//2) % self.app.cell_height == 0:
                if self.direction == vec(0, 1) or self.direction == vec(0, -1):
                    return True
        return False

    def eat_person(self):
        self.app.persons.remove(self.grid_pos)
        self.app.player.current_score -= 50
        if self.app.persons == []:
            self.app.state = 'game_over'

    def find_next_cell_in_path(self, target):
        path = self.BFS([int(self.grid_pos.x), int(self.grid_pos.y)], [
                        int(target[0]), int(target[1])])
        return path[1]

    def BFS(self, start, target):
        grid = [[0 for x in range(28)] for x in range(30)]
        for cell in self.app.walls:
            if cell.x < 28 and cell.y < 30:
                grid[int(cell.y)][int(cell.x)] = 1
        queue = [start]
        path = []
        visited = []
        while queue:
            current = queue[0]
            queue.remove(queue[0])
            visited.append(current)
            if current == target:
                break
            else:
                neighbours = [[0, -1], [1, 0], [0, 1], [-1, 0]]
                for neighbour in neighbours:
                    if neighbour[0]+current[0] >= 0 and neighbour[0] + current[0] < len(grid[0]):
                        if neighbour[1]+current[1] >= 0 and neighbour[1] + current[1] < len(grid):
                            next_cell = [neighbour[0] + current[0],
                                         neighbour[1] + current[1]]
                            if next_cell not in visited:
                                if grid[next_cell[1]][next_cell[0]] != 1:
                                    queue.append(next_cell)
                                    path.append(
                                        {"Current": current, "Next": next_cell})
        shortest = [target]
        while target != start:
            for step in path:
                if step["Next"] == target:
                    target = step["Current"]
                    shortest.insert(0, step["Current"])
        return shortest

    def get_random_direction(self):
        available_directions = []
        
        if self.grid_pos + self.direction not in self.app.walls:
            available_directions.append(self.direction)
        
        if self.direction[0] in [-1, 1]:
            if self.grid_pos + vec(0, -1) not in self.app.walls:
                available_directions.append(vec(0,-1))
            if self.grid_pos + vec(0,1) not in self.app.walls:
                available_directions.append(vec(0,1))
        elif self.direction[1] in [-1, 1]:
            if self.grid_pos + vec(-1, 0) not in self.app.walls:
                available_directions.append(vec(-1,0))
            if self.grid_pos + vec(1,0) not in self.app.walls:
                available_directions.append(vec(1,0))
 
        if len(available_directions) == 1:
            return available_directions[0]
        elif len(available_directions) > 1:
            random_number = random.randint(0, len(available_directions) - 1)
            return available_directions[random_number]
        

    def return_home(self):
        self.return_flag = True

    def get_pix_pos(self):
        return vec((self.grid_pos.x*self.app.cell_width)+TOP_BOTTOM_BUFFER//2+self.app.cell_width//2,
                   (self.grid_pos.y*self.app.cell_height)+TOP_BOTTOM_BUFFER//2 +
                   self.app.cell_height//2)

    def set_colour(self):
        if self.number == 0:
            return (178, 252, 68)
        if self.number == 1:
            return (110, 175, 12)
        if self.number == 2:
            return (74, 112, 16)

    def set_personality(self):
        if self.number == 0:
            return "speedy"
        elif self.number == 1:
            return "random"
        elif self.number == 2:
            return "random"
        else:
            return "random"