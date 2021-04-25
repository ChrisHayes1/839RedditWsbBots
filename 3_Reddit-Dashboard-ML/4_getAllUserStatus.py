import pandas as pd
import numpy as np
import os
import sys
import datetime as dt
import time
from getUserStatus import Botidentification

gs = Botidentification()
df_response = pd.DataFrame()
out_file = "./lib/data/live_data/results/result.csv"
is_start = True

print_point = 1000
count = 0

def query_status(row):
    global count
    #query_data = row.to_json(orient='records')
    #row = row.reshape(1, -1)
    df_new = pd.DataFrame()    
    df_new = df_new.append(row)
    df_new = df_new.drop(columns='author')
    #print(df_new)
    count += 1
    if (count % print_point == 0):
        print(f"Count = {count} on {row['author']}")
    return gs.get_user_status(df_new)
    
# For each live file, iterate through and ID potential bots
def get_status(file_name):
    global df_response

    df = pd.read_csv(file_name, dtype={
        'no_follow': str,
        'link_id': str,
        'author': str,
        'author_verified': str,
        'author_comment_karma': np.float64,
        'author_link_karma': np.float64,
        'created_utc': str,
        'over_18': str,
        'body': str,
        'is_submitter': str,
        'recent_num_comments': np.int64,
        'recent_num_last_30_days' :np.int64,
        'recent_avg_no_follow': np.float64,
        'recent_avg_gilded': np.float64,
        'recent_avg_responses': np.float64,
        'recent_percent_neg_score': np.float64,
        'recent_avg_score': np.float64,
        'recent_min_score': np.float64,
        'recent_avg_controversiality': np.float64,
        'recent_avg_ups': np.float64,
        'recent_avg_diff_ratio': np.float64,
        'recent_max_diff_ratio': np.float64,
        'recent_avg_sentiment_polarity': np.float64,
        'recent_min_sentiment_polarity': np.float64,
        'target': str
    })
    
    df['no_follow']  = df['no_follow'].map({'True':True}).fillna(False)
    df['author_verified'] = df['author_verified'].map({'True':True}).fillna(False)
    df['over_18'] = df['over_18'].map({'True':True}).fillna(False)
    df['is_submitter'] = df['is_submitter'].map({'True':True}).fillna(False)

    columns = ['author', 'no_follow', 'author_verified', 'author_comment_karma', 'author_link_karma', 'over_18', 'is_submitter', 
                 'recent_avg_no_follow', 'recent_avg_gilded', 
                 'recent_avg_responses', 'recent_percent_neg_score', 'recent_avg_score', 'recent_min_score', 
                 'recent_avg_controversiality', 'recent_avg_ups', 'recent_avg_diff_ratio', 'recent_max_diff_ratio', 
                 'recent_avg_sentiment_polarity', 'recent_min_sentiment_polarity']


    df = df[columns]
    #df['created_utc'] = df['created_utc'].apply(lambda x: time.mktime(dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timetuple()))
    #df['created_utc'] = pd.to_datetime(df['created_utc'].values, unit='s')
    
    #print (df)    
    df['status'] = df.apply(query_status, axis=1)
    print(df)
    
    normies = df.loc[df['status'] == 'normal']
    bots = df.loc[df['status'] == 'bot']
    trolls = df.loc[df['status'] == 'troll']
    print("Number of bot comments: ", len(bots))
    print("Number of troll comments:", len(trolls))
    print("Number of normal comments:", len(normies))

    df = df[['author', 'status']]
    if is_start:
        df_response = df
    else:
        df_response = df_response.append(df, header=False)

    
    #print(gs.get_user_status(df))



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
        print("Usage: 4_getAllUserStatus.py <folder>")
        return

    # itterate through folder
    for filename in os.listdir(directory):        
        if filename.endswith(".csv"):             
            file = os.path.join(directory, filename)
            print(f"Running {file}")
            get_status(file)
            continue
        else:
            continue


    df_response.to_csv(out_file)

    end = dt.datetime.now().strftime('%H:%M:%S')
    print("The data cleaning finished correctly!!!")
    print(f"Started at {start} ended at {end}")


if __name__ == "__main__":
    main()