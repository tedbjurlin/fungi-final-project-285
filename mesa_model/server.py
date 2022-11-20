import mesa

from .fungi_model import FungiModel
from .FungiContinuousModule import FungiCanvas
from .agents import Hypha
import math


def fungi_draw(agent):
    if isinstance(agent, Hypha):    
        return {"Shape": "line", "w": 1, "Color": "Black"}
    else:
        return {"Shape": "circle", "r": 0.5, "Filled": "true", "Color": "Red"}


fungi_canvas = FungiCanvas(fungi_draw, 500, 500)
model_params = {
    "width": 500,
    "height": 500,
    "pixel_width": 5,
    "pixel_height": 5,
    "cell_width": 10,
    "cell_height": 10,
    "extension_rate": math.sqrt(128),
    "extension_threshold": 0.3,
    "lateral_branch_threshold": 0.5,
    "dichotomous_branch_threshold": 0.7,
    "dir_change_stdev": math.pi/10,
    "lateral_branch_prob": 0.1,
    "dichotomous_branch_prob": 0.1,
    "delta_t": 1,
    "initial_substrate_level": 10,
    "uptake_coefficient_1": 1,
    "uptake_coefficient_2": 1,
    "internal_diffusion_coefficient": 0.5
}

server = mesa.visualization.ModularServer(
    FungiModel, [fungi_canvas], "Fungi", model_params
)
