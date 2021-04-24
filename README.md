## Overview
This project is designed to scrape subreddits and use that data to identify the level of bot interaction in a series of posts. Additionally, it will provide sentiment analysis and a qualitative overview of comments found in the same subset of posts.

## Scraper
The scraper uses two different APIs (reddit api via [PRAW](https://praw.readthedocs.io/en/latest/index.html), and [pushisft.io](https://reddit-api.readthedocs.io/en/latest/#)) to generate two datasets containing information from a sereis of pull requests.  Each pull request collects the top X number of posts within a subreddits over a configured epoch. One dataset contains a list of the authors for each comment, along with the comment depth (which level of the comment tree was it found) and rank (what postition within the level was it found).  The second dateset contains all comments from the top y levels. Both datasets include keys linking them to the appropriate pull request.  

Parameters defining the pulls, as well as global veriables are outlined in config.json files, and examples can be found in .\Scrapper\config.  

Currently Reddit does not provide functionality for searching historical posts.  To counter this we use pushshift.io, which allows historical searches on a limited set of attributes.  Pushshift utilizes a reddit archive, it does not access reddit directly on queries.  Submissions found in the archive are captured close to when they are posted, resulting in inaccurate score and comment counts.  Our approach then is to use pushshift.io to gather a list of all submissions within a subreddit over an epoch, and then collect accurate scores for those submissions from the reddit API. Once the scores are collected the submissions can be sorted in a dataframe and we can create a filtered list of the top x posts from each pull group. This list is then used to query the reddit API and collect the list of commenters and the top Y comments for each submission in the filtered list. 

Both APIs enforce query limits.  This means the major bottleneck is querying the data.  The system could be improved in the future to user iterators, which would be more effecient especially given the lag on the queries.  This could then be fed into the other two tools (undetermined bot identification, comment analyzer) iterativly as well. Biggest bottleneck is at pullin in comment counts because of the reddit query limits.  Each post counts as a query, and the limit is 60 query per minute.  This is built into PRAW.  So thousands of queries can take some time.  Ideally we would track down a better way to either get all counts for a set of posts, or to get accurate counts on historical data from either one of the APIs.  Currently I am unsure how.  Exploration of the APIs could reveal a cleaner approach. 

Example Config

**********confi.json************
{
  "Pulls": [
    {
      "desc":"WSB",
      "name":"WallStreetBets", 
      "timeframe":["01/10/2020", "01/19/2020", "01/26/2020", "01/29/2020", "02/05/2020"]
    },
    {
      "desc": "WSBControl",
      "name": "WallStreetBets",
      "timeframe": ["12/01/2020","12/8/2020"]
    },
    {
      "desc": "Control",
      "name": "YouShouldKnow",
      "timeframe":["01/10/2020", "01/19/2020", "01/26/2020", "01/29/2020", "02/05/2020"]
    }
  ],
  "Globals": {
    "PULL_X_POSTS": 3,
    "COMMENT_LVLS_SCRAPPED":3,
    "SORT_COMMENTS_BY" : "top",
    "POST_LIST_PATH" : "../Data/postList.csv",
    "POST_LIST_PATH_FILTERED" : "../Data/postListFiltered.csv",
    "COMMENT_DATA_PATH" : "../Data/comments.csv",
    "AUTHOR_DATA_PATH" : "../Data/authors.csv",
    "GET_POST_FLDS" : ["id", "created_utc", "full_link"],
    "GET_COMMENT_FLDS" : ["postID", "depth", "depth_rank", "comment"],
    "GET_AUTHOR_FLDS" : ["postID", "depth", "depth_rank", "author"]
  }
}
*********************************

Notes on Config:

Each pull generates a series of comment and author data found in the final datasets.  Data is linked back to the pull through the desc and grouped by day.  The defined timeframe is for analysis, but currently the scrapper only pulls in the frist and last dates in the list.  This means that if there are gaps in the timeframe the data from those gaps will still be present in the final datasets.  

name = subreddit
PULL_X_POSTS: Pull data from the top X posts on a given day from a given subreddit. 
COMMENT_LVLS_SCRAPPED: Number of levels within comment tree to collect comment data from

if you do not send in a config file in the args when you run the scrapper it defaults to ./config/config.json


## praw.ini

In order to access the reddit API you need a client id and secrete.  Details can be found [here](https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example).  Once you have obtained this information you can create '.\Scrapper\praw.ini' and add the following

[ClientSecrets]
client_id=<your ID no quotes>
client_secret=<your secrete no quotes>
user_agent="<your self made user agent (be unique) in qoutes"
