import os
import sys
import json
import datetime
import time

import praw

from praw.exceptions import APIException

# open config files
if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/config.json"):
    sys.exit("config.json not found")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

# convert environment variables to config values
for key, value in config.items():
    # If the value is a string that starts with "${" and ends with "}"
    if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
        # Get the environment variable name from the value
        env_var_name = value[2:-1]
        # Get the environment variable value
        env_var_value = os.environ.get(env_var_name)
        # If the environment variable exists, update the value
        if env_var_value is not None:
            config[key] = env_var_value

if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/queue.json"):
    sys.exit("queue.json not found")
else:
    with open(f"{os.path.realpath(os.path.dirname(__file__))}/queue.json", "r", encoding="utf-8") as f:
        queue = json.load(f)


class subFunctions():
    def __init__(self):
        # login to reddit
        try:
            self.reddit = praw.Reddit(client_id=config["client_id"],
                                      client_secret=config["client_secret"],
                                      user_agent=config["user_agent"],
                                      username=config["username"],
                                      password=config["password"])
        except Exception as e:
            print(e)
            sys.exit("reddit login failed")

    # update datetime
    now = datetime.datetime.now()

    def submit_post(self, sub, title, text, link, image, video, parent, flairid, flairtext, collectionid, sort, commenttext, post_time, spoiler, nsfw, lock, contest, dontnotify, distinguish, sticky, lockcomment, distinguishcomment, stickycomment, wait):
        current_date = str(self.now.strftime("%m/%d/%Y, %H:%M"))

        if post_time != current_date:
            return 1

        if parent is None:
            try:
                if image is None and video is None:
                    submission = self.reddit.subreddit(sub).submit(title, selftext=text, url=link, flair_id=flairid, flair_text=flairtext, send_replies=not (
                        dontnotify), nsfw=nsfw, spoiler=spoiler, collection_id=collectionid)
                else:
                    if video is None:
                        submission = self.reddit.subreddit(sub).submit_image(title, image_path=image, flair_id=flairid, flair_text=flairtext, send_replies=not (
                            dontnotify), nsfw=nsfw, spoiler=spoiler, collection_id=collectionid)
                    else:
                        submission = self.reddit.subreddit(sub).submit_video(title, video_path=video, thumbnail_path=image, flair_id=flairid,
                                                                             flair_text=flairtext, send_replies=not (dontnotify), nsfw=nsfw, spoiler=spoiler, collection_id=collectionid)

                print(f"Posted {self.to_link(submission.permalink)}")

            except APIException as e:
                if e.field == "ratelimit":
                    if wait == True:
                        msg = e.message.lower()
                        index = msg.find("minute")
                        minutes = int(msg[index - 2]) + 1 if index != -1 else 1
                        print(
                            f"Ratelimit reached. Waiting {str(minutes)} minutes before retrying.")
                        time.sleep(minutes * 60)
                        return 5
            except Exception as e:
                print(f"Error posting submission {str(e)}")

            try:
                if distinguish:
                    submission.mod.distinguish()
                    print("Distinguished")
                if sticky:
                    submission.mod.sticky()
                    print("Stickied")
                if lock:
                    submission.mod.lock()
                    print("Locked")
                if contest:
                    submission.mod.contest_mode()
                    print("Enabled Contest Mode")
                if sort is not None:
                    submission.mod.suggested_sort(sort)
                    print(f"Set suggested sort to {sort}")
            except Exception as e:
                print(
                    f"Error attributing submission. (Are you a moderator?) {str(e)}")
        else:
            submission = self.reddit.comment(parent)
            try:
                submission.body
            except Exception as e:
                submission = self.reddit.submission(parent)

        if commenttext is None:
            return 2

        try:
            comment = submission.reply(commenttext)
            print(f"Commented {self.to_link(comment.permalink)}")
        except Exception as e:
            print(f"Error posting comment {str(e)}")

        try:
            if stickycomment:
                comment.mod.distinguish(how='yes', sticky=True)
                print("Distinguished and Stickied")
            elif distinguishcomment:
                comment.mod.distinguish(how='yes')
                print("Distinguished")
            if lockcomment:
                comment.mod.lock()
                print("Locked")
        except Exception as e:
            print(
                f"Error attributing comment. (Are you a moderator?) {str(e)}")

        return 0

    def to_link(self, permalink):
        return "https://reddit.com" + permalink


if __name__ == "__main__":
    sub_functions_instance = subFunctions()
    while True:
        sub_functions_instance.now = datetime.datetime.now()
        for post in queue["posts"]:
            postspecs = {"sub": None, "title": None, "text": None, "link": None, "image": None, "video": None, "parent": None, "flairid": None, "flairtext": None, "collectionid": None, "sort": None, "commenttext": None, "post_time": None,
                         "spoiler": False, "nsfw": False, "lock": False, "contest": False, "dontnotify": False, "distinguish": False, "sticky": False, "lockcomment": False, "distinguishcomment": False, "stickycomment": False, "wait": False}
            postspecs.update(post)
            if postspecs["link"] != None:
                postspecs["text"] = None
        err = sub_functions_instance.submit_post(sub=postspecs["sub"], title=postspecs["title"], text=postspecs["text"], link=postspecs["link"], image=postspecs["image"], video=postspecs["video"], parent=postspecs["parent"], flairid=postspecs["flairid"], flairtext=postspecs["flairtext"], collectionid=postspecs["collectionid"], sort=postspecs["sort"], commenttext=postspecs["commenttext"],
                                                 post_time=postspecs["post_time"], spoiler=postspecs["spoiler"], nsfw=postspecs["nsfw"], lock=postspecs["lock"], contest=postspecs["contest"], dontnotify=postspecs["dontnotify"], distinguish=postspecs["distinguish"], sticky=postspecs["sticky"], lockcomment=postspecs["lockcomment"], distinguishcomment=postspecs["distinguishcomment"], stickycomment=postspecs["stickycomment"], wait=postspecs["wait"])
        if err == 5:
            sub_functions_instance.submit_post(sub=postspecs["sub"], title=postspecs["title"], text=postspecs["text"], link=postspecs["link"], image=postspecs["image"], video=postspecs["video"], parent=postspecs["parent"], flairid=postspecs["flairid"], flairtext=postspecs["flairtext"], collectionid=postspecs["collectionid"], sort=postspecs["sort"], commenttext=postspecs["commenttext"], post_time=postspecs["post_time"],
                                               spoiler=postspecs["spoiler"], nsfw=postspecs["nsfw"], lock=postspecs["lock"], contest=postspecs["contest"], dontnotify=postspecs["dontnotify"], distinguish=postspecs["distinguish"], sticky=postspecs["sticky"], lockcomment=postspecs["lockcomment"], distinguishcomment=postspecs["distinguishcomment"], stickycomment=postspecs["stickycomment"], wait=postspecs["wait"])
        time.sleep(60)
