# Import the wordcloud library
import pandas as pd
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
import datetime as dt
from wordcloud import WordCloud, STOPWORDS
import collections
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
stoplist = stopwords.words('english')
stoplist.extend(STOPWORDS)
stoplist.extend(["i'm", "will", "people", "will", "", "think", "go", "The", "it", "know", "really",
                 "time", "use", "got", "want", "it", "even", "make", "one", "i", "still", "see", "back",
                 "still", "see", "detroit", "ta", "going", "see", "need", "back", "gang", "made",
                 "fucking",  "post", "let", "say", "point", "everyone", "deleted", "gonna", "trying"
                 "https", "post", "thing", "say", "sub", "mean", "said", "im", "way", "start", "said",
                 "give", "part", "np", "next", "look", "happen", "night", "anything", "right", "u", "guy",
                 "lol", "job", "first", "good", "fuck", "fucking", "shit"])
print(stoplist)



in_file = "../Data/Run01/4_post_comments.csv"
out_file = '../Data/Run01/8_word_cloud_{}_{}_{}.png'
out_file_plot = '../Data/Run01/8_word_cloud_plot_{}_{}_{}.png'

grp_NAME = 0
grp_START = 1
grp_END = 2
#groupings = ['Control', 'WSB', 'WSBControl']
#groupings_update = [["WSBControl", "12/01/2020", "12/8/2020"],
                    # ["Control",  "01/10/2020", "01/18/2020"],
                    # ["Control", "01/19/2020", "01/25/2020" ],
                    # ["Control", "01/26/2020", "01/28/2020"],
                    # ["Control", "01/29/2020", "02/05/2020"],
                    # ["WSB", "01/10/2020", "01/18/2020"],
                    # ["WSB", "01/19/2020", "01/25/2020"],
                    # ["WSB", "01/26/2020", "01/28/2020"],
                    # ["WSB", "01/29/2020", "02/05/2020"]]

groupings_update = [["WSB", "01/10/2021", "01/18/2021"],
                    ["WSB", "01/19/2021", "01/25/2021"],
                    ["WSB", "01/26/2021", "01/28/2021"],
                    ["WSB", "01/29/2021", "02/05/2021"]]

def build_string(row):
    global long_string
    long_string += str(row['comment']).lower()
    return row

def convert_dates(row):
    try:
        row['utc_date'] = dt.datetime.strptime(str(row['postDate']), '%Y-%m-%d')
    except ValueError:
        row['utc_date'] = None
    return row

print("Reading data")
df = pd.read_csv(in_file)
df = df.apply(convert_dates, axis=1)

for group in groupings_update:
    long_string = ""

    print("Building long_string")
    start_date = dt.datetime.strptime(group[grp_START], '%m/%d/%Y')
    end_date = dt.datetime.strptime(group[grp_END], '%m/%d/%Y')
    #post_date = dt.datetime.strptime(df.loc['postDate'], '%Y-%m-%d')

    df_control = df.loc[(df['reqName'] == group[grp_NAME]) &
                        (df['utc_date'] >= start_date) &
                        (df['utc_date'] <= end_date)]
    df_control.apply(build_string, axis=1)
    print(f"{group} has {len(df_control)}")
    #print(long_string)
    # Create a WordCloud object
    if (long_string):
        wordcloud = WordCloud(stopwords=stoplist, background_color="white", max_words=1000,
                              contour_width=3, contour_color='steelblue')
        # Generate a word cloud
        wordcloud.generate(long_string)
        # Visualize the word cloud
        strt = group[grp_START].replace("/", "_")
        end = group[grp_END].replace("/", "_")
        wordcloud.to_image().save(out_file.format(group[grp_NAME], strt, end))

        #Generate count for each word
        filtered_words = [word for word in long_string.split() if word not in stoplist]
        counted_words = collections.Counter(filtered_words)

        words = []
        counts = []
        for letter, count in counted_words.most_common(10):
            words.append(letter)
            counts.append(count)

        colors = cm.rainbow(np.linspace(0, 1, 10))
        rcParams['figure.figsize'] = 20, 10

        plt.title('Top words in the headlines vs their count')
        plt.xlabel('Count')
        plt.ylabel('Words')
        plt.barh(words, counts, color=colors)
        plt.savefig(out_file_plot.format(group[grp_NAME], strt, end))

#wordcloud.to_file(out_file)

# Join the different processed titles together.
#long_string = ','.join(list(papers['paper_text_processed'].values))
# with open(in_file, "r") as f:
#     for line in f:
#         long_string += line