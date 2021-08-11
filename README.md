# 2017-group-2

**Project Title: Footsie**

Group Number: 2

Member 1: Joshan Bajaj - jbajaj1

Member 2: Achintya Gopal - agopal2

Member 3: Riley Scott - rscott39

Member 4: Paul Watson - pwatso14

Member 5: William Watson - wwatso13

## Directory Structure

~~~~
2017-group-2/
├─ docs/ - Documentation
|   ├─ Backend/ - Shows Database Schema
|   ├─ Frontend/
|   |   ├─ Design/ - UML, Domain Analysis
|   |   ├─ Sketches/
|   |   └─ UIView/
|   └─ Tests/ - Defines test cases and shows test coverage
|
├─ grades/
|
├─ prototype/ - Old Prototype Of Views
|
├─ src/
|   ├─ Analytics/ - Contains files for running analytics and training on tables
|   ├─ Backend/
|   |   ├─ app/
|   |   |   ├─ models/
|   |   |   └─ views/
|   |   |   |   └─ helperFunctions/
|   |   |   |   |   └─ preprocess/
|   |   |   |   |   └─ scorer/
|   |   |   |   |   └─ combiner/
|   |   └─ migrations/
|   └─ Footsie/ - Frontend Code
|       └─ src/
|           ├─ assets/
|           ├─ models/
|           └─ views/
|
└─ tests/ - Contains tests and setup demo script
    └─ helperFunctions/
~~~~


## **Build Instructions**

Assumptions: 
* Mac for homebrew (`brew`)
* `pip` for `python2.7` (Note, run `pip install --upgrade pip`) 
* XCode

### Deployment Methodology (For Debian)

Our CS server is "footsie.cs.jhu.edu"

`sudo apt-get install git htop postgresql postgresql-client pip python-pip`

`sudo pip2 install -r requirements.txt `

This command "logs in" as postgres user

`sudo -u postgres bash`

As postgres user:

`echo "create database footsie;" | psql `

`createuser pwatso14`

`createdb -O pwatso14 footsie`

As regular user:
Changed /etc/postgresql/X.Y/main/pg_hba.conf from `trust` to `all`

`/etc/init.d/postgresql reload`

`python init_db.py`

`sudo python run.py`

Note: We use pwatso14 because that is the user that we were given for the CS server

### Installs (For Mac):

`brew install node`

`brew install watchman`

`brew install postgres`

`sudo pip install -r requirements.txt`

*NOTE:* If you receive an error declaring that there is an existing installation (for example, `Found existing installation: six 1.4.1`), then rerun `sudo pip install -r requirements.txt` with an added `--ignore-installed <package>` (For example, `sudo pip install -r requirements.txt —ignore-installed six`)

### Create the database

`postgres -D /usr/local/var/postgres`

The postgres database needs to run in the backgorund.

``createdb `whoami` ``

`echo "create database footsie;" | psql `

This creates a postgres database called footsie

### This runs the server:

`cd src/Backend`

`CONFIG=testing python init_db.py`

`CONFIG=testing python run.py`

The CONFIG=testing is to use the local database

### For the frontend:

`npm install -g react-native-cli`

This installs the react-native command line interface: https://facebook.github.io/react-native/docs/understanding-cli.html

### Facebook SDK

1. Download the Facebook SDK by going to https://origincache.facebook.com/developers/resources/?id=facebook-ios-sdk-current.zip which should automatically start downloading the zip file


2. Move it to Documents, unzip it, and rename it to `FacebookSDK`

3. Go to the `src/Footsie/` directory and run `npm install` to install the react-native modules. It will put the modules in `src/Footsie/node_modules/`

4. Go to `src/Footsie/ios` and open Footsie.xcodeproj in Finder. Run it in Xcode.


If building on Xcode fails because it couldn't build the frameworks/modules, then these instructions may help:
  1. create a new project by running `react-native init Test` from the command line
  2. `cd` to `Test`, and `cat package.json`
  3. Copy the versions that are mentioned in `package.json` of `Test` into the `package.json` of `Footsie`
  4. Use `npm install` in `srs/Footsie` again

If the above still doesn't work, then follow these steps

  1. Clean Project in Xcode by typing Shift+Command+K
  2. Run the Test project by opening Test/ios/Test.xcodeproj in Finder.
  3. Once the Test project app is running in the simulator, keep it running and then run Footsie as well
  4. If Footsie is running in the simulator and you get a red screen, stop running Test and stop and close the react-native terminal
  5. Stop the Footsie app and run it again. Tada!


