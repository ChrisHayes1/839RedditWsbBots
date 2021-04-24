###############
# Author: Chris Hayes-Birchler
# Date: 3/25/21
# Some code repurposed from
# https://rareloot.medium.com/using-pushshifts-api-to-extract-reddit-submissions-fb517b286563
# https://github.com/Watchful1/Sketchpad/blob/master/postDownloader.py
###############
# Implementation of pushshift.io wrapper allowing us to search reddit by dates
###############
from math import trunc
from socket import socket

import pandas as pd
import requests
import json
import csv
import time
import datetime
from urllib.parse import urlencode


SEARCH_COMMENTS = "comments"
SEARCH_POSTS = "submission"

class PushShiftIO:
    #def __init__(self):

    def _query_pushshift(self, payload, search_type):
        """Queries pushshift.io API with payload as parameters."""
        url = 'https://api.pushshift.io/reddit/search/' + search_type + '/'
        delim = '?'
        for key, value in payload.items():
            url += delim + key + "=" + str(value)
            delim = '&'
        r = requests.get(url)
        return r.text

    ##########
    # Expectations:  return_fields must include ID and created_utc, and there
    # should be no sort or sort order specified
    #
    # @params start: start date of data draw (inclusive)
    # @params end: end date of data draw (exclusive)
    # @params params:  User defined parameters for query (see pushshift api docs for details)
    # @params return_fields: List of fields user wants returned, should not be included
    #                        in params field
    ##########
    def getAllByDates(self, start, end, params, return_fields):
        """Returns all posts within a timeframe outlined by start and end, and returns
        a dataframe containing return_fields.  Parameters dictate what is queried"""
        current_epoch = start
        total_count = 0

        # Add return fields and end date to pushshift query parameters. End ensures
        # that we do not get queries after end of window, and is exclusive
        params['before'] = end  # Set end of epoch, only return results prior to end
        params['fields'] = ",".join(return_fields)
        if 'size' not in params.keys():
            params['size'] = 100
        if 'created_utc' not in return_fields:
            return_fields.append('created_utc')
        if 'created_utc_time' not in return_fields:
            return_fields.append('created_utc_time')

        # Set up data frame, and list to load into it
        df = pd.DataFrame()
        post_list = []

        # Each pushshift query has a max limit (I think 100 - independent of user set limits)
        # that it can draw, so you can not just give a range and expect to get all results.
        # To counter this we start with 'start' value and track the date created returned
        # in each query and then add 1 to the timestamp.  Expectation is that there is no
        # sort, which means we are given results sorted by timestamp.
        # The loop below handles the iterative query requests until we get no data
        # returned
        count = 0
        while current_epoch < end:

            # Get query results
            params['after'] = current_epoch
            json_text = self._query_pushshift(params, SEARCH_POSTS)
            if json_text == "":
                break

            time.sleep(1)

            try:
                json_data = json.loads(json_text)
            except json.decoder.JSONDecodeError:
                time.sleep(1)
                continue
            except socket.gaierror:
                time.sleep(10)
                continue


            data = json_data['data']

            # Deal with no Data Returned
            if not data:
                break
            total_count += len(data)

            # Get last (newest) post in epoch to track id and utc date
            last_post = data[len(data)-1]
            current_epoch = last_post['created_utc'] + 1

            # Add data to list, which is then appended after while loop
            # Feel like there is an easier way to do this with pandas, but unsure how
            for point in data:
                count += 1
                tempList = []
                for fld in return_fields:
                    if fld == 'created_utc':
                        appendData = datetime.datetime.fromtimestamp(point[fld]).strftime('%Y-%m-%d')
                    elif fld == 'created_utc_time':
                        appendData = datetime.datetime.fromtimestamp(point['created_utc']).strftime('%H:%M:%S')
                    elif fld == 'id':
                        appendData = point[fld]
                        if count % 50 == 0:
                            print(f".{point[fld]}", end="")
                    else:
                        appendData = point[fld]
                    tempList.append(appendData)
                post_list.append(tempList)

            if count % 500 == 0:
                print("", flush=True)


            # If we get less then the requested record size back then we know we hit the
            # end of the epoch, and we can break.
            if len(data) < params['size']:
                break

        # Append any data we collected in the request phase into a dataframe, and return it
        df = df.append(pd.DataFrame(post_list, columns=return_fields), ignore_index=True)
        print(f"Pulled {total_count} posts for post list")
        return df


def main():
    # pushShift = PushShiftIO()
    #
    # #search_flds = "id,score,num_comments,created_utc"
    # search_flds = ['id', 'score', 'created_utc']
    # params = {
    #     'subreddit': 'MealPrepSunday',
    #     'size': 33,
    #     'stickied': "false",
    # }


    pushShift = PushShiftIO()
    start = '01/28/2021'
    end = '01/31/2021'
    start_stamp = trunc(time.mktime(datetime.datetime.strptime(start, "%m/%d/%Y").timetuple()))
    end_stamp = trunc(time.mktime(datetime.datetime.strptime(end, "%m/%d/%Y").timetuple()))

    #search_flds = "id,score,num_comments,created_utc"
    search_flds = ['id', 'score', 'created_utc']
    params = {
        'subreddit': 'MealPrepSunday',
        'size': 33,
        'stickied': "false",
    }

    return_df = pushShift.getAllByDates(start_stamp, end_stamp, params, search_flds)
    return_df.to_csv('../Data/postList.csv')

if __name__ == '__main__':
    main()

