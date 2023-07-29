import datetime
import time
import sys
import os
import json
import praw

from praw.exceptions import APIException


def open_file(file):
    if not os.path.isfile(f"{os.path.realpath(os.path.dirname(__file__))}/{file}"):
        sys.exit(f"{file} not found")
    else:
        with open(f"{os.path.realpath(os.path.dirname(__file__))}/{file}", "r", encoding="utf-8") as f:
            return json.load(f)


def convert_env_var(config):
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


def to_link(permalink):
    return "https://reddit.com" + permalink


class RedditFunc():
    def __init__(self):
        # open config file and convert environment variables to config values
        config = open_file("config.json")
        convert_env_var(config)

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

    def submit_post(self, sub, title, text, link, image, video, parent, flairname, flairtext, collectionid, sort, commenttext, post_time, spoiler, nsfw, lock, contest, dontnotify, distinguish, sticky, lockcomment, distinguishcomment, stickycomment, wait):
        current_date = str(self.now.strftime("%m/%d/%Y, %H:%M"))

        if post_time != current_date:
            return 1

        # flair name to id
        choices = list(self.reddit.subreddit(
            sub).flair.link_templates.user_selectable())
        template_id = next(
            (x for x in choices if x["flair_text"] == flairname), None)
        if template_id is not None:
            template_id = template_id["flair_template_id"]
        else:
            print(
                "Failed to find flair named %s. Attempting to post without flair" % flairname)
            template_id = None

        if parent is None:
            try:
                if image is None and video is None:
                    submission = self.reddit.subreddit(sub).submit(title, selftext=text, url=link, flair_id=template_id, flair_text=flairtext, send_replies=not (
                        dontnotify), nsfw=nsfw, spoiler=spoiler, collection_id=collectionid)
                else:
                    if video is None:
                        submission = self.reddit.subreddit(sub).submit_image(title, image_path=image, flair_id=template_id, flair_text=flairtext, send_replies=not (
                            dontnotify), nsfw=nsfw, spoiler=spoiler, collection_id=collectionid)
                    else:
                        submission = self.reddit.subreddit(sub).submit_video(title, video_path=video, thumbnail_path=image, flair_id=template_id,
                                                                             flair_text=flairtext, send_replies=not (dontnotify), nsfw=nsfw, spoiler=spoiler, collection_id=collectionid)

                print(
                    f"Posted {to_link(submission.permalink)} at {current_date}")

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
            print(f"Commented {to_link(comment.permalink)}")
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
