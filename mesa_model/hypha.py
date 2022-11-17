import mesa
import numpy as np

class Hypha(mesa.Agent):
    def __init__(
        self,
        unique_id,
        model,
        pos,
        end_pos,
        direction,
        size
    ):
        """
        Create a new hypha agent.

        Args:
            unique_id: Unique agent identifyer.
            pos: the origin position of the hypha
            direction: the direction that the hypha grew from the origin
            size: the length of the hypha
        """
        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.end_pos = np.array(end_pos)
        self.direction = direction
        self.size = size
        self.parents = []
        self.children = []

    def step(self):
        pass
