import unittest
import reddit_daemon.daemon as daemon
import praw

class DaemonTest(unittest.TestCase):

    def test_non_existing_input_file(self):
        self.assertRaises(SystemExit, daemon.init, "non_existing_file.json")

    def test_input_file_not_in_json_format(self):
        self.assertRaises(SystemExit, daemon.init, "../reddit_daemon/daemon.py")

#    def test_json(self):
#    	r = praw.Reddit(user_agent="my_reddit_script:v1.0")
#    	r.login()
#        self.assertRaises(praw.errors.HTTPException, daemon.get_submissions_list, r, "Go")
