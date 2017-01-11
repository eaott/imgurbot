from bot_utils import *
class tempitem:
    images_count = ""
    id = ""
# hack to ensure that the util code will run on anything.
SMALL_SAMPLE_SIZE = 10
# make the minimum viable object to work with the post_comment code
item = tempitem()
item.id= raw_input("album id: ")
item.images_count = int(raw_input("album size: "))
imgur = getImgur(config_file="/Users/Evan/Dropbox/imgur_app.ini")
post_comment(imgur=imgur, item=item)
