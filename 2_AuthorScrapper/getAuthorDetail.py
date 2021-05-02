import pandas as pd
import praw
import prawcore
import time
import datetime
import pprint
# Pull from const path = `https://www.reddit.com/user/${profile.name}/comments.json?limit=25`
# to get JSON user comment data

#CORE_LINK = "https://www.reddit.com/user/{}/comments.json?limit=25"
#file_in = "../Data/Run01/6n0_authors_dedup.txt"
file_in = "../Data/Run01/6n0_authors_dedup.txt"
#file_out = "../Data/TrainingData/TrollsBots/raw/TrollBot_AuthorDetail_ReadyForCleanings.csv"
file_out = "/mydata/node0/LiveData_n0_{}_ReadyForClean.txt"

reddit = praw.Reddit('ClientSecrets')
df_final = pd.DataFrame()

columns = ["link_id", 
               "author", "author_verified", "author_comment_karma",
               "author_link_karma", "num_comments", "created_utc",
               "score",  "body", "downs", 
               "num_reports", "controversiality", 
               "ups"]

global_auth_count = 0
global_row_count = 0
prev_row_count = 0
save_point = 1000
print_point = 100
file_max = 10000
current_file = 1


def get_author_detail(row):
    global df_final
    global global_auth_count
    global file_max
    global current_file
    global global_row_count
    global prev_row_count
    global_auth_count += 1

    #function we will apply to get detail information
    auth_name = row['author']
    httpCount = 0
    count = 0
    while True:
        try:
            if auth_name == "":
                raise UnboundLocalError

            author = reddit.redditor(auth_name)
            count = 0
            df_return = pd.DataFrame()
            # Author Specific
            row['author_verified'] = 'true' if author.has_verified_email else 'false'
            row['author_comment_karma'] = author.comment_karma
            row['author_link_karma'] = author.link_karma

            for comment in author.comments.new(limit=25):
                mod_row = row
                #print(comment.body)
                mod_row['link_id'] = comment.link_id
                mod_row['num_comments'] = comment.num_comments
                mod_row['created_utc'] = comment.created_utc
                mod_row['score'] = comment.score
                mod_row['body'] = comment.body.replace('\\','')
                mod_row['downs'] = comment.downs
                mod_row['num_reports'] = comment.num_reports
                mod_row['controversiality'] = comment.controversiality
                mod_row['ups'] = comment.ups
                mod_row['body'] = comment.body
                mod_row['count'] = count

                #deal with recent comments
                # df_temp adds record after row is built
                # but want to generate it prior to appending the current record
                #prev_comments = df_temp.to_json(orient='records')
                #mod_row['recent_comments'] = prev_comments
                #df_temp = df_temp.append(mod_row, ignore_index=True)
                #df_temp = df_temp[columns]
                #df_temp = df_temp.drop(['recent_comments'], axis=1)                
                #mod_row['recent_comments'] = ''
                df_final = df_final.append(mod_row, ignore_index=True)
                count += 1

        except AttributeError:
            print(f"...Warning: Attribute Error for {auth_name}")
        except UnboundLocalError:
            print(f"...Waring: Participant has no user name")
        except prawcore.exceptions.NotFound as e:
            print(f"...Non 200 response - trying again - {auth_name}")
            time.sleep(1)
            httpCount += 1            
            if httpCount >= 5:
                print("...Breaking From Exception")
                break
            print(f"...Continuing From Exception {httpCount}")
            continue
        
        #break under normal circumstances
        break

    global_row_count += count
    if (global_auth_count % print_point == 0):
        print(f".{auth_name}")
    if (global_auth_count % save_point ==0 and global_auth_count % file_max != 0):
        #Save the file
        print(f"<- Saving at {auth_name} auth_count={global_auth_count} row_count={global_row_count}->")                
        if (global_auth_count == save_point):
            df_final.to_csv(file_out.format(current_file), index=False)
        else:
            df_final[prev_row_count:global_row_count].to_csv(file_out.format(current_file), mode='a', index=False,  header=False)
        prev_row_count = global_row_count
    #files getting to large, going to split up
    if (global_auth_count % file_max == 0):
        print(f"<- Starting new file {current_file} with gc = {global_auth_count}->")
        df_final = df_final[columns]
        df_final.to_csv(file_out.format(current_file), index=False)
        df_final = pd.DataFrame()
        prev_row_count = 0
        global_row_count = 0
        current_file += 1
    return row



def main():
    start = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"Starting at {start}")
    print("Collecting Author and Author Comment Details")
    global df_final
    global columns
    df = pd.read_csv(file_in, index_col=False)
    df = df.drop(df.columns[0], axis=1)
    df.apply(get_author_detail, axis=1)


    df_final = df_final[columns]
    print(df_final)
    df_final.to_csv(file_out.format(current_file), index=False)
    #df_final.to_csv(file_out, index=False)

    end = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"Started at {start} ending at {end}")

if __name__ == "__main__":
    main()
