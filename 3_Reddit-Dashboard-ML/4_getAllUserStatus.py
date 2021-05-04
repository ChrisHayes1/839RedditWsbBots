import pandas as pd
import numpy as np
import os
import sys
import datetime as dt
import time
from getUserStatus import Botidentification
import pickle
from model import RFModel

gs = Botidentification()
df_response = pd.DataFrame()
#out_file = "../Data/Run01/test_run/3_results/result.csv"
out_file = '../Data/Run01/live_data/results/LiveData_Results_n0_{}.csv'
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
    
    #try:
    row['status'] =  gs.get_user_status(df_new.values.tolist())
    #print(row[['author', 'status', 'recent_avg_diff_ratio', 'author_verified', 'author_comment_karma', 'author_comment_karma' , 'author_link_karma', 'recent_avg_score', 'recent_max_diff_ratio', 'recent_avg_ups']])
    return row
    #except ValueError:
    #    return "error"
    
def get_results(df):
    df_new = df.drop(columns='author')
    model = RFModel()

    clf_path = 'lib/models/DecisionTreeClassifier.pkl'
    with open(clf_path, 'rb') as f:
        model.clf = pickle.load(f)

    clean_data_path = 'lib/models/CleanData.pkl'
    with open(clean_data_path, 'rb') as f:
        model.vectorizer = pickle.load(f)

    return model.predict(df_new)


# For each live file, iterate through and ID potential bots
def get_status(file_name):
    global df_response
    print("Running get_status")

    df = pd.read_csv(file_name, dtype={
        'link_id': str,
        'author': str,
        'author_verified': str,
        'author_comment_karma': np.float64,
        'author_link_karma': np.float64,
        'created_utc': str,
        'body': str,
        'recent_num_comments': np.float64,
        'recent_num_last_30_days' :np.float64,
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
    
    df.fillna(0, inplace=True)
    df['author_verified'] = df['author_verified'].map({'True':True, 'False':False}).fillna(False)

    columns = ['author', 
                 'author_comment_karma', 
                 'author_link_karma', 
                 'recent_num_comments', 
                 'recent_num_last_30_days',
                 'recent_avg_responses', 
                 'recent_percent_neg_score', 
                 'recent_avg_score', 
                 'recent_min_score', 
                 'recent_avg_controversiality', 
                 'recent_avg_ups', 
                 'recent_avg_diff_ratio', 
                 'recent_max_diff_ratio', 
                 'recent_avg_sentiment_polarity', 
                 'recent_min_sentiment_polarity']

    # columns = ['author', 'no_follow', 'author_verified', 'author_comment_karma', 'author_link_karma', 'over_18', 'is_submitter', 
    #              'recent_num_comments', 'recent_num_last_30_days', 'recent_avg_no_follow', 'recent_avg_gilded', 
    #              'recent_avg_responses', 'recent_percent_neg_score', 'recent_avg_score', 'recent_min_score', 
    #              'recent_avg_controversiality', 'recent_avg_ups', 'recent_avg_diff_ratio', 'recent_max_diff_ratio', 
    #              'recent_avg_sentiment_polarity', 'recent_min_sentiment_polarity']

    df = df[columns]
    #df['created_utc'] = df['created_utc'].apply(lambda x: time.mktime(dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S").timetuple()))
    #df['created_utc'] = pd.to_datetime(df['created_utc'].values, unit='s')
    
    #print (df)    
    #df = df.apply(query_status, axis=1)
    df['status'] = get_results(df)
    #print(df)
    
    normies = df.loc[df['status'] == 'normal']
    bots = df.loc[df['status'] == 'bot']
    trolls = df.loc[df['status'] == 'troll']
    print("Number of bot comments: ", len(bots))
    print("Number of troll comments:", len(trolls))
    print("Number of normal comments:", len(normies))

    #df = df[['author', 'status']]
    df = df[['author', 'status', 'recent_avg_diff_ratio', 'recent_max_diff_ratio',  'author_comment_karma' , 'author_link_karma']]
    
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
        # itterate through folder
        for filename in os.listdir(directory):        
            if filename.endswith(".csv"):             
                file = os.path.join(directory, filename)
                print(f"Running {file}")
                get_status(file)
                continue                
    else:
        print("Usage: 4_getAllUserStatus.py <folder>")
        #file ="../Data/Run01/test_run/2_cleaned/LiveData_0_CleanedForQuery.csv"
        file = '../Data/Run01/live/clean/LiveData_n0_1_ReadyForTraining_subsetA.csv'
        #file ="../Data/TrainingData/TrollsBots/cleaned/TrollBot_ReadyForTraining_subset.csv"
        print(f"Running {file}")
        get_status(file)
        
    df_response.to_csv(out_file)

    end = dt.datetime.now().strftime('%H:%M:%S')
    print("The data cleaning finished correctly!!!")
    print(f"Started at {start} ended at {end}")


if __name__ == "__main__":
    main()