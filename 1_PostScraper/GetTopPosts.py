###############
# Author: Chris Hayes-Birchler
# Date: 3/25/21
# Some code repurposed from https://github.com/iam-abbas/Reddit-Stock-Trends
###############
import sys
from copy import copy
from json.decoder import NaN
from math import trunc
import time
from pushShiftIO import PushShiftIO
import json
import pprint
import pandas as pd
import praw
import prawcore
import datetime


########
# during each timeframe (varies by project - control week, control sub, wsb)
# a) Goal -  identify bots posing as users in top posts
# b) Goal - Analyze comments in tops posts for themes and sentiment
# Timeframes:  WSB & control sub 1/10-1/19, 1/20-1/26, 1/27-1/28, 1/29-2/4
#             WSB control timeframe: 12/1-12/7
# Data Collection
#   X = 10 # Variable config option
#   a) Collect top X posts on each day in timeframe
#   b) For each post
#       i) Qualitative - Examine all first level comments
#           - Additionally we could pull all comments from Y% to first level comments
#           Y could be top Y percent, or random Y percent
#       ii) Quantitative - ID all unique users from top X posts
#           Pull in data from user accounts necessary for ML alg
#               -> Last 20 responses, karma, response volume and accountverification
#               -> awardee_karma, awarder_karma, comment_karma, link_karma, created,
#                  has_verified_email, is_mod, name, total_karma, verified
#
#               -> Maybe also number of comments per post? Age of account?
#                  quarantine, restrict_commenting, restrict_posting, user_is_banned
#                   user_is_muted, user_is_subscriber, user_is_muted
#           Might be interesting (now or follow up) to identify how much karma
#           comments got in post and how much visibility
########


class Scraper:
    def __init__(self, config):

        with open(config) as json_file:
            self.requests = json.load(json_file)

        self.pull_x_posts = self.requests['Globals']['PULL_X_POSTS']
        self.comment_lvls_scrapped = self.requests['Globals']['COMMENT_LVLS_SCRAPPED']
        self.sort_comments_by = self.requests['Globals']['SORT_COMMENTS_BY']
        # Pathways
        self.author_data_path = self.requests['Globals']['AUTHOR_DATA_PATH']
        self.comment_data_path = self.requests['Globals']['COMMENT_DATA_PATH']
        self.post_list_path = self.requests['Globals']['POST_LIST_PATH']
        self.post_list_score_build = self.requests['Globals']['POST_LIST_PATH_BUILD']
        self.post_list_path_filtered = self.requests['Globals']['POST_LIST_PATH_FILTERED']
        # Fields for different pulls
        self.get_post_flds = self.requests['Globals']['GET_POST_FLDS']
        self.get_comment_flds = self.requests['Globals']['GET_COMMENT_FLDS']
        self.get_author_flds = self.requests['Globals']['GET_AUTHOR_FLDS']


    ###########
    # Uses pushShift.io to pull in all posts from a given date range provided by pulls
    # in config file
    ###########
    def get_post_list(self):
        """Get full post list based on config file"""
        print("\n---------\nGetting post list\n---------\n")
        pushShift = PushShiftIO()
        final_df = pd.DataFrame()
        for pull in self.requests['Pulls']:
            # Need to create master list of [pull.desc, id, utc_created]
            print(f"Running {pull['desc']}")
            start_time = pull['timeframe'][0]
            end_time = pull['timeframe'][-1]
            print(f"start_time = {start_time} and end_time = {end_time}")
            start_stamp = trunc(time.mktime(datetime.datetime.strptime(start_time, "%m/%d/%Y").timetuple()))
            end_stamp = trunc(time.mktime(datetime.datetime.strptime(end_time, "%m/%d/%Y").timetuple()))

            # search_flds = "id,score,num_comments,created_utc"
            search_flds = self.get_post_flds  # ["id", "created_utc"]
            params = {
                'subreddit': pull['name']
            }

            # save_flds = [pull['desc'], search_flds]
            return_order = copy(search_flds)
            return_df = pushShift.getAllByDates(start_stamp, end_stamp, params, return_order)
            return_df['reqName'] = pull['desc']
            return_order.insert(0, 'reqName')
            return_df = return_df[return_order]
            # print(return_df)
            final_df = final_df.append(return_df, ignore_index=True)

        final_df.to_csv(self.post_list_path, index=False)

    ###########
    # push.io does not have accurate score counts, so we need to build up the dataset
    # to include comment count and score from PRAW and add to the csv
    ###########
    def get_post_scores(self):
        """filters results to only the top x posts from get_post_list"""
        print(f"\n---------\nSorting post data at {datetime.datetime.now().strftime('%H:%M:%S')}\n---------\n")
        # Need to iterate over post list and build detail csvs
        df_post_list = pd.read_csv(self.post_list_path)
        # Loop through post list and get counts
        df_post_list['comment_count'] = None
        df_post_list['score'] = None

        reddit = praw.Reddit('ClientSecrets')

        print(f"...Pulling in comment counts at {datetime.datetime.now().strftime('%H:%M:%S')}")
        for r in range(0, len(df_post_list.index)):
            savePoint = 2500
            post_id = df_post_list.iloc[r]['id']
            if (r+1) % 10 == 0:
                print(f".{post_id}", end="")
            if (r+1) % 100 == 0:
                print("", flush=True)
            if (r+1) % savePoint == 0:
                if (r+1) == savePoint:
                    df_post_list[(r+1-savePoint):r].to_csv(self.post_list_score_build, index=False)
                else:
                    df_post_list[(r-savePoint):r].to_csv(self.post_list_score_build, mode='a', header=False, index=False)
                print(f"\n--File Saved ({(r+1)})--\n")
            # Loop through post list and
            # score, comment_count = self._get_post_list_details(df_post_list.iloc[r]['id'])
            httpCount = 0

            while True:
                try:
                    #print(f"Getting submission({post_id})\n")
                    submission = reddit.submission(post_id)
                    score = submission.score
                    comment_count = submission.num_comments
                    df_post_list.at[r, 'comment_count'] = comment_count
                    df_post_list.at[r, 'score'] = score
                    break
                except prawcore.exceptions.NotFound as e:
                    print(f"Non 200 response - trying again - {post_id}")
                    time.sleep(1)
                    httpCount += 1
                    if httpCount == 5:
                        break
                except Exception as e:
                    x, y = e.args
                    print(f"Unexpected error: {x} : {y} : \n Trying again")
                    df_post_list.to_csv(self.post_list_path_build, index=False)
                    raise


        # Save updated post list with comment count and score
        print(f"...Sorting posts at {datetime.datetime.now().strftime('%H:%M:%S')}")
        #df_post_list = df_post_list.sort_values(by=['reqName', 'created_utc', 'score'], ascending=False)
        df_post_list.to_csv(self.post_list_score_build, index=False)



    ###########
    # Filter post data down to top X submissions
    ###########
    def filter_post_data(self):
        # Filter to top X posts by score and save filtered list
        print(f"\n---------\nFiltering post data at {datetime.datetime.now().strftime('%H:%M:%S')}\n---------\n")
        df_post_list = pd.read_csv(self.post_list_score_build)


        current_group = ""
        current_date = ""
        count = 1
        columns = df_post_list.columns
        df_post_list_filter = pd.DataFrame(columns=columns)
        for r in range(0, len(df_post_list.index)):
            reqName = df_post_list.iloc[r]['reqName']
            created_utc = df_post_list.iloc[r]['created_utc']

            if current_group != reqName or current_date != created_utc:
                count = 1
                current_date = created_utc
                current_group = reqName

