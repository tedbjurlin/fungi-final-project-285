import mesa
import numpy as np
import random
import math

from hypha import Hypha

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
        
        self.direction = self.choose_direction()
        
        size = self.choose_length()
        
        x = old_pos[0] + math.cos(self.direction) * size
        y = old_pos[1] + math.sin(self.direction) * size
        
        # it works ¯\_(ツ)_/¯
        # if x >= self.model.width:
        #     print(self.model.width, old_pos[0], size)
        #     self.direction = math.acos(((self.model.width - 1) - old_pos[0]) / size)
        #     if old_pos[1] > y:
        #         self.direction *= -1
        #     x = self.model.width - 1
        #     y = old_pos[1] + math.sin(self.direction) * size
        # elif y >= self.model.height:
        #     print(self.model.height, old_pos[1], size)
        #     self.direction = math.asin(((self.model.height - 1) - old_pos[1]) / size)
        #     if old_pos[0] > x:
        #         self.direction += (math.pi / 2 - self.direction) * 2
        #     x = old_pos[0] + math.cos(self.direction) * size
        #     y = self.model.height - 1
        # elif x <= 0:
        #     print(0, old_pos[0], size)
        #     self.direction = math.acos(1 - old_pos[0] / size)
        #     if old_pos[1] > y:
        #         self.direction *= -1
        #     x = 1
        #     y = old_pos[1] + math.sin(self.direction) * size
        # elif y <= 0:
        #     print(0, old_pos[1], size)
        #     self.direction = math.asin(1 - old_pos[1] / size)
        #     if old_pos[0] < x:
        #         self.direction += math.pi - self.direction
        #     else:
        #         self.direction -= math.pi + self.direction
        #     y = 1
        #     x = old_pos[0] + math.cos(self.direction) * size
        
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
        
        hyphaSet = self.find_hyphae(old_pos, self.pos, self.direction, self.model.hyphae, self.model.pixel_width, self.model.pixel_height)
        
        print(len(hyphaSet))
        
        for h in hyphaSet:
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
                                
                self.model.hyphae = self.add_hyphae(old_pos, self.pos, self.direction, self.model.hyphae, self.model.width, self.model.height, self.hypha)
                
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
        self.model.schedule.add(self.hypha)
        
        self.model.hyphae = self.add_hyphae(old_pos, self.pos, self.direction, self.model.hyphae, self.model.width, self.model.height, self.hypha)

    def find_hyphae(self, old_pos, new_pos, direction: float, hyphae: list, pixel_width: int, pixel_height: int) -> set:
                
        pixel, end_pixel, stepX, stepY, tMaxX, tDeltaX, tMaxY, tDeltaY = self.get_search_values(old_pos, new_pos, direction, pixel_width, pixel_height)
        
        hyphaeSet = set()
        hyphaeSet.update(hyphae[pixel[0]][pixel[1]])
        
        while not np.equal(pixel, end_pixel).all():
            if 0 > pixel[0] or 0 > pixel[1]:
                breakpoint()
            if tMaxX < tMaxY:
                tMaxX += tDeltaX
                pixel[0] += stepX
            else:
                tMaxY += tDeltaY
                pixel[1] += stepY
            hyphaeSet.update(hyphae[pixel[0]][pixel[1]].copy())
            print(len(hyphae[pixel[0]][pixel[1]]))
        return hyphaeSet

    def get_search_values(self, old_pos, new_pos, direction, pixel_width, pixel_height):
        pixel = np.array((int(old_pos[0] / pixel_width), int(old_pos[1] / pixel_height)))
        end_pixel = np.array((int(new_pos[0] / pixel_width), int(new_pos[1] / pixel_height)))

        stepX = math.copysign(1, new_pos[0] - old_pos[0])
        stepY = math.copysign(1, new_pos[1] - old_pos[1])
        
        direction = ((direction + math.pi) % (math.pi * 2)) - math.pi
        
        v = np.array((math.cos(direction), math.sin(direction)))
                
        if stepX < 0:
            minx = old_pos[0] - int(old_pos[0] / pixel_width) * pixel_width
        else:
            minx = (int(old_pos[0] / pixel_width) * pixel_width + pixel_width) - old_pos[0]
        vMaxX = np.array((minx, v[1] * (minx / v[0])))
        tMaxX = abs(math.sqrt(vMaxX[0]**2 + vMaxX[1]**2))
        vDeltaX = np.array((pixel_width, v[1] * (pixel_width / v[0])))
        tDeltaX = abs(math.sqrt(vDeltaX[0]**2 + vDeltaX[1]**2))
        
        if stepY < 0:
            miny = old_pos[1] - int(old_pos[1] / pixel_height) * pixel_height
        else:
            miny = (int(old_pos[1] / pixel_height) * pixel_height + pixel_height) - old_pos[1]
        vMaxY = np.array((v[0] * (miny / v[1]), miny))
        tMaxY = abs(math.sqrt(vMaxY[0]**2 + vMaxY[1]**2))
        vDeltaY = np.array((v[0] * (pixel_height / v[1]), pixel_height))
        tDeltaY = abs(math.sqrt(vDeltaY[0]**2 + vDeltaY[1]**2))
        
        return pixel,end_pixel,stepX,stepY,tMaxX,tDeltaX,tMaxY,tDeltaY

    def add_hyphae(self, old_pos, new_pos, direction: float, hyphae: list, pixel_width: int, pixel_height: int, hypha: Hypha):
                
        pixel, end_pixel, stepX, stepY, tMaxX, tDeltaX, tMaxY, tDeltaY = self.get_search_values(old_pos, new_pos, direction, pixel_width, pixel_height)
        
        hyphae[pixel[0]][pixel[1]].append(hypha)
        
        while not np.equal(pixel, end_pixel).all():
            if tMaxX < tMaxY:
                tMaxX += tDeltaX
                pixel[0] += stepX
            else:
                tMaxY += tDeltaY
                pixel[1] += stepY
            hyphae[pixel[0]][pixel[1]].append(hypha)
        
        return hyphae


    def choose_length(self):
        return random.random() * math.sqrt(128)

    def choose_direction(self):
        direction = ((random.random() * math.pi / 4) - (math.pi / 8)) + self.direction
        return ((direction + math.pi) % (math.pi * 2)) - math.pi
        

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
        return random.random() < 0.1