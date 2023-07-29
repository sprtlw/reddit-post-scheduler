import datetime
import time
import reddit


def main():
    reddit_func = reddit.RedditFunc()
    # open queue file
    queue = reddit.open_file("queue.json")

    while True:
        # update datetime
        reddit_func.now = datetime.datetime.now()

        for post in queue["posts"]:
            postspecs = {"sub": None, "title": None, "text": None, "link": None, "image": None, "video": None, "parent": None, "flairname": None, "flairtext": None, "collectionid": None, "sort": None, "commenttext": None, "post_time": None,
                         "spoiler": False, "nsfw": False, "lock": False, "contest": False, "dontnotify": False, "distinguish": False, "sticky": False, "lockcomment": False, "distinguishcomment": False, "stickycomment": False, "wait": False}
            postspecs.update(post)
            if postspecs["link"] != None:
                postspecs["text"] = None

            err = reddit_func.submit_post(sub=postspecs["sub"], title=postspecs["title"], text=postspecs["text"], link=postspecs["link"], image=postspecs["image"], video=postspecs["video"], parent=postspecs["parent"], flairname=postspecs["flairname"], flairtext=postspecs["flairtext"], collectionid=postspecs["collectionid"], sort=postspecs["sort"], commenttext=postspecs["commenttext"],
                                          post_time=postspecs["post_time"], spoiler=postspecs["spoiler"], nsfw=postspecs["nsfw"], lock=postspecs["lock"], contest=postspecs["contest"], dontnotify=postspecs["dontnotify"], distinguish=postspecs["distinguish"], sticky=postspecs["sticky"], lockcomment=postspecs["lockcomment"], distinguishcomment=postspecs["distinguishcomment"], stickycomment=postspecs["stickycomment"], wait=postspecs["wait"])
            if err == 5:
                reddit_func.submit_post(sub=postspecs["sub"], title=postspecs["title"], text=postspecs["text"], link=postspecs["link"], image=postspecs["image"], video=postspecs["video"], parent=postspecs["parent"], flairname=postspecs["flairname"], flairtext=postspecs["flairtext"], collectionid=postspecs["collectionid"], sort=postspecs["sort"], commenttext=postspecs["commenttext"], post_time=postspecs["post_time"],
                                        spoiler=postspecs["spoiler"], nsfw=postspecs["nsfw"], lock=postspecs["lock"], contest=postspecs["contest"], dontnotify=postspecs["dontnotify"], distinguish=postspecs["distinguish"], sticky=postspecs["sticky"], lockcomment=postspecs["lockcomment"], distinguishcomment=postspecs["distinguishcomment"], stickycomment=postspecs["stickycomment"], wait=postspecs["wait"])

        time.sleep(60)


if __name__ == "__main__":
    main()
