import csv
import pandas as pd
import numpy as np
import os

directory = "./normie_data/updated/"

def clean_comments(mFile):
    with open(mFile) as f:
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

# itterate through folder
for filename in os.listdir(directory):        
    if filename.endswith(".csv"):             
        file = os.path.join(directory, filename)
        print(f"Running {file}")
        clean_comments(file)
        continue
    else:
        continue




# try:
#     recent_comments = pd.read_json(directory)
# except exception:
#     print "Error found"



#
# file = open(directory, "w+")
# reader = csv.reader(file, delimiter=',')
# for row in reader:
#     row = row.str.replace('\\','')

# reader.close()


