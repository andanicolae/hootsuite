import json
from flask import Flask, jsonify, request, abort
from flask_pymongo import PyMongo
from bson import json_util
from utils.constants import *
from utils.http_exception import InvalidUsage


app = Flask(DEFAULT_DATABASE)
if not app:
    print "Error: app failed"
    sys.exit(-1)

mongo = PyMongo(app)
if not mongo:
    print "Error: PyMongo failed"
    sys.exit(-1)

# Code taken from flask documentation
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Check that the mandatory parameters (subreddit, from, to) are present in query
# Check that from and to are valid Unix timestamps
def validate_input(subreddit, min_timestamp, max_timestamp):
    if subreddit is None:
        raise InvalidUsage('Please include "subreddit" parameter in request',
                status_code = 410)

    if min_timestamp is None:
        raise InvalidUsage('Please include from parameter in request',
                status_code = 410)

    if max_timestamp is None:
        raise InvalidUsage('Please include to parameter in request',
                status_code = 410)

    try:
        t1 = float(min_timestamp)
    except ValueError:
        raise InvalidUsage('Please set to parameter value to a valid Unix timestamp',
                status_code = 410)

    try:
        t2 = float(max_timestamp)
    except ValueError:
        raise InvalidUsage('Please set from parameter value to a valid Unix timestamp',
                status_code = 410)

    return (t1, t2)

@app.route('/items/', methods=['GET'])
def get_elems():
    subreddit = request.args.get('subreddit')
    print "subreddit is " + str(subreddit)
    min_timestamp = request.args.get('from')
    print "min_timestamp is " + str(min_timestamp)
    max_timestamp = request.args.get('to')
    print "max_timestamp is " + str(max_timestamp)

    keyword = request.args.get('keyword')

    t1, t2 = validate_input(subreddit, min_timestamp, max_timestamp)

    # Do not show _id field in responses
    if not keyword:
        elems = mongo.db[subreddit].find({"created_utc" : {"$gt" : t1, "$lt" : t2}}, {"_id" : 0}).sort("created_utc", -1)
    else:
        elems = mongo.db[subreddit].find({"created_utc" : {"$gt" : t1, "$lt" : t2}, "$text" : {"$search" : keyword}}, {"_id" : 0}).sort("created_utc", -1)

    # Return the list of elements in json format
    elems_list = [json.dumps(elem, default = json_util.default) for elem in elems]
    return jsonify(elems_list)

if __name__ == '__main__':
    app.run()
