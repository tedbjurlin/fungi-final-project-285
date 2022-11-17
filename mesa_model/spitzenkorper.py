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
    ):
        """
        Create a new spitzenkorper agent.

        Args:
            unique_id: Unique agent identifyer.
            pos: Starting position.
            direction: the direction that the spitzenkorper in degrees going 
            counterclockwise from east.
        """
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.direction = direction
        
    def cross_product(self, p1, p2): # borrowed from https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
        return p1[0] * p2[1] - p2[0] * p1[1]
    
    def on_segment(self, p1, p2, p):
        return min(p1[0], p2[0]) <= p[0] <= max(p1[0], p2[0]) and min(p1[1], p2[1]) <= p[1] <= max(p1[1], p2[1])
    
    def direct(self, p1, p2, p3): # borrowed from https://algorithmtutor.com/Computational-Geometry/Determining-if-two-consecutive-segments-turn-left-or-right/
        return self.cross_product(np.subtract(p3, p1), np.subtract(p2, p1))

    def intersect(self, p1, p2, p3, p4): # borrowed from https://algorithmtutor.com/Computational-Geometry/Check-if-two-line-segment-intersect/
        d1 = self.direct(p3, p4, p1)
        d2 = self.direct(p3, p4, p2)
        d3 = self.direct(p1, p2, p3)
        d4 = self.direct(p1, p2, p4)

        if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
            ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
            return True

        elif d1 == 0 and self.on_segment(p3, p4, p1):
            return True
        elif d2 == 0 and self.on_segment(p3, p4, p2):
            return True
        elif d3 == 0 and self.on_segment(p1, p2, p3):
            return True
        elif d4 == 0 and self.on_segment(p1, p2, p4):
            return True
        else:
            return False

    def step(self):
        old_pos = self.pos
        
        self.direction = ((random.random() * math.pi / 4) - (math.pi / 8)) + self.direction
        
        size = random.random() * math.sqrt(128)
        
        x = old_pos[0] + math.cos(self.direction) * size
        y = old_pos[1] + math.sin(self.direction) * size
        
        self.pos = np.array((x, y))
        
        hypha = Hypha(
            self.model.next_id(),
            self.model,
            old_pos,
            self.pos,
            self.direction,
            size
        )
        
        for h in self.model.hyphae:
            if self.intersect(hypha.pos, hypha.end_pos, h.pos, h.end_pos):
                print('intersect')
        
        if random.random() < 0.05:
            spitz = Spitzenkorper(
                self.model.next_id(),
                self.model,
                self.pos,
                self.direction + (math.pi / 4)
            )
            self.direction -= math.pi / 4
            
            self.model.space.place_agent(spitz, self.pos)
            self.model.schedule.add(spitz)
        
        self.model.space.move_agent(self, self.pos)
        self.model.space.place_agent(hypha, old_pos)
        self.model.schedule.add(hypha)
        
