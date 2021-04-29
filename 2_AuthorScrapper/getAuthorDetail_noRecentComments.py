import pandas as pd
import praw
import prawcore
import time
import datetime
# Pull from const path = `https://www.reddit.com/user/${profile.name}/comments.json?limit=25`
# to get JSON user comment data

CORE_LINK = "https://www.reddit.com/user/{}/comments.json?limit=25"
file_in = "../Data/Run00/6_authors_dedup.csv"
file_out = "/mydata/node0/7g1_run00_{}_author_comments_and_attr.csv"

reddit = praw.Reddit('ClientSecrets')
df_final = pd.DataFrame()

columns = ["banned_by", "no_follow", "link_id", "gilded",
               "author", "author_verified", "author_comment_karma",
               "author_link_karma", "num_comments", "created_utc",
               "score", "over_18", "body", "downs", "is_submitter",
               "num_reports", "controversiality", "quarantine",
               "ups"]

global_count = 0
prev_count = 0
save_point = 250
print_point = 100
file_max = 10000
current_file = 1

def get_author_detail(row):
    global df_final
    global global_count
    global file_max
    global current_file
    global_count += 1

    #function we will apply to get detail information
    auth_name = row['author']
    httpCount = 0
    while True:
        try:
            if auth_name == "":
                raise UnboundLocalError
            #Should probably put this in try block
            author = reddit.redditor(auth_name)


            #print(f"Author {auth_name} has {author.comment_karma} karma")
            count = 0
            df_return = pd.DataFrame()
            row['author_verified'] = 'true' if author.verified else 'false'
            row['author_comment_karma'] = author.comment_karma
            row['author_link_karma'] = author.link_karma
            #df_temp = pd.DataFrame()

            for comment in author.comments.new(limit=25):
                mod_row = row
                #print(comment.body)
                mod_row['banned_by'] = comment.banned_by
                mod_row['no_follow'] = 'true' if comment.no_follow else 'false'
                mod_row['link_id'] = comment.link_id
                mod_row['gilded'] = comment.gilded
                mod_row['num_comments'] = comment.num_comments
                mod_row['created_utc'] = comment.created_utc
                mod_row['score'] = comment.score
                mod_row['over_18'] = 'true' if comment.over_18 else 'false'
                mod_row['body'] = comment.body
                mod_row['downs'] = comment.downs
                mod_row['is_submitter'] = 'true' if comment.is_submitter else 'false'
                mod_row['num_reports'] = comment.num_reports
                mod_row['controversiality'] = comment.controversiality
                mod_row['quarantine'] = 'true' if comment.quarantine else 'false'
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

    if (global_count % print_point == 0):
        print(f".{auth_name}")
    if (global_count % save_point ==0):
        #Save the file
        print(f"<- Saving at {auth_name} count={global_count}->")
        prev_count = global_count
        if (global_count == save_point):
            df_final.to_csv(file_out.format(current_file), index=False)
        else:
            df_final.to_csv(file_out.format(current_file), mode='a', index=False,  header=False)
    #files getting to large, going to split up
    if (global_count% file_max == 0):
        print(f"<- Starting new file {current_file} with gc = {global_count}->")
        df_final.to_csv(file_out.format(current_file), mode='a', index=False,  header=False)
        df_final = pd.DataFrame()
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

    #csvs for training data has feilds as
    #df_final['author_verified'] = "true" if df_final['author_verified'] == 1 else "false"
    # df_final['over_18'] = df_final['over_18'].map(lambda x: 'true' if x else 'false')
    # df_final['is_submitter'] = df_final['is_submitter'].map({1: 'true', 0: 'false'})
    # df_final['quarantine'] = df_final['quarantine'].map({1: 'true', 0: 'false'}).fillna('false')


    df_final = df_final[columns]
    print(df_final)
    df_final.to_csv(file_out.format(current_file), index=False)
    #df_final.to_csv(file_out, index=False)

    end = datetime.datetime.now().strftime('%H:%M:%S')
    print(f"Started at {start} ending at {end}")

if __name__ == "__main__":
    main()
