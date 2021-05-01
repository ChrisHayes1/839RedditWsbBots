import pandas as pd

df = pd.read_csv("./raw/TrollBot_AuthorCommentDet.csv")
df_new = df.head(4000)

columns = ["banned_by", "no_follow", "link_id", "gilded",
               "author", "author_verified", "author_comment_karma",
               "author_link_karma", "num_comments", "created_utc",
               "score", "over_18", "body", "downs", "is_submitter",
               "num_reports", "controversiality", "quarantine",
               "ups"]

df_new = df_new[columns]        
df_new.to_csv("./raw/TrollBot_AuthorCommentDet_subset.csv")