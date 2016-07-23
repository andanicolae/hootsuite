* Reddit daemon and web server for Hootsuite challenge *

* Run mongod *
./mongodb_start.sh

* Run Reddit daemon: *
python -m reddit_daemon.daemon

* Run web server: *
python -m web_server.web_server

* Test the web server: *
curl "http://127.0.0.1:5000/items/?subreddit=Scala&from=1.0&to=1500000000.0"
curl "http://127.0.0.1:5000/items/?subreddit=Scala&from=-20&to=5534"
curl "http://127.0.0.1:5000/items/?subreddit=Python&from=1.0&to=1500000000.0&keyword=Python"
curl "http://127.0.0.1:5000/items/?subreddit=Python&from=1.0&to=1500000000.0&keyword=aaaa"

For subreddits, searching in the database is case-sensitive, while for the keyword, searching
in the database is case-insensitive.
Also, for the keyword, matching does not happen on the  whole word 
(i.e. if keyword=class and a submission/comment contains the word "superclass",
then the respective submission/comment is returned).

* Run unittests *
python -m unittest discover -v

* Run Docker composer *
sudo docker-compose up --build

* Check that the containers are up and running *
sudo docker ps -a

* Kill all running containers *
sudo docker rm -f $(sudo docker ps -a -q)
