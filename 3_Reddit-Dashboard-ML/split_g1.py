import pandas as pd

in_file = "../Data/Run01/live/raw/LiveData_n0_1_ReadyForClean.csv"
#in_file = "./test_set.csv"
out_file = "../Data/Run01/live/raw/subsets/LiveData_n0_1_ReadyForClean_subset{}.csv"
num_slices = 8
head_size = 10000

is_splices = True

print("About to read in file")
df = pd.read_csv(in_file)
print("Read in file")

if is_splices:
    
    total_len = len(df)
    slice_len = int(total_len/num_slices)

    current = 0
    next_spot = slice_len

    for i in range(1, num_slices+1):
        print(f"running {i} in range {current} : {next_spot}")  
        df_out = df[current:next_spot]
        df_out.to_csv(out_file.format(i), index=False)    
        current = next_spot + 1
        if i == num_slices:
            next_spot = len(df)
        else:
            next_spot = current + slice_len
else:
    df_out = df.head(head_size)
    df_out.to_csv(out_file, index=False)    
    



