import pandas as pd
import numpy as np

in_file = "./lib/data/training-dump.csv"
train_out_file = "./lib/data/train_group.csv"
test_out_file = "./lib/data/test_group.csv"

df = pd.read_csv(in_file)
df['split'] = np.random.randn(df.shape[0], 1)

msk = np.random.rand(len(df)) <= 0.7
msk2 = np.random.rand(len(df)) <= 0.1

train = df[msk]
test = df[~msk]
subset = df[msk2]

train.to_csv(train_out_file)
test.to_csv(test_out_file)
subset.to_csv("./lib/data/sub_dump.csv")