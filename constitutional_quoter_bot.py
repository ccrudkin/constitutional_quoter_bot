# TODO: Make list of ignored users dynamic and expandable via comment replies.
# TODO: Run in multiple subs at once. (Eventually).
# TODO: Avoid attempts to comment on LOCKED posts.

import praw
from datetime import datetime
import re
import json
from time import sleep
import os

cwd = os.getcwd()
files = cwd + '/Files/'
print(files)

with open(files + "private_info.json", "r") as p:  # must create Files/private_info.json and populate with info
    priv = json.load(p)

reddit = praw.Reddit(user_agent=priv["reddit_credentials"]["user_agent"],  # see readme and PRAW docs for more info.
                     client_id=priv["reddit_credentials"]["client_id"],
                     client_secret=priv["reddit_credentials"]["client_secret"],
                     username=priv["reddit_credentials"]["username"],
                     password=priv["reddit_credentials"]["password"])

subreddit = reddit.subreddit('Libertarian')

first = re.compile(r'(\s1st|\sfirst)\s(amendment)', re.I)
second = re.compile(r'(\s2nd|\ssecond)\s(amendment)', re.I)
third = re.compile(r'(\s3rd|\sthird)\s(amendment)', re.I)
fourth = re.compile(r'(\s4th|\sfourth)\s(amendment)', re.I)
fifth = re.compile(r'(\s5th|\sfifth)\s(amendment)', re.I)
sixth = re.compile(r'(\s6th|\ssixth)\s(amendment)', re.I)
seventh = re.compile(r'(\s7th|\sseventh)\s(amendment)', re.I)
eighth = re.compile(r'(\s8th|\seighth)\s(amendment)', re.I)
ninth = re.compile(r'(\s9th|\sninth)\s(amendment)', re.I)
tenth = re.compile(r'(\s10th|\stenth)\s(amendment)', re.I)

regs = [first, second, third, fourth, fifth, sixth, seventh, eighth, ninth, tenth]
am_names = ['first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth']

with open(files + 'bill_of_rights.json', 'r') as f:
    bor = json.load(f)
with open(files + 'ignore.json', 'r') as f:
    ignore = json.load(f)


def print_results():  # for debugging regex results
    for comment in subreddit.stream.comments():
        for r in regs:
            mo = r.search(comment.body)
            if mo:
                print('{} alert from u/{}'.format(mo.group(0), comment.author))
                print(comment.body[:140] + ' ...')  # print first 140 characters of comment
                print('https://www.reddit.com' + comment.permalink)  # this combo creates a live hyperlink
                print('r/{} @ {}'.format(comment.subreddit, datetime.now()))
                print('Submission ID: {}'.format(comment.submission))
                print()


def respond_with_amendments():
    print('Ignore: {}'.format(ignore))
    for comment in subreddit.stream.comments():
        if comment.author not in ignore['users'] and str(comment.submission) not in ignore['submissions']:
            for r in regs:
                mo = r.search(comment.body)
                if mo:
                    am_name = am_names[regs.index(r)]
                    basic_rep = bor['basic_reply'].format(am_name)
                    am_text = 'The {} amendment states: \n\n*{}*'.format(am_name, bor[am_name])
                    full_reply = basic_rep + am_text + bor['bot_info'] + bor['more_bot_info']
                    comment.reply(full_reply)
                    ignore['submissions'].append(str(comment.submission))  # Limits to 1 response per submission.
                    print('Replied to https://www.reddit.com{}\nat {}'.format(comment.permalink, datetime.now()))
                    return 'snoozeplease'
    return 'snoozeplease'
                    # Respond appropriately, check user/sub blacklists, etc. Call other functions for each task!


def loop_replier():
    while True:
        if respond_with_amendments() == 'snoozeplease':
            with open(files + 'ignore.json', 'w') as f:
                json.dump(ignore, f)
            print('Sleeping...\n')
            sleep(60)


# print_results()
loop_replier()
