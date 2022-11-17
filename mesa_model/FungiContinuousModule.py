import mesa
from .hypha import Hypha

# base for continuous visualisation borrowed from mesa example project boid_flockers

class FungiCanvas(mesa.visualization.VisualizationElement):
    local_includes = ["mesa_model/fungi_canvas.js"]
    portrayal_method = None
    canvas_height = 500
    canvas_width = 500

    def __init__(self, portrayal_method, canvas_height=500, canvas_width=500):
        """
        Instantiate a new FungiCanvas
        """
        self.portrayal_method = portrayal_method
        self.canvas_height = canvas_height
        self.canvas_width = canvas_width
        new_element = "new Fungi_Continuous_Module({}, {})".format(
            self.canvas_width, self.canvas_height
        )
        self.js_code = "elements.push(" + new_element + ");"

    def render(self, model):
        space_state = []
        for obj in model.schedule.agents:
            portrayal = self.portrayal_method(obj)
            x, y = obj.pos
            x = (x - model.space.x_min) / (model.space.x_max - model.space.x_min)
            y = (y - model.space.y_min) / (model.space.y_max - model.space.y_min)
            portrayal["x"] = x
            portrayal["y"] = y
            portrayal["direction"] = obj.direction
            if isinstance(obj, Hypha):
                s = obj.size / (model.space.y_max - model.space.y_min)
                portrayal["size"] = s
            space_state.append(portrayal)
        return space_state
