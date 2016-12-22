# imgurbot
Simple bot to run on imgur that powers RandomSampleForDumps.

Every half-hour, my Raspberry Pi executes this Python script (`bot.py`). The bot:
* Connects to imgur and a MongoDB server (also running on the Pi)
* Uses the DB to find when the last auto-generated comment was made (could be done with imgur API calls, but those are rate-limited, so it's easier to do it this way)
* Finds new content in usersub and identifies SFW albums with 55+ images (cutoff subject to change)
* Posts an auto-generated sample from {11, ..., N} as a comment on the album (sorted for convenience, also to maintain any "trends" in the album -- maybe a section from Twitter, then some confession bears, etc.)
* Upvotes the album (partially self-serving, also just to be nice to the OP)
* Saves album ID and timestamps to database for next time

## "i-score"
This is another example of what can be done with the imgur API. This computes
the "i-score", the imgur equivalent of the h-score in academia. This is the
largest value `H` where `H` comments have `H` points or more.
