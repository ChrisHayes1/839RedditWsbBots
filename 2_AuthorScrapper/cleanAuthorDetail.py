import pandas as pd


#read in file

file_in = "../Data/Run01/6n0_authors_dedup.txt"
file_out = "../Data/Run01/6_authors_dedup.csv"



def main():
    df = pd.read_csv(file_in)
    df = df['author']
    start = len(df)
    df = df.drop_duplicates()
    print(f"Dropped {start-len(df)} duplicates")
    #df.to_csv(file_out)

if __name__ == '__main__':
    main()