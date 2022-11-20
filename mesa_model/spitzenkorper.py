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
    
    def get_intersection(self, p0, p1, p2, p3): # from https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect... it works ¯\_(ツ)_/¯
        
        if np.equal(p0, p2).all():
            return False, None, None
        
        s1_x = p1[0] - p0[0]
        s1_y = p1[1] - p0[1]
        s2_x = p3[0] - p2[0]
        s2_y = p3[1] - p2[1]

        s = (-s1_y * (p0[0] - p2[0]) + s1_x * (p0[1] - p2[1])) / (-s2_x * s1_y + s1_x * s2_y)
        t = ( s2_x * (p0[1] - p2[1]) - s2_y * (p0[0] - p2[0])) / (-s2_x * s1_y + s1_x * s2_y)

        if (s >= 0 and s <= 1 and t >= 0 and t <= 1):
            # Collision detected
            return True, p0[0] + (t * s1_x), p0[1] + (t * s1_y)

        return False, None, None # No collision

    def step(self):
        old_pos = self.pos
        
        self.direction = self.choose_direction()
        
        size = self.choose_length()
        
        # choose x and y based 
        x = old_pos[0] + math.cos(self.direction) * size
        y = old_pos[1] + math.sin(self.direction) * size
        
        
        if x >= self.model.width - 1:
            
            # caluclate new direction based on the distance to the wall
            new_dir = math.acos(((self.model.width - 1) - old_pos[0]) / size)

            # switch direction angle based on original angle
            if y > old_pos[0]:
                self.direction = new_dir
            else:
                self.direction = -new_dir

            # set new x and y using new direction
            x = self.model.width - 1
            y = old_pos[1] + math.sin(self.direction) * size
                
        elif y >= self.model.height - 1:

            # caluclate new direction based on the distance to the wall
            new_dir = math.asin(((self.model.height - 1) - old_pos[1]) / size)
            
            # switch direction angle based on original angle
            if x > old_pos[0]:
                self.direction = new_dir
            else: 
                self.direction = new_dir + ((math.pi / 2 - new_dir) * 2)
                
            # set new x and y using new direction
            x = old_pos[0] + math.cos(self.direction) * size
            y = self.model.height - 1
        elif x <= 1:
            
            # caluclate new direction based on the distance to the wall
            new_dir = math.acos((1 - old_pos[0]) / size)
            
            # switch direction angle based on original angle
            if y > old_pos[1]:
                self.direction = new_dir
            else:
                self.direction = -new_dir
                
            # set new x and y using new direction
            x = 1
            y = old_pos[1] + math.sin(self.direction) * size
        elif y <= 1:

            # caluclate new direction based on the distance to the wall
            new_dir = math.asin((1 - old_pos[1]) / size)
            
            # switch direction angle based on original angle
            if x > old_pos[0]:
                self.direction = new_dir
            else:
                self.direction = new_dir - ((math.pi / 2 + new_dir) * 2)
                
            # set new x and y using new direction
            y = 1
            x = old_pos[0] + math.cos(self.direction) * size
            
        # if the new position is still out of bounds we are in a corner
        # we are killing all hyphae that hit a corner for now
        if x >= self.model.width \
            or y <= 0 \
            or y >= self.model.height \
            or x <= 0:
            self.model.schedule.remove(self)
            return
        
        # create our new position for our spitz to move to
        self.pos = np.array((x, y))
        
        # create the new hyphae drawn from the old position to the new one
        hypha = Hypha(
            self.model.next_id(),
            self.model,
            old_pos,
            self.pos,
            self.direction,
            size
        )
        
        hyphaSet = self.find_hyphae(old_pos, self.pos, self.direction, self.model.hyphae, self.model.pixel_width, self.model.pixel_height)
                
        for h in hyphaSet:
            b, x0, y0 = self.get_intersection(hypha.pos, hypha.end_pos, h.pos, h.end_pos)
            if b and h != self.hypha:
                
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
        
        # the current spitzenkorper's hypha is the new one's parent
        # and the new one is the current one's child
        hypha.parents.append(self.hypha)               
        self.hypha.children.append(hypha)
        
        # the spitzenkorper's hypha is now the new one
        self.hypha = hypha
        
        # update grid of hyphae
        self.model.hyphae = self.add_hyphae(old_pos, self.pos, self.direction, self.model.hyphae, self.model.pixel_width, self.model.pixel_height, self.hypha)
        
        # decide to branch
        if self.branch_chance():
            self.branch_function()
        
        # update space and schedule
        self.model.space.move_agent(self, self.pos)
        self.model.space.place_agent(hypha, old_pos)
        self.model.schedule.add(self.hypha)

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
        return hyphaeSet
    
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

    def get_search_values(self, old_pos, new_pos, direction, pixel_width, pixel_height):
        # get beginning pixel
        pixel = np.array((int(old_pos[0] / pixel_width), int(old_pos[1] / pixel_height)))
        
        # get end pixel
        end_pixel = np.array((int(new_pos[0] / pixel_width), int(new_pos[1] / pixel_height)))
        
        # get unit vector form of direction
        v = np.array((math.cos(direction), math.sin(direction)))
        
        x_pix_diff = end_pixel[0] - pixel[0]
        y_pix_diff = end_pixel[1] - pixel[1]
        # get step values for based off diff between pixels
        if x_pix_diff > 0: stepX = 1
        elif x_pix_diff < 0: stepX = -1
        else: stepX = 0
        if y_pix_diff > 0: stepY = 1
        elif y_pix_diff < 0: stepY = -1
        else: stepY = 0
        
        # generate x distance to edge of pixel    
        if stepX < 0:
            minx = old_pos[0] % pixel_width
        else:
            minx = pixel_width - (old_pos[0] % pixel_width)
            
        # scale vector to have x axis equivalent to distance to edge of pixel
        vMaxX = np.array((minx, v[1] * (minx / v[0])))
        
        # used scaled vector to calculate distance along vector to x edge of pixel
        tMaxX = abs(math.sqrt(vMaxX[0]**2 + vMaxX[1]**2))
        
        # scale vector to have x axis equivalent to width of pixel
        vDeltaX = np.array((pixel_width, v[1] * (pixel_width / v[0])))
        
        # use scaled vector to calculate the distance along vetor to travel
        # one pixel along x axis
        tDeltaX = abs(math.sqrt(vDeltaX[0]**2 + vDeltaX[1]**2))
        
        # generate y distance to edge of pixel
        if stepY < 0:
            miny = old_pos[1] % pixel_height
        else:
            miny = pixel_height - (old_pos[1] % pixel_height)
            
        # scale vector to have y axis equaivalent to distance to edge of pixel
        vMaxY = np.array((v[0] * (miny / v[1]), miny))
        
        # use scaled vector to caluclate the distance vector to y edge of pixel
        tMaxY = abs(math.sqrt(vMaxY[0]**2 + vMaxY[1]**2))
        
        # scale vector to have y axis equivalent to pixel height
        vDeltaY = np.array((v[0] * (pixel_height / v[1]), pixel_height))
        
        # use scaled vector to calculate distance along vector to travel
        # one pixel along y axis
        tDeltaY = abs(math.sqrt(vDeltaY[0]**2 + vDeltaY[1]**2))
        
        return pixel,end_pixel,stepX,stepY,tMaxX,tDeltaX,tMaxY,tDeltaY

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
        return random.random() < 0.3