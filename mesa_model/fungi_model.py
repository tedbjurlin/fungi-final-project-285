import mesa
import numpy as np
import math

from .hypha import Hypha
from .spitzenkorper import Spitzenkorper

class FungiModel(mesa.Model):
    
    
    def __init__(
        self,
        width=100,
        height=100,
    ):
        """
        Create a new Flockers model.pip

        Args:
            population: Number of Boids
            width, height: Size of the space.
            speed: How fast should the Boids move.
            vision: How far around should each Boid look for its neighbors
            separation: What's the minimum distance each Boid will attempt to
                    keep from any other
            cohere, separate, match: factors for the relative importance of
                    the three drives."""
        super().__init__()
        self.width = width
        if self.width % 10 != 0:
            raise Exception('Width must be divisible by 10!')
        self.height = height
        if self.height % 10 != 0:
            raise Exception('Height must be divisible by 10!')
        self.init_pop = 8
        self.schedule = mesa.time.RandomActivation(self)
        self.space = mesa.space.ContinuousSpace(width, height, False)
        self.hyphae = []
        self.spitz_to_add = []
        self.make_agents()
        self.running = True

    def make_agents(self):
        """
        Create self.population agents, with random positions and starting headings.
        """
        for i in range(self.init_pop):
            pos = np.array((self.width / 2, self.height / 2))
            dir = i * (math.pi / 4)
            size = 128 ** (1/2)
            spitz_x = math.cos(dir) * size + pos[0]
            spitz_y = math.sin(dir) * size + pos[1]
            spitz_pos = np.array((spitz_x, spitz_y))
            hypha = Hypha(
                self.next_id(),
                self,
                pos,
                spitz_pos,
                dir,
                size
            )
            spitz = Spitzenkorper(
                self.next_id(),
                self,
                spitz_pos,
                dir,
                hypha
            )
            self.space.place_agent(hypha, pos)
            self.space.place_agent(spitz, spitz_pos)
            
            self.hyphae.append(hypha)
            
            self.schedule.add(hypha)
            self.schedule.add(spitz)

    def step(self):
        self.schedule.step()
        
        for s in self.spitz_to_add:
            self.space.place_agent(s, s.pos)
            self.schedule.add(s)
            
        self.spitz_to_add = []
        
        if self.schedule.get_agent_count() == 0:
            self.running = False
