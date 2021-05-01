import pandas as pd

in_file = "./7g1_run00_1_author_comments_and_attr.csv"
out_file = "./test_set.csv"

df = pd.read_csv(in_file)
df_out = df.head(1000)

df_out.to_csv(out_file)
