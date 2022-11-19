import mesa

from .fungi_model import FungiModel
from .FungiContinuousModule import FungiCanvas
from .hypha import Hypha


def fungi_draw(agent):
    if isinstance(agent, Hypha):    
        return {"Shape": "line", "w": 2, "Color": "Black"}
    else:
        return {"Shape": "circle", "r": 1, "Filled": "true", "Color": "Red"}


fungi_canvas = FungiCanvas(fungi_draw, 500, 500)
model_params = {
    "width": 500,
    "height": 500,
    "pixel_width": 50,
    "pixel_height": 50
}

server = mesa.visualization.ModularServer(
    FungiModel, [fungi_canvas], "Fungi", model_params
)