*NOTE:* Change the IP address of the server in `SocketModel.js` to connect to the backend. Heruko is currently having trouble handling more than one SocketIO connection, so for testing purposes we have been using local host but using the heroku database (To do this, change the url in SocketModel.js to http://localhost:5000/).


We used the following for our random chat names:
https://github.com/concentricsky/python-randomnames

### Logging in ###
To log in through facebook, we need to give you permission on our side since the app is still in development mode. To do this, send us either your Facebook name or your Facebook ID.


*NOTE:* To test this app effectively, use a second device with the app running on it so two users can interact. You will also need two Facebook accounts.

## **Testing**

Testing is done by navigating to the `tests` folder and running the following commands to run the tests and see the coverage report:  

`CONFIG=testing py.test --cov=../src/Backend/app/views/ ./`

CONFIG=testing is to run the tests locally

#### Test Coverage
![alt text](https://github.com/jhu-oose/2017-group-2/blob/master/docs/Tests/testCoverage.png "Test Coverage")


## **Complex Algorithms**

### Graph Algorithm

Allow users to modify the “radius” at which they can discover others as well as shortening or extending the time in which another user is considered viable to connect with.

#### Radius

Allow users to set the radius of discovery (up to 4 people away)

When users discover other users through bluetooth, the information is stored in the backend in a table. This information implicitly creates a graph with users as points in the graph.

When users are looking for others to connect with, the algorithm looks up all people that are r distance away in the graph. It also checks that the person discovered by the algorithm also wants to be found by people within that radius of people-hops. 

The lookup scheme is a breadth first search on the graph while checking certain conditions on the users found.

#### Time

Instead of being able to connect with other users who were near 1 hour ago, users can set it to any time (up to 24 hours), and as with the radius rules, both users have to agree that they were near each other given the time defined (if User A defines a time t1 and User B defines time t2 (t1 < t2), then for user B to message user A, they must have been near each other within the last t1 time).

The data will be removed from the database after 24 hours. The data is kept for that long instead of the time specified by the user in case they later decide to increase the time variable. 

#### Optimizations

The queries are computationally intensive because of the many lookup queries necessary, and so when a valid conncetion edge is found, it is stored in the user's session. It is automatically removed once the edge is no longer considered valid, with the cached edges giving a extra five minute grace period before being considered invalid.

Users can set the maximum amount of users they want returned from the graph with a max of 100 and default of 25, and once the correct number is found, the query is ended. If the user's session contains enough valid connecions, no query to the graph will happen.

### Tags

Allow users to set their own tags

Users can evaluate who they want to chat with by reviewing the other user's interest tags, or they can set their own interests so that our matching algorithm can sort users for them to talk to based on common interest.

#### Sorting by Tags

To sort by tags, we had to write a few algorithms that can compare the tags of two users. We have a set of preprocessing algorithms we perform spell checking on the tags, splits the tags into words, and removes stopwords. Once this is done, two set of tags are compared using algorithms such as fuzzy wuzzy (levenshtein distance) or exact matching. Then the score is calculated influenced by the Jaccard Index or Dice's Coefficient.

### Machine Learning

#### Logging 

Even though we do not have too much data to actually do Machine Learning, we realized there is a lot of infrastructure needed to collect data to apply machine learning algorithms.

To collect the data from the front end, when users view a set of people in the discover view, a session id is given for the set of people. This session id is passed by the front end to do the backend for logging; the information logged is the people the user clicks on as well as who the user sent a request to.

#### Feature Vectors

Along with the data, the feature vectors are stored in the back end. When the list of nearby users is retrieved from the backend, these users are sorted according to a set of feature vectors. The feature vectors are populated using a set of scorers (the scorers use the hops away a user is, the tags, etc). Once a feature vector is populated, combiners are used to calculate a score given the feature vectors. The list of users are then sorted by the scores. 

Given the data that is logged in the backend, we wrote a file Metrics.py in Analytics/ that calculates statistics about user behavior such as the number of clicks, the number of requests sent, the number of clicks that did not lead to a request, the average position of users who a request was sent to, etc.

We also wrote a machine learning file Training.py in Analytics/ that joins the Logging tables and the Feature Vectors table to create training data. We use PyTorch to train the model. Once the model is trained, the model is saved with 'pickle' in list format. Then, we wrote a combiner that loads in the saved model to calculate the scores of feature vectors.

## **Project Iterations**

[Project Iteration 1](https://github.com/jhu-oose/2017-group-2/wiki/Project-Iteration-1 "Project Iteration 1 Page")

[Project Iteration 2](https://github.com/jhu-oose/2017-group-2/wiki/Project-Iteration-2 "Project Iteration 2 Page")

[Project Iteration 3](https://github.com/jhu-oose/2017-group-2/wiki/Project-Iteration-3 "Project Iteration 3 Page")

[Project Iteration 4](https://github.com/jhu-oose/2017-group-2/wiki/Project-Iteration-4 "Project Iteration 4 Page")

[Project Iteration 5](https://github.com/jhu-oose/2017-group-2/wiki/Project-Iteration-5 "Project Iteration 5 Page")

[Project Iteration 6](https://github.com/jhu-oose/2017-group-2/wiki/Project-Iteration-6 "Project Iteration 6 Page")
