import pandas as pd


#read in file

#file_in = "../Data/TrainingData/TrollsBots/raw/old/TrollBot_AuthorCommentDet.csv"
file_in = "../Data/TrainingData/TrollsBots/raw/TrollBot_AuthorDetail_ReadyForCleanings.csv"

file_out = "../Data/TrainingData/TrollsBots/raw/TrollBot_AuthorList.csv"


def main():
    df = pd.read_csv(file_in)
    df = df['author']
    start = len(df)
    df = df.drop_duplicates()
    print(f"Dropped {start-len(df)} duplicates")
    df.to_csv(file_out)

if __name__ == '__main__':
    main()