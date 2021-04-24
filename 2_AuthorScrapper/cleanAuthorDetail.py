import pandas as pd


#read in file

file_in = "../Data/Run01/5_post_authors.csv"
file_out = "../Data/Run01/6_authors_dedup.csv"



def main():
    df = pd.read_csv(file_in)
    df = df['author']
    df = df.drop_duplicates()
    df.to_csv(file_out)

if __name__ == '__main__':
    main()