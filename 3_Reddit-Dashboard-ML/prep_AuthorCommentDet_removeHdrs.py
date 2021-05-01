import os
import sys
import pandas as pd
import numpy as np
import datetime as dt

out_file = 'preped/raw_set_{}_preped.csv'
current_run = 0
directory = ""

#def clean_bad_rows:


def prep_training_files(file):
    df = pd.read_csv(file)
    #print(f"df.info = {df.info()})
    print("Prior", df.shape)
    #print(df)
    #df.author_link_karma.fillna(0, inplace=True)
    try:
        df = df[~(df.author_link_karma.str.contains('author_link_karma') == True)]    
    except AttributeError:
        print("Warning: Attribute Error, may already be in correct format")
        
    print("Post", df.shape)
    #print(df)

    out_path = os.path.join(directory, out_file.format(current_run))
    df.to_csv(out_path)

def main():
    # Loop through folder pulling in files
    # Run clean on each file
    # Build aggregate results set
    global current_run
    global directory
    start = dt.datetime.now().strftime('%H:%M:%S')
    print(f"Starting at {start}")

    if len(sys.argv) == 2:
        directory = sys.argv[1]
        # itterate through folder
        for filename in os.listdir(directory):        
            if filename.endswith(".csv"):             
                file = os.path.join(directory, filename)
                print(f"Running {file}")
                prep_training_files(file)
                current_run += 1
                continue
            else:
                continue
    else:
        print("Usage: clean_data_live <folder>")
        directory = "../Data/Run01/test_run/1_raw/"
        prep_training_files("../Data/Run01/test_run/1_raw/raw_set_2.csv")
        #clean_comments("../Data/TrainingData/NormieData/raw/7g1_run00_1_AuthorCommentDet_ReadyForCleaning_med.csv")

    


    #df = pd.read_csv(file_in, index_col=False)
    end = dt.datetime.now().strftime('%H:%M:%S')
    print("The data cleaning finished correctly!!!")
    print(f"Started at {start} ended at {end}")


if __name__ == "__main__":
    main()