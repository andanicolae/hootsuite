import json
import sys
import time
import praw
from pymongo import MongoClient, DESCENDING, TEXT
import pymongo
import os.path
from utils.constants import *
from praw.errors import RateLimitExceeded, APIException, HTTPException
from requests import HTTPError
from requests.exceptions import ReadTimeout

# List containing subreddits from input file
input_data = []
# Praw login
r = None
# Dictionary containing for each subreddit, fullname for the oldest submission
# inserted in database
last_submission_fullname = {}
# MongoDB instance
db = None
# Dictionary containing collection instance for each subreddit from input file.
# Each subreddit from input file has its own collection.
collections_dict = {}

def init(input_filename):
    # Check if input file exists
    input_path = os.path.join(INPUT_FOLDER, input_filename)
    if not os.path.isfile(input_path):
        print "File " + str(input_filename) + " does not exist"
        sys.exit(-1)

    # Try to read subreddits from the input file
    try:
        global input_data
        input_data = json.loads(open(input_path).read())
    except ValueError as e:
        print "The following error was encountered while reading input file: " +str(e)
        sys.exit(-1)

    # Connect to Reddit
    global r
    r = praw.Reddit(user_agent="my_reddit_script:v1.0")
    r.login()

    client = MongoClient()

    # Create database
    global db
    db = client[DEFAULT_DATABASE]
    if not db:
        print "Error creating database"
        sys.exit(-1)

    # Drop the collection assigned to each subreddit
    # In case the input file is changed between runs, older collections are not dropped
    for subreddit in input_data:
        db.drop_collection(subreddit)
        collections_dict[subreddit] = db[subreddit]

# Returns a list of maximum MAX_SUBMISSIONS_CHUNK_NO(= 5) submissions corresponding
# to the subreddit.
# 5 has been selected to make debugging easier, 1000 is the maximum limit
def get_submissions_list(r, subreddit):
    # In the docs, I cound not find whether get_subreddit() or get_new() 
    # throws any exception. So, no try /except here

    # Get the submissions older than the last submission stored in
    # last_submission_fullname
    global last_submission_fullname
    submissions = r.get_subreddit(subreddit).get_new(limit = MAX_SUBMISSIONS_CHUNK_NO,
                params={"after" : last_submission_fullname.get(subreddit)})

    submissions_list = []
    try:
        # get_new() returns a generator of submissions, so we convert it
        # to a list

        # if the subreddit does not exist (e.g.: Go, or the 
        # current user has no permission to access it, praw.errors.HTTPException is
        # thrown when trying to convert the submission generator to a list
        submissions_list = list(submissions)
	last_submission_fullname[subreddit] = submissions_list[-1].fullname
        print "subreddit " + str(subreddit) + " fullname " + str(last_submission_fullname[subreddit])
    except (RateLimitExceeded, APIException, HTTPError, HTTPException, ReadTimeout), e:
        print "Exception occurred while getting submissions for " \
                + str(subreddit) + ": " + str(e)
    return submissions_list

def main_loop():

    global r
    init(INPUT_FILE)

    while 1:
        for subreddit in input_data:
            print "Start getting submissions and comments for " + str(subreddit)
            # Each subreddit has its own collection
            coll = collections_dict[subreddit]
 
            submissions_list = get_submissions_list(r, subreddit)
            # Save the fullname of the last submission obtained
            # We need this fullname so that in the next iteration, we get the
            # submissions older than the last submission inserted in the database
            for submission in submissions_list:
                # We create 2 indexes
                # First index is for searching only after timestamps
                coll.create_index([("created_utc", DESCENDING)])
                # Second index is for searching after timestamps and keyword
                coll.create_index([("data", TEXT), ("created_utc", DESCENDING)])
                res = coll.insert_one(
                                           {"created_utc": submission.created_utc, 
                                            "data_id": submission.id,
                                            "data" : submission.title})
                try:
                    flat_comments = praw.helpers.flatten_tree(submission.comments)
                    for comment in flat_comments:
                        if isinstance(comment, praw.objects.MoreComments):
                            continue
                        coll.create_index([("created_utc", DESCENDING)])
                        # Second index is for searching after timestamps and keyword
                        coll.create_index([("data", TEXT), ("created_utc", DESCENDING)])
                        res = coll.insert_one(
                                               {"created_utc": comment.created_utc,
                                                "data_id": comment.id,
                                                "data" : comment.body})
                except (RateLimitExceeded, APIException, HTTPError, HTTPException, ReadTimeout), e:
                    print "Exception occurred while getting comments for " \
                        + str(submission.title) + ": " + str(e)
        # Do not overload Reddit servers with requests
        time.sleep(3)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print "Exiting by user request"
        sys.exit(0)

