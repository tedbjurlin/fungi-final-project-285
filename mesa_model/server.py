import mesa

from .fungi_model import FungiModel
from .FungiContinuousModule import FungiCanvas
from .agents import Hypha
import math


def fungi_draw(agent):
    if isinstance(agent, Hypha):    
        return {"Shape": "line", "w": 2, "Color": "Black"}
    else:
        return {"Shape": "circle", "r": 1, "Filled": "true", "Color": "Red"}


fungi_canvas = FungiCanvas(fungi_draw, 500, 500)
model_params = {
    "width": 5000,
    "height": 5000,
    "pixel_width": 5,
    "pixel_height": 5,
    "cell_width": 100,
    "cell_height": 100,
    "extension_rate": 5000,
    "extension_threshold": 1e-12,
    "lateral_branch_threshold": 1e-11,
    "dichotomous_branch_threshold": 1e-11,
    "delta_t": 0.01,
    "initial_substrate_level": 3e-8,
    "uptake_coefficient_1": 2,
    "uptake_coefficient_2": 4e-9,
    "internal_diffusion_coefficient": 0.5,
}

server = mesa.visualization.ModularServer(
    FungiModel, [fungi_canvas], "Fungi", model_params
)