#            if current_group == reqName or current_date == created_utc:
            if count <= self.pull_x_posts:
                temp = df_post_list.iloc[r]
                df_post_list_filter = df_post_list_filter.append(temp, ignore_index=True)
                count += 1



        df_post_list_filter.to_csv(self.post_list_path_filtered, index=False)
    ###########
    # For a given post ID, pull in comment and author details, returns two
    # pandas dataframes, one for comments and one for authors
    ###########
    def _get_post_data(self, post_id):
        # Scrape reddit for desired posts
        # auth_column_names = ["postID", "depth", "depth_rank", "author"]
        # comment_column_names = ["postID", "depth", "depth_rank", "comment"]

        auth_column_names = self.get_author_flds
        comment_column_names = self.get_comment_flds

        # Build DF for comment authors
        df_auths = pd.DataFrame()
        # Build DF to collect comments
        df_comments = pd.DataFrame()

        # Begin scraping comments and commenter's
        reddit = praw.Reddit('ClientSecrets')
        submission = reddit.submission(post_id)

        try:
            subCreated = datetime.datetime.fromtimestamp(submission.created_utc)
            # Comments
            # Need to build two datasets from comments
            # a) A list of all commenters
            author_list = []
            # b) A list of all x lvl comments, id of author
            comments_list = []

            # Began parsing
            submission.comment_sort = self.sort_comments_by
            submission.comments.replace_more(limit=None)

            # Prime queue and get ready to parse comments
            comment_queue = submission.comments[:]  # Seed with top-level
            level = 0
            count = 0
            # Itterate through comments
            while comment_queue:
                if (count % 100) == 0:
                    print(",", end="")
                if (count % 1000) == 0:
                    print("")
                if count == 0:
                    count = len(comment_queue)
                    start = count
                    level += 1
                comment = comment_queue.pop(0)
                # Add to list of comments
                if level <= self.comment_lvls_scrapped:
                    comments_list.append([submission.id, level, start - count + 1, comment.body])
                # Add author to larger list
                author_list.append([submission.id, level, start - count + 1, comment.author])
                count -= 1
                comment_queue.extend(comment.replies)
        except prawcore.exceptions.NotFound as e:
            return df_auths, df_comments


        # Append submission comments to dataframe
        df_auths = df_auths.append(pd.DataFrame(author_list, columns=auth_column_names))
        df_comments = df_comments.append(pd.DataFrame(comments_list, columns=comment_column_names))

        # Save to CSV

        return df_auths, df_comments

    ###########
    # Loops through the filtered posts returned from pushshift.IO and iterates
    # through them, calling _get_post_data on each post in list, and then appending
    # the results to the final lists
    ###########
    def get_post_details(self):
        print(f"---------\nGetting post contributors and comments at at {datetime.datetime.now().strftime('%H:%M:%S')} \n---------\n")
        auth_column_names = self.get_author_flds
        comment_column_names = self.get_comment_flds

        df_final_auths = pd.DataFrame()
        df_final_comments = pd.DataFrame()

        # Need to iterate over post list and build detail csvs
        df_post_list = pd.read_csv(self.post_list_path_filtered)
        save_point = 10
        auth_count = 0
        comment_count = 0
        prevauth_count = 0
        prev_commentCount = 0

        for r in range(0, len(df_post_list.index) - 1):

            # print(f"Running id = {df_post_list.iloc[r]['id']}")
            df_auths, df_comments = self._get_post_data(df_post_list.iloc[r]['id'])
            auth_count += len(df_auths.index)
            comment_count += len(df_comments.index)

            print(f"{df_post_list.iloc[r]['id']}")
            if df_auths.empty and df_comments.empty:
                print("No authors and comments returned")
            else:
                # add post details
                df_auths['reqName'] = df_post_list.iloc[r]['reqName']
                df_auths['postDate'] = df_post_list.iloc[r]['created_utc']
                df_comments['reqName'] = df_post_list.iloc[r]['reqName']
                df_comments['postDate'] = df_post_list.iloc[r]['created_utc']
                # print("df_auths = \n",  df_auths)
                # print("df_comments = \n", df_comments)
                # append to full list
                df_final_auths = df_final_auths.append(df_auths, ignore_index=True)
                df_final_comments = df_final_comments.append(df_comments, ignore_index=True)

            if (r+1) % save_point == 0:
                if (r+1) == save_point:
                    df_final_auths[0:auth_count].to_csv(self.author_data_path, index=False)
                    df_final_comments[0:comment_count].to_csv(self.comment_data_path, index=False)
                else:
                    df_final_auths[prevauth_count:auth_count].to_csv(self.author_data_path, mode='a', header=False, index=False)
                    df_final_comments[prev_commentCount:comment_count].to_csv(self.comment_data_path, mode='a', header=False, index=False)
                print(f"\n--File Saved ({(r+1)})--\n")
                prevauth_count = auth_count
                prev_commentCount = comment_count

        # Output author details to csv
        print("\n----------------\n")
        return_auth_order = auth_column_names
        return_auth_order.insert(0, 'reqName')
        return_auth_order.insert(1, 'postDate')
        df_final_auths = df_final_auths[return_auth_order]
        df_final_auths.to_csv(self.author_data_path)

        # Output comment details to csv
        return_comment_order = comment_column_names
        return_comment_order.insert(0, 'reqName')
        return_comment_order.insert(1, 'postDate')
        df_final_comments = df_final_comments[return_comment_order]
        df_final_comments.to_csv(self.comment_data_path)


###########
# Sort a list by values
###########
def sort_list(path, sort_list):
    df_list = pd.read_csv(path)
    df_list = df_list.sort_values(by=sort_list, ascending=False)
    df_list.to_csv(path, index=False)


def main():
    print(f"Starting at {datetime.datetime.now().strftime('%H:%M:%S')}")
    config = './config/config.json'
    if len(sys.argv) == 2:
        config = sys.argv[1]
    scraper = Scraper(config)

    # Get list of all posts within config groupings
    #scraper.get_post_list()

    # Get scores for all posts within config groupings
    #scraper.get_post_scores()

    # Sort list by grouping then score
    #sort_list(scraper.post_list_path_build, ['reqName', 'created_utc', 'score'])

    # Filter full scored list into top x posts in each group\time point
    #scraper.filter_post_data()

    # Get all authors and top y comments
    scraper.get_post_details()
    print(f"\n\nFinished at {datetime.datetime.now().strftime('%H:%M:%S')}")


if __name__ == '__main__':
    main()

