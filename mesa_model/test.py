import numpy as np
from spitzenkorper import Spitzenkorper
from fungi_model import FungiModel

        
model = FungiModel(500, 500, 10, 10)

for i in range(1000):
    model.step()