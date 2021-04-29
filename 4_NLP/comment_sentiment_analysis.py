##########
# Run sentiment analysis on comment file, produce new file with output
##########

import pandas as pd
import numpy as np
from textblob import TextBlob

in_file = "../Data/Run01/4_post_comments.csv"
out_file = "../Data/Run01/8_Sentiment_analysis.csv"
def getSent(row):
    comment = str(row['comment'])
    return TextBlob(comment).sentiment.polarity

def main():
    #run through comments file, create output file with Comment sentiment analsysis
    df = pd.read_csv(in_file)
    print(df['comment'])
    #df['sentiment_polarity'] = df['comment'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['sentiment_polarity'] = df.apply(getSent, axis=1)
    columns = ['depth','depth_rank']
    df.drop(columns=columns)
    df.to_csv(out_file, index=False)



if __name__ == "__main__":
    main()