#/u/GoldenSights
import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import sqlite3
import traceback
 
'''USER CONFIGURATION'''
 
USERNAME  = "checks_for_checks"
#This is the bot's Username. In order to send mail, he must have some amount of Karma.
PASSWORD  = "[REDACTED]"
#This is the bot's Password.
USERAGENT = "/u/Livebeef's /r/theydidthemath checkmark checker"
#This is a short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
SUBREDDIT = "Theydidthemath"
#This is the sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
TITLETAG = "[Request]"
#If this is non-blank, then this string must be in the title or flair of the post to work
TRIGGERS = ["thanks", "thank you", "awesome", "well done"]
TRIGGERS2 = ["&gt; ✓", "&gt;✓"]
#These tell the bot to make the comment
TRIGGERREQUIRED = True
#If this is True, the comment must contain a trigger to post
#If this is False, the comment will be posted as long as there are no anti-triggers
#Anti-triggers will ALWAYS deny the post.
ANTITRIGGERS = ["✓", "but", "wouldn't", "shouldn't", "couldn't", "?"]
#These force the bot not to make the comment.
REPLYSTRING = "If you're satisfied with a user's math answer, don't forget to reply to their comment with a\n\n> ✓\n\n#to award a request point! (Must make a new comment, can't edit into this one. Can't be indented, like the one in this message.) See the sidebar for more info!\n\n^^I ^^am ^^a ^^bot ^^run ^^by ^^/u/Livebeef, ^^please ^^let ^^him ^^know ^^if ^^I'm ^^acting ^^up!"
REPLYSTRING2 = "#Did you mean to award a request point for another user's math? If so, please make a new reply (as in, don't change this one) to their comment with the checkmark unindented (without the '>' or bar in front of it). The indentation keeps the request point from being awarded. \n\n^^I ^^am ^^a ^^bot ^^run ^^by ^^/u/Livebeef, ^^please ^^let ^^him ^^know ^^if ^^I'm ^^acting ^^up!"
#This is the word you want to put in reply
MAXPOSTS = 100
#This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
WAIT = 50
#This is how many seconds you will wait between cycles. The bot is completely inactive during this time.
 
 
'''All done!'''
 
 
 
 
WAITS = str(WAIT)
try:
    import bot #This is a file in my python library which contains my Bot's username and password. I can push code to Git without showing credentials
    USERNAME = bot.uG
    PASSWORD = bot.pG
    USERAGENT = bot.aG
except ImportError:
    pass
 
sql = sqlite3.connect('sql.db')
print('Loaded SQL Database')
cur = sql.cursor()
 
cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
print('Loaded Completed table')
 
sql.commit()
 
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)
 
def scanSub():
    print('Searching '+ SUBREDDIT + '.')
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_comments(limit=MAXPOSTS)
    for post in posts:
        pid = post.fullname
        cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
        if not cur.fetchone():
            if not post.is_root:
                print('Parsing comment ' + pid)
                submission = post.submission
                if not submission.link_flair_text:
                    submission.link_flair_text = ""
                stitle = submission.title.lower()+' '+submission.link_flair_text.lower()
                if TITLETAG == "" or TITLETAG.lower() in stitle:
                    try:
                        pauthor = post.author.name
                        sauthor = submission.author.name
                        if pauthor == sauthor:
                            if TRIGGERREQUIRED ==False or any(trig.lower() in post.body.lower() for trig in TRIGGERS):
                                if not any(atrig.lower() in post.body.lower() for atrig in ANTITRIGGERS):
                                    print('Replying to ' + pauthor + ', comment ' + pid + ', thanked but no RP awarded')
                                    post.reply(REPLYSTRING)
                            elif any(trig.lower() in post.body.lower() for trig in TRIGGERS2):
                                print('Replying to ' + pauthor + ', comment ' + pid + ', failed RP award (indented)')
                                post.reply(REPLYSTRING2)
                    except AttributeError:
                        print('Either commenter or OP is deleted. Skipping.')
 
            cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
            sql.commit()
 
 
while True:
    try:
        scanSub()
    except Exception as e:
        traceback.print_exc()
    print('Running again in ' + WAITS + ' seconds \n')
    sql.commit()
    time.sleep(WAIT)