from bot_utils import *
def main():
    imgur = getImgur("/Users/Evan/Dropbox/imgur_app.ini")
    if imgur.credits['UserRemaining'] < MIN_REQUESTS_PER_HOUR:
        print "Too few credits remain"
        return
    COUNT = imgur.get_account_comment_count('RandomSampleForDumps')
    mongo = getMongo(host='192.168.0.3', temp_albums='albums_test')
    page = 0
    counter = 0
    repeats = []
    old_counter = -1
    while counter != old_counter:
        old_counter = counter
        print(imgur.credits['UserRemaining'])
        # ordering doesn't matter
        comments = imgur.get_account_comments("RandomSampleForDumps", page=page)
        for comment in comments:
            album_id = comment.image_id
            comment_date = datetime.datetime.utcfromtimestamp(comment.datetime)
            # FIXME this is not accurate, but is annoying to fix in one swoop
            # just subtract off 30 minutes
            # So later, let's write a script to edit the DB a few posts at a time...
            post_date = comment.datetime - 30 * 60

            auto_gen = False
            if comment.comment.startswith("Random sample for this dump: "):
                auto_gen = True
            counter = counter + 1
            data = {
                'album': album_id,
                'post_date': post_date,
                'comment_date': comment_date,
                'auto_gen': auto_gen,
                'fake_post_time': True
            }
            if auto_gen:
                if mongo.find_one({'album':album_id, 'auto_gen': True}):
                    repeats.append(album_id)
            mongo.insert_one(data)

        print("Sleeping after page", page, "with total", counter)
        time.sleep(SLEEP)
        page = page + 1
    for repeat in repeats:
        print repeat
main()


'''
comment count exists

to rebuild the database, will need to use comments/oldest/{page}
> this gives an array of Comment objects which should have:
>>> comment.image_id = 'album'
>>> comment.datetime (as an integer) = 'comment_date'
>>> [image/<comment.image_id>].datetime (as an integer) = 'post_date'
but also need
>>> comment.comment to determine if it starts with the "Random sample for this dump" key
example_schema = {
    'album': item.id,
    'post_date': item.datetime,
    'comment_date': datetime.datetime.utcnow()
}
'''
