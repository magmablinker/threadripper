import requests
import threading
import os
import re
import urllib.request
import pymysql
import base64
from pprint import pprint
from time import sleep

os.system("cls")

class Download:
    def __init__(self):
        self.error = ""
        self.boards = [ line.rstrip("\n") for line in open("boards_custom.txt") ]
        self.data_threads = {}
        self.data_images = {}
        try:
            self.db = pymysql.connect(
                        host="localhost",
                        user="threadripper",
                        passwd="1337",
                        db="threadrip",
                        port=3306,
                        autocommit=True
                    )
            self.cur = self.db.cursor()
        except Exception as e:
            print("=-=-=ERROR=-=-=",
                  "DB CONN FAILED!!",
                  "=-=-=-=-=-=-=-=", sep="\n")
            exit(1)

    def fetchImages(self):
        if not self.fetchThreads():
            self.error = "Fetching threads failed."
            return False

        if not self.fetchContent():
            self.error = "Fetching images failed."
            return False


    def fetchThreads(self):
        for board in self.boards:
            url = "http://a.4cdn.org/%s/1.json" %(board)

            try:
                result = requests.get(url)
            except Exception as e:
                print("=-=-=ERROR=-=-=",
                      "Fetching data for board {} failed, skipping".format(board),
                      "=-=-=-=-=-=-=-=", sep="\n")
                continue

            if result.status_code != 200:
                print("=-=-=ERROR=-=-=",
                      "Fetching board /{}/ returned stauts code {}".format(board, result.status_code),
                      "=-=-=-=-=-=-=-=", sep="\n")
                continue

            result = result.json()

            self.data_threads[board] = [ thread for thread in result["threads"] if "cock" not in thread["posts"][0]["semantic_url"] and "dick" not in thread["posts"][0]["semantic_url"] and "trap" not in thread["posts"][0]["semantic_url"] ]

            print(
                "***************************************************",
                "Done fetching data for /{}/, sleeping one second".format(board),
                "***************************************************", sep="\n")

            sleep(1)

        return True # Kinda useless

    def fetchContent(self):
        i = 0
        for board, threads in self.data_threads.items():
            for thread in threads:
                thread_name = str(thread["posts"][0]["no"]) + "-" + thread["posts"][0]["semantic_url"]
                url = "http://a.4cdn.org/{}/thread/{}.json".format(board, thread["posts"][0]["no"])

                try:
                    result = requests.get(url)
                except Exception as e:
                    print("=-=-=ERROR=-=-=",
                          "Fetching images for thread {} on board {} failed, skipping".format(thread["posts"]["no"], board),
                          "=-=-=-=-=-=-=-=", sep="\n")
                    continue

                if result.status_code != 200:
                    continue

                result = result.json()

                files = []
                comments = []

                for post in result['posts']:
                    if "tim" in post:
                        files.append(board + "-" + str(post['tim']) + post['ext'])
                    else:
                        files.append(None)
                    if "com" in post:
                        comments.append(post['com'])
                    else:
                        comments.append(None)

                self.data_images[thread_name] = {}
                self.data_images[thread_name]['images'] = files
                self.data_images[thread_name]['comments'] = comments

                # Insert query
                try:
                    insert_query = "INSERT INTO threads(thread_no, thread_title) VALUES({}, '{}')".format(int(thread["posts"][0]["no"]), thread["posts"][0]["semantic_url"])
                    print(insert_query)
                    self.cur.execute(insert_query)
                except Exception as e:
                    print(e)
                    print("IDIOT DB FAILED")

            i += 1

            print(
                "***************************************************",
                "Done fetching data for thread {} on board /{}/".format(thread_name, board),
                "***************************************************", sep="\n")

    def createDirectories(self):
        i = 0
        for board, threads in self.data_threads.items():
            for thread in threads:
                dir_name = "images/" + board + "/" + str(thread["posts"][0]["no"]) + "-" + thread["posts"][0]["semantic_url"]

                if not os.path.exists(dir_name) and not os.path.isdir(dir_name):
                        try:
                            os.makedirs(dir_name)
                        except Exception as e:
                            print("=-=-=ERROR=-=-=",
                                  "Making directory {} failed".format(dir_name),
                                  "=-=-=-=-=-=-=-=", sep="\n")
                            continue

                i += 1

    def downloadImages(self):
        self.createDirectories()

        print("******************************************",
              "Found {} images, downloading in 2 seconds.".format(sum(len(v) for v in self.data_images.values())),
              "******************************************", sep="\n")

        sleep(2)

        t = []
        i = 0

        for thread, posts in self.data_images.items():
            for (image, comment) in zip(posts['images'], posts['comments']):
                t.append(threading.Thread(target=self.writeImages, args=(image, comment, thread, i,)))
                t[i].start()
                i += 1
                
        t[i-1].join()

    def writeImages(self, image, comment, thread, i):
        if image != None:
            no = image.find("-")
            board = image[0:no]
            filename = image[(no+1):]
            threadno = int(thread[0:thread.find("-")])
            url = "http://i.4cdn.org/{}/{}".format(board, filename)
            path = "images/" + board + "/" + thread + "/" + filename

            if not os.path.exists(path) and not os.path.isfile(path):
                print("Writing image {} to file".format(path))
                try:
                    urllib.request.urlretrieve(url, path)
                    with open(path, "rb") as image_file:
                        encoded_image = db.escape_string(base64.b64encode(image_file.read()))
                    os.unlink(path)
                except Exception as e:
                    exit(1)

                print("Inserting image {} into db".format(path))
                try:
                    insert_query = "INSERT INTO comments(tid, comment) VALUES({}, '{}')".format(threadno, comment)
                    self.cur.execute(insert_query)
                    if not i == 0:
                        cid = self.db.insert_id()
                    else:
                        cid = self.cur.execute("SELECT cid FROM comments ORDER BY cid DESC LIMIT 1")
                    insert_query = "INSERT INTO images(cid, image) VALUES({}, '{}')".format(int(cid), encoded_image)
                    self.cur.execute(insert_query)
                except Exception as e:
                    print(e)
                    print("DB Insert failed!")
            else:
                print("Skipping file {}, exists".format(path))

def main():
    # Create new instance
    download = Download()

    download.fetchImages()
    download.downloadImages()

if __name__ == "__main__":
    main()
