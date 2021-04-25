import panadas as pd
import numpy as np
import os
import getUserStatus

gs = getUserStatus()
df_response = pd.Dataframe()
df = =pd.Dataframe()

def query_status(row):
    query_data = row.to_json(orient='records')
    
# For each live file, iterate through and ID potential bots
def get_status(file_name):
    df = pd.read_csv(file_name)
    df.apply(query_status, axis=1)
    print()



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
            get_status(file)
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