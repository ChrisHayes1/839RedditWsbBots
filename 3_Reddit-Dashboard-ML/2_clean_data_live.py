import sys
#%load clean_data.py
"""Cleaning comments dataset."""
import pandas as pd
import numpy as np
#import psycopg2
import json
import datetime as dt
import difflib
from textblob import TextBlob
import os
import csv

# Same as clean_data_normies, but I want to clean it up so I can grow results on multiple input files
# I also need to build recent comments either while running or prior to running the cleaning section
outfile = 'lib/data/live_data/raw/temp_clean/my_clean_data_live_r1g1s1_{}.csv'
current_run = 0

def diff_ratio(_a, _b):
    return difflib.SequenceMatcher(a=_a, b=_b).ratio()


def last_30(a, b):
    recent_comment_date = pd.to_datetime(b/1000, unit='s')
    #print(f"a = {a} and b = {b} and recent_comment_date = {recent_comment_date}")
    return a - dt.timedelta(days=30) < recent_comment_date
    #recent_comment_date = pd.to_datetime(b/1000, format='%Y%m%d%H%M%S',  errors='coerce')
    #print(f"a = {a} and b = {b} and recent_comment_date = {recent_comment_date}")
    #return a - dt.timedelta(days=30) < recent_comment_date


####
# I removed recent comments in scrapping because of size, but need to rebuild it here prior to calculating below
# I need a running count of comments by author, but am not sure if .apply is serial (which it would have to be)
# to work with a simple approach
####
# my_columns = ["no_follow", "link_id", 
#                "author", "author_verified", "author_comment_karma",
#                "author_link_karma",  "created_utc",
#                "over_18", "body", "is_submitter", "recent_comments"]

#columns = ['banned_by', 'downs', 'quarantine', 'num_reports', 'num_comments', 'score', 'ups', 'controversiality', 'gilded']


author_comments = ""
recent_authors = ""
num = 0
df_temp = pd.DataFrame()
is_start = True

def calc_stats(comment):
    global author_comments
    global recent_authors
    global df_temp
    global is_start

    if is_start:
        is_start = False
        return comment

    # On a new set of comments
    if comment['author'] != recent_authors:        
        recent_authors = comment['author'] 
        author_comments = ""
        df_temp = pd.DataFrame()

    # Build list of recent comments as we go
    author_comments = df_temp.to_json(orient='records')
    comment['recent_comments'] = author_comments
    df_temp = df_temp.append(comment, ignore_index=True)
    #df_temp = df_temp[my_columns]
    df_temp = df_temp.drop(['recent_comments'], axis=1)                

    # track progress
    global num
    num += 1
    if (num % 1000 == 0): print(num)
    #print(f"\n{num} - Author {comment['author']} has {len(df_temp)} comments")
    #print(f"\n...current comment = {comment['body']}")
    #print(f"\nrecent comments are {author_comments}")


    recent_comments = pd.read_json(author_comments, dtype={
        "banned_by": str,
        "no_follow": bool,
        "link_id": str,
        "gilded": np.float64,
        "author": str,
        "author_verified": bool,
        "author_comment_karma": np.float64,
        "author_link_karma": np.float64,
        "num_comments": np.float64,
        "created_utc": np.datetime64,
        "score": np.float64,
        "over_18": bool,
        "body": str,
        "downs": np.float64,
        "is_submitter": bool,
        "num_reports": np.float64,
        "controversiality": np.float64,
        "quarantine": bool,
        "ups": np.float64})
    
    #print(f"{comment['author']} has {len(recent_comments)}")

    if (len(recent_comments) > 0):
        #print(f"parsing recent comments - # recent comments = {len(recent_comments)}")
        comment['recent_num_comments'] = len(recent_comments)
        comment['recent_num_last_30_days'] = recent_comments['created_utc'].apply(
            lambda x: last_30(comment['created_utc'], x)).sum()
        comment['recent_avg_no_follow'] = recent_comments['no_follow'].mean()
        comment['recent_avg_gilded'] = recent_comments['gilded'].mean()
        comment['recent_avg_responses'] = recent_comments['num_comments'].mean()
        comment['recent_percent_neg_score'] = recent_comments['score'].apply(lambda x: x < 0).mean() * 100
        comment['recent_avg_score'] = recent_comments['score'].mean()
        comment['recent_min_score'] = recent_comments['score'].min()
        comment['recent_avg_controversiality'] = recent_comments['controversiality'].mean()
        comment['recent_avg_ups'] = recent_comments['ups'].mean()
        diff = recent_comments['body'].str.slice(stop=200).fillna('').apply(lambda x: diff_ratio(comment['body'], x))
        comment['recent_avg_diff_ratio'] = diff.mean()
        comment['recent_max_diff_ratio'] = diff.max()
        scores = recent_comments['body'].append(pd.Series(comment['body'])).apply(
            lambda x: TextBlob(x).sentiment.polarity)
        comment['recent_avg_sentiment_polarity'] = scores.mean()
        comment['recent_min_sentiment_polarity'] = scores.min()

    return comment


