import pandas as pd
from matplotlib import pyplot as plt
import os

plt.rcParams["figure.figsize"] = [7.00, 3.50]
plt.rcParams["figure.autolayout"] = True
columns = ["epoch", "lr/pg0"]
df = pd.read_csv(os.path.join(os.curdir, "runs", "detect", "train69", "results.csv"))
plt.plot(df.epoch, df["lr/pg0"])
plt.xlabel("Epoch")
plt.ylabel("Learning Rate")
plt.show()