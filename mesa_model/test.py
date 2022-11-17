import numpy as np
from spitzenkorper import Spitzenkorper
from fungi_model import FungiModel

        
model = FungiModel()
        
spitz = Spitzenkorper(
    model.next_id(),
    model,
    np.array((1, 3)),
    0.0
)

model.space.place_agent(spitz, spitz.pos)
model.schedule.add(spitz)

model.step()