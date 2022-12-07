import mesa
import numpy as np
import math
from mesa import DataCollector

from .agents import Spitzenkorper, Hypha


class FungiModel(mesa.Model):
    
    
    def __init__(
        self,
        width=5000,
        height=5000,
        pixel_width=10,
        pixel_height=10,
        cell_width = 100,
        cell_height = 100,
        extension_rate=5000,
        extension_threshold = 1e-12,
        lateral_branch_threshold = 1e-11,
        dichotomous_branch_threshold = 1e-11,
        lateral_branch_prob = 2.25e-15,
        dichotomous_branch_prob = 2.25e-15,
        delta_t = 0.01,
        initial_substrate_level = 3e-8,
        uptake_coefficient_1 = 2,
        uptake_coefficient_2 = 4e-9,
        internal_diffusion_coefficient = 0.5,
        search_length = 25000
        
    ):
        """
        Create a new Fungi Model

        Args:
            width, height: Size of the space.
            pixel_width, pixel_height: Size of pixels for fast pixel traversal.
            cell_width, cell_height: Size of cells of substrate.
            extension_rate: Average growth rate of hypha in micrometers / day.
            extension_threshold: Quantity of substrate required by hypha to extend.
            lateral_branch_threshold: Quantity of substrate required by hypha to branch laterally.
            dichotomous_branch_threshold: Quantity of substrate required by hypha to branch dichotomously.
            lateral_branch_prob: The probability of the hypha branching laterally.
            dichotomous_branch_prob: The probability of the hypha branching dichotomously.
            delta_t: Change in time over each step in days.
            initial_substrate_level: Initial substrate concentration in mol / micrometer^2.
            uptake_coefficient_1: The first coefficient in the uptake equation.
            uptake_coefficient_2: The second coefficient in the uptake equation.
            internal_diffusion_coefficient: The coefficient for internal diffusion.
        
        """
        super().__init__()
        
        # initialize paramters
        self.width = width
        self.height = height
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.extension_rate = extension_rate
        self.extension_threshold = extension_threshold
        self.lateral_branch_threshold = lateral_branch_threshold
        self.dichotomous_branch_threshold = dichotomous_branch_threshold
        self.lateral_branch_prob = lateral_branch_prob
        self.dichotomous_branch_prob = dichotomous_branch_prob
        self.delta_t = delta_t
        self.initial_substrate_level = initial_substrate_level
        self.uptake_coefficient_1 = uptake_coefficient_1
        self.uptake_coefficient_2 = uptake_coefficient_2
        self.internal_diffusion_coefficient = internal_diffusion_coefficient
        self.search_length = search_length
        
        # set non-parameter values
        self.init_pop = 8
        self.schedule = mesa.time.BaseScheduler(self)
        self.space = mesa.space.ContinuousSpace(width, height, False)
        self.hyphae = []
        self.substrate = np.full((int(self.width / self.cell_width), int(self.height / self.cell_height)), self.initial_substrate_level, dtype=float)
        self.spitz_to_add = []
        self.hypha_length = 0
        
        dataCollectorParameters = dict(
            model_reporters={
                "agent_count": (lambda m: m.schedule.get_agent_count()),
                "total_hypha_length": (lambda m: m.hypha_length),
                "total_substrate": (lambda m: m.get_substrate())
                },
            # agent_reporters={
            #     "name": (lambda a:a.unique_id),
            #     "hyphal_length": (lambda a: a.size if isinstance(a, Hypha) else None),
            #     "substrate": (lambda a: a.substrate if isinstance(a, Hypha) else None),
            #     }
        )
        
        self.datacollector = DataCollector(**dataCollectorParameters)
        
        if self.width % self.pixel_width != 0:
            raise Exception('Width must be evenly divisible by pixel_width!')

        if self.height % self.pixel_height != 0:
            raise Exception('Height must be evenly divisible by pixel_height!')
        
        if self.width % self.cell_width != 0:
            raise Exception('Width must be evenly divisible by cell_width!')

        if self.height % self.cell_height != 0:
            raise Exception('Height must be evenly divisible by cell_height!')
        
        for i in range(int(self.width / self.pixel_width)):
            self.hyphae.append([])
            for j in range(int(self.height / self.pixel_height)):
                self.hyphae[i].append([])

        self.make_agents()
        self.running = True
        
    def get_substrate(self):
        substrate = 0
        for i in range(int(self.width / self.cell_width)):
            for j in range(int(self.height / self.cell_height)):
                substrate += self.substrate[i, j] * (self.cell_width * self.cell_height)
        
        return substrate

    def make_agents(self):
        
        
        for i in range(self.init_pop):
            pos = np.array((self.width / 2, self.height / 2))
            dir = i * (math.pi / 4)
            size = self.extension_rate * self.delta_t
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
            
            self.hyphae = spitz.add_hyphae(
                pos,
                spitz_pos,
                dir,
                self.hyphae,
                self.pixel_width,
                self.pixel_height,
                hypha
            )
            
            self.schedule.add(hypha)
            self.schedule.add(spitz)

    def step(self):
        self.hypha_length = 0
        self.schedule.step()
        
        for s in self.spitz_to_add:
            self.space.place_agent(s, s.pos)
            self.schedule.add(s)
            
        self.spitz_to_add = []
            
        self.datacollector.collect(self)