def clean_comments(file):
            
    with open(file) as f:
        my_data = pd.read_csv(f,  sep=',',  dtype={
            "banned_by": str,
            "no_follow": str,
            "link_id": str,
            "gilded": str,
            "author": str,
            "author_verified": str,
            "author_comment_karma": np.float64,
            "author_link_karma": np.float64,
            "num_comments": np.float64,
            "created_utc": np.float64,
            "score": np.float64,
            "over_18": str,
            "body": str,
            "downs": np.float64,
            "is_submitter": str,
            "num_reports": np.float64,
            "controversiality": np.float64,
            "quarantine": str,
            "ups": np.float64,
        })

    
    my_data['is_bot'] = 'false'
    my_data['is_troll'] = 'false'
    
    #print(my_data['body'])

    # drop duplicates
    dupes = len(my_data)
    my_data = my_data.drop_duplicates(subset=['author','link_id','created_utc'])
    print("Duplicates: ", dupes - len(my_data))

    # remove escape characters to make parsing easier
    my_data['body'] = my_data['body'].str.replace('\\','')

    # format columns
    my_data['created_utc'] = pd.to_datetime(my_data['created_utc'].values, unit='s')
    my_data['body'] = my_data['body'].str.slice(stop=200).fillna('')
    my_data['is_bot'] = my_data['is_bot'].map({'true':True}).fillna(False)
    my_data['is_troll'] = my_data['is_troll'].map({'true':True, 'false':False}).fillna(False)
    my_data['is_troll'] = my_data['is_troll'].map({'true':True, 'false':False}).fillna(False)
    my_data['over_18'] = my_data['over_18'].map({'true':True, 'false':False}).fillna(False)
    my_data['is_submitter'] = my_data['is_submitter'].map({'true':True, 'false':False}).fillna(False)
    my_data['author_verified'] = my_data['author_verified'].map({'true':True, 'false':False}).fillna(False)
    my_data['no_follow'] = my_data['no_follow'].map({'true':True, 'false':False}).fillna(False)



    # add our new stats columns
    my_data['recent_num_comments'] = pd.Series(np.zeros(len(my_data.index), np.int64))
    my_data['recent_num_last_30_days'] = pd.Series(np.zeros(len(my_data.index), np.int64))
    my_data['recent_avg_no_follow'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_avg_gilded'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_avg_responses'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_percent_neg_score'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_avg_score'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_min_score'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_avg_controversiality'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_avg_ups'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_avg_diff_ratio'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_max_diff_ratio'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_avg_sentiment_polarity'] = pd.Series(np.zeros(len(my_data.index), np.float64))
    my_data['recent_min_sentiment_polarity'] = pd.Series(np.zeros(len(my_data.index), np.float64))

    # Count num of bots and trolls
    bots = my_data['is_bot']
    trolls = my_data['is_troll']
    normies = my_data[(my_data.is_bot == False) & (my_data.is_troll == False)]
    print("Number of bot comments: ", bots.sum())
    print("Number of troll comments:", trolls.sum())
    print("Number of normal comments:", len(normies))

    bot_authors = my_data[my_data['is_bot'] == True][['author']]
    troll_authors = my_data[my_data['is_troll'] == True][['author']]
    print("Number of bot authors: ", len(np.unique(bot_authors)))
    print("Number of troll authors:", len(np.unique(troll_authors)))

    # Num of users
    users = my_data['author'].values
    num_of_users = np.unique(users)
    print("Number of total authors: ", len(num_of_users))


    #Build stats
    new_data = my_data.apply(calc_stats, axis=1)

    new_data['target'] = 'normal'

    # Delete is_bot and is_troll collumns and add targets column
    columns = ['is_bot', 'is_troll']
    new_data.drop(columns, inplace=True, axis=1)

    # Delete recent_comments to save space
    columns = ['recent_comments']
    new_data.drop(columns, inplace=True, axis=1)
    out_columns = ['no_follow',
        'link_id',
        'author',
        'author_verified',
        'author_comment_karma',
        'author_link_karma',
        'created_utc',
        'over_18',
        'body',
        'is_submitter',
        'recent_num_comments',
        'recent_num_last_30_days',
        'recent_avg_no_follow',
        'recent_avg_gilded',
        'recent_avg_responses',
        'recent_percent_neg_score',
        'recent_avg_score',
        'recent_min_score',
        'recent_avg_controversiality',
        'recent_avg_ups',
        'recent_avg_diff_ratio',
        'recent_max_diff_ratio',
        'recent_avg_sentiment_polarity',
        'recent_min_sentiment_polarity',
        'target']
    new_data = new_data[out_columns]

    #if current_run == 0:
    new_data.to_csv(outfile.format(current_run),  sep=',', index=False)
    # else:
    #     new_data.to_csv(outfile, mode='a', sep=',', index=False, header=False)

    


def main():
    # Loop through folder pulling in files
    # Run clean on each file
    # Build aggregate results set
    global current_run
    start = dt.datetime.now().strftime('%H:%M:%S')
    print(f"Starting at {start}")

    if len(sys.argv) == 2:
        directory = sys.argv[1]
    else:
        print("Usage: clean_data_live <folder>")
        return

    # itterate through folder
    for filename in os.listdir(directory):        
        if filename.endswith(".csv"):             
            file = os.path.join(directory, filename)
            print(f"Running {file}")
            clean_comments(file)
            current_run += 1
            continue
        else:
            continue


    #df = pd.read_csv(file_in, index_col=False)
    end = dt.datetime.now().strftime('%H:%M:%S')
    print("The data cleaning finished correctly!!!")
    print(f"Started at {start} ended at {end}")


if __name__ == "__main__":
    main()