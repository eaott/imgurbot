from bot_utils import *
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
    print datetime.datetime.now()
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
