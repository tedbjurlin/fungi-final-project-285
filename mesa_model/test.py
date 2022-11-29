import numpy as np
from fungi_model import FungiModel

        
model = FungiModel()

for i in range(1000):
    model.step()
    print(i)