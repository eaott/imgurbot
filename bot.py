from imgurpython import ImgurClient
import ConfigParser
import random
from pymongo import MongoClient
import datetime
import time

MIN_REQUESTS_PER_HOUR = 10 # starts at ~500 / user
MAX_PAGES_PER_JOB = 45
SLEEP = 5
SHORT_SLEEP = 2
MIN_IMAGE_COUNT = 55
SAMPLE_SIZE = 15

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

def new_to_db(mongo, item):
    # see if this album id is in the albums we've looked at.
    return mongo.find_one({'album':item.id}) is None

def getLastMongoDate(mongo):
    # sorts on "post_date", descending, and gets one value.
    date = mongo.find_one(sort=[("post_date", -1)])
    if date is None:
        return 0
    return date['post_date']

def getNewImgurItems(mongo, imgur, date):
    # Ensuring (up to a point) that we will always go back in time far enough
    # to see things we've visited.
    items = []
    visited = 0
    page = 0
    while visited == 0 and page < MAX_PAGES_PER_JOB:
        if imgur.credits['UserRemaining'] < MIN_REQUESTS_PER_HOUR:
            print "Too few credits remain"
            return items
        orig_items = imgur.gallery(section='user', sort='time', show_viral=True, page=page)

        # Yes, this is slow, and makes this function less singular in purpose,
        # but it's for logging, which is useful for later.
        for item in orig_items:
            if new_to_db(mongo, item):
                if (item.is_album and item.images_count >= MIN_IMAGE_COUNT and
                   not item.nsfw and item.datetime > date):
                    items.append(item)
            else:
                # Yes, we're done if visited > 0, but would like to make sure
                # the order within the gallery call doesn't impact things.
                visited = visited + 1

        if visited == 0 and page != MAX_PAGES_PER_JOB - 1:
            print "sleeping before asking for more posts"
            time.sleep(SHORT_SLEEP)
        page = page + 1
    print "Found %d posts that are in the DB already." % visited
    return items

def post_comment(imgur, item):
    N = item.images_count
    data = random.sample(xrange(11, N + 1), SAMPLE_SIZE)
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

    imgur_items = getNewImgurItems(mongo, imgur, mongo_date)
    for item in imgur_items:
        # sleep for a bit because overwhelming things is bad, also
        # we're not exactly in a hurry here...
        time.sleep(SLEEP)
        posted = post_comment(imgur, item)
        if posted:
            print item.link
            insert_db(mongo, item)
main()
