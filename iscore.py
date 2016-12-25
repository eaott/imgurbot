from bot_utils import *

def getCountBefore(mongo, date):
    mongo.count()
def main():
    imgur = getImgur()
    if imgur.credits['UserRemaining'] < MIN_REQUESTS_PER_HOUR:
        print "Too few credits remain"
        return
    score = -1
    counter = 1
    page = 0
    while score == -1:
        comments = imgur.get_account_comments("RandomSampleForDumps", sort='best', page=page)
        for comment in comments:
            if comment.points <= counter:
                score = counter
                break
            counter = counter + 1
        page = page + 1
    account = imgur.get_account("RandomSampleForDumps")
    mongo = getMongo()
    # In principle, could do something like
    # mongo.find({"comment_date": {"$lt": datetime.datetime(2016, 12, 23, 23, 55, 8)}}).count()
    # to count all the posts before a given time, but we really want all of them
    # for this script.
    autoposts = mongo.count()
    print "%s, %d, %f, %d" % (datetime.datetime.now(), score, account.reputation, autoposts)
main()
