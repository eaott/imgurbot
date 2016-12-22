from bot_utils import *

def main():
    print datetime.datetime.now()
    imgur = getImgur("/Users/Evan/Dropbox/imgur_app.ini")
    print "connected to imgur"
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
    print "i-score is %d" % score
main()
