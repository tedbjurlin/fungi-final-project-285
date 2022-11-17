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
        Create a new Flockers model.

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
        self.init_pop = 8
        self.schedule = mesa.time.RandomActivation(self)
        self.space = mesa.space.ContinuousSpace(width/2, height/2, False, -width/2, -height/2)
        self.hyphae = []
        self.make_agents()
        self.running = True

    def make_agents(self):
        """
        Create self.population agents, with random positions and starting headings.
        """
        for i in range(self.init_pop):
            pos = np.array((0, 0))
            dir = i * (math.pi / 4)
            size = 128 ** (1/2)
            spitz_x = math.cos(dir) * size
            spitz_y = math.sin(dir) * size
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
                dir
            )
            self.space.place_agent(hypha, pos)
            self.space.place_agent(spitz, spitz_pos)
            
            self.hyphae.append(hypha)
            
            self.schedule.add(hypha)
            self.schedule.add(spitz)

    def step(self):
        self.schedule.step()
