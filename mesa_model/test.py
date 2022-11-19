import numpy as np
from spitzenkorper import Spitzenkorper
from fungi_model import FungiModel

        
model = FungiModel(500, 500, 5, 5)

for i in range(1000):
    model.step()