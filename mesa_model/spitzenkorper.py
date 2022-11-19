import mesa
import numpy as np
import random
import math

from .hypha import Hypha

class Spitzenkorper(mesa.Agent):
    def __init__(
        self,
        unique_id,
        model,
        pos,
        direction,
        hypha
    ):
        """
        Create a new spitzenkorper agent.

        Args:
            unique_id: Unique agent identifyer.
            pos: Starting position.
            direction: the direction that the spitzenkorper in degrees going 
            counterclockwise from east.
            hypha: the hypha that the spitzenkorper is attatched to
        """
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.direction = direction
        self.hypha = hypha
    
    def get_intersection(self, p0, p1, p2, p3): # from https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        s1_x = p1[0] - p0[0]
        s1_y = p1[1] - p0[1]
        s2_x = p3[0] - p2[0]
        s2_y = p3[1] - p2[1]

        s = (-s1_y * (p0[0] - p2[0]) + s1_x * (p0[1] - p2[1])) / (-s2_x * s1_y + s1_x * s2_y)
        t = ( s2_x * (p0[1] - p2[1]) - s2_y * (p0[0] - p2[0])) / (-s2_x * s1_y + s1_x * s2_y)

        if (s >= 0 and s <= 1 and t >= 0 and t <= 1):
            # Collision detected
            return True, p0[0] + (t * s1_x), p0[1] + (t * s1_y)

        return False, None, None; # No collision

    def step(self):
        old_pos = self.pos
        
        print(old_pos)

        self.direction = self.choose_direction()
        
        size = self.choose_length()
        
        x = old_pos[0] + math.cos(self.direction) * size
        y = old_pos[1] + math.sin(self.direction) * size
        
        # it works ¯\_(ツ)_/¯
        if x >= self.model.width:
            print(self.model.width, old_pos[0], size)
            self.direction = math.acos((self.model.width - old_pos[0]) / size)
            if old_pos[1] > y:
                self.direction *= -1
            x = self.model.width - 1
            y = old_pos[1] + math.sin(self.direction) * size
        elif y >= self.model.height:
            print(self.model.height, old_pos[1], size)
            self.direction = math.asin((self.model.height - old_pos[1]) / size)
            if old_pos[0] > x:
                self.direction += (math.pi / 2 - self.direction) * 2
            x = old_pos[0] + math.cos(self.direction) * size
            y = self.model.height - 1
        elif x <= 0:
            print(0, old_pos[0], size)
            self.direction = math.acos(-old_pos[0] / size)
            if old_pos[1] > y:
                self.direction += (math.pi - self.direction) * 2
            x = 1
            y = old_pos[1] + math.sin(self.direction) * size
        elif y <= 0:
            print(0, old_pos[1], size)
            self.direction = math.asin(-old_pos[1] / size)
            if old_pos[0] > x:
                self.direction -= (3 * math.pi / 2 - self.direction) * 2
            y = 1
            x = old_pos[0] + math.cos(self.direction) * size
        
        if x >= self.model.width \
            or y <= 0 \
            or y >= self.model.height \
            or x <= 0:
            self.model.schedule.remove(self)
            return
        
        self.pos = np.array((x, y))
        
        hypha = Hypha(
            self.model.next_id(),
            self.model,
            old_pos,
            self.pos,
            self.direction,
            size
        )
        
        hypha.parents.append(self.hypha)

        
        for h in self.model.hyphae:
            b, x0, y0 = self.get_intersection(hypha.pos, hypha.end_pos, h.pos, h.end_pos)
            if b and h != self.hypha and sorted(hypha.parents) != sorted(h.parents):
                
                size = self.model.space.get_distance(old_pos, np.array((x0, y0)))
                
                hypha = Hypha(
                    self.model.next_id(),
                    self.model,
                    old_pos,
                    np.array((x0, y0)),
                    self.direction,
                    size
                )
                
                hypha.parents.append(self.hypha)
                self.hypha.children.append(hypha)
                self.hypha = hypha
                self.model.hyphae.append(hypha)
                
                self.model.space.place_agent(hypha, old_pos)
                self.model.schedule.add(hypha)
                self.model.schedule.remove(self)
                return
                        
        self.hypha.children.append(hypha)
        self.hypha = hypha
        
        if self.branch_chance():
            self.branch_function()
        
        self.model.space.move_agent(self, self.pos)
        self.model.space.place_agent(hypha, old_pos)
        self.model.schedule.add(hypha)
        self.model.hyphae.append(hypha)

    def choose_length(self):
        return random.random() * math.sqrt(128)

    def choose_direction(self):
        return ((random.random() * math.pi / 4) - (math.pi / 8)) + self.direction

    def branch_function(self):
        spitz = Spitzenkorper(
                self.model.next_id(),
                self.model,
                self.pos,
                self.direction + (math.pi / 4) * (random.random() + 0.05),
                self.hypha
            )
        self.direction -= math.pi / 4 * (random.random() + 0.05)
            
        self.model.spitz_to_add.append(spitz)

    def branch_chance(self):
        return random.random() < 1