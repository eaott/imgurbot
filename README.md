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

## Operational Notes
Primarily for my own use based on my own network setup.

I use a MongoDB instance running on my Raspberry Pi. For a time, it allowed
remote connections through my router so I could check on it remotely. During
the infamous MongoDB hack
(https://www.bleepingcomputer.com/news/security/mongodb-databases-held-for-ransom-by-mysterious-attacker/)
my instance was compromised as well. This removed approximately 1200 entries from
the DB (but they offered to fix it if I only paid them ~$200 worth of bitcoins -- how kind).
Now, although I can SSH remotely into my Pi, the DB will only be visible on my local network.

This also prompted the addition of a new script that hopefully only needs to be run
once, wherein it will back-fill all the data from the DB in the same format.
That's `fix_db_from_hack.py`. It goes through all the comments, finds the auto-generated
ones, adds enough metadata to work with, and fixes the DB. It also produces a list
of album IDs impacted by the hack (ones with 2+ auto-generated comments),
so I can manually delete them (I'd like more control over this part, otherwise
I could automatically do this too).
