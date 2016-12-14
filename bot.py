from imgurpython import ImgurClient
import ConfigParser
import random
from pymongo import MongoClient
import datetime
import time

MIN_REQUESTS_PER_HOUR = 10 # starts at ~500 / user
PAGES_PER_JOB = 25
SLEEP = 5
SHORT_SLEEP = 2

def getImgur():
    config = ConfigParser.RawConfigParser()
    config.read("/home/pi/imgur_app.ini")
    client_id = config.get("client", "id")
    client_secret = config.get("client", "secret")
    user_refresh = config.get("user", "refresh_token")

    # Does not cost an API call
    client = ImgurClient(client_id, client_secret, refresh_token=user_refresh)
    return client

def getMongo():
    client = MongoClient()
    db = client['imgur_db']
    collection = db['imgur_collection']
    albums = collection['albums']
    return albums

def getLastMongoDate(mongo):
    # sorts on "post_date", descending, and gets one value.
    date = mongo.find_one(sort=[("post_date", -1)])
    if date is None:
        return 0
    return date['post_date']

def getImgurItems(imgur, date):
    # FIXME need to find a more elegant method that uses
    # maybe usersub and sorting by time, including paging, ensuring the number
    # of calls isn't too big...
    items = []
    for page in xrange(PAGES_PER_JOB):
        if imgur.credits['UserRemaining'] < MIN_REQUESTS_PER_HOUR:
            print "Too few credits remain"
            return items
        orig_items = imgur.gallery(section='user', sort='time', show_viral=True, page=page)
        items = items + [item for item in orig_items if item.is_album and item.images_count >= 55 and not item.nsfw and item.datetime > date]
        if page != PAGES_PER_JOB - 1:
            print "sleeping before asking for more posts"
            time.sleep(SHORT_SLEEP)
    return items

def post_comment(imgur, item):
    N = item.images_count
    data = random.sample(xrange(11, N + 1), 10)
    data.sort()
    end_comment = " ".join(map(lambda x: "#{0}".format(x), data))
    comment = "Random sample for this dump: " + end_comment
    if imgur.credits['UserRemaining'] >= MIN_REQUESTS_PER_HOUR + 4:
        for attempt in range(4):
            response = imgur.gallery_comment(item.id, comment)
            if response is not None:
                print response, response['id'] is not None
            if response is not None and response['id'] is not None:
                print "posted %s, now sleeping to help with spam" % item.id
                time.sleep(SLEEP)
                print "upvoting %s to help it along" % item.id
                imgur.gallery_item_vote(item.id)
                time.sleep(SLEEP)
                return True
            if attempt != 3:
                print "Failed response - trying again for %s " % item.id
                time.sleep(SLEEP)
        print "Could not get a successful response when posting comment %s" % item.id
        return False
    print "Too few credits remain for comment"
    return False

def insert_db(mongo, item):
    # FIXME need to be a little more careful here and thoughtful about what
    # might be needed
    example_schema = {
        'album': item.id,
        'post_date': item.datetime,
        'comment_date': datetime.datetime.utcnow()
    }
    mongo.insert_one(example_schema)

def new_to_db(mongo, item):
    # see if this album id is in the albums we've looked at.
    return mongo.find_one({'album':item.id}) is None

'''
At interval that works for API calls...

> Open DB
> find the post_date of the last post in DB
> ask imgur API for posts after that date, hopefully for albums only
> for each post:
>>> post a comment to imgur
>>> add the metadata about the post to the DB
'''
def main():
    mongo = getMongo()
    print "connected to mongo"
    mongo_date = getLastMongoDate(mongo)
    imgur = getImgur()
    if imgur is None:
        return
    print "connected to imgur"

    imgur_items = getImgurItems(imgur, mongo_date)
    for item in imgur_items:
        # sleep for a bit because overwhelming things is bad
        time.sleep(SLEEP)
        if new_to_db(mongo, item):
            posted = post_comment(imgur, item)
            if posted:
                print item.link
                insert_db(mongo, item)
main()
