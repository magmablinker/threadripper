import requests
import threading
import os
import shutil
import pymysql
from time import sleep

if os.name == "nt": # Check if Windows or Linux
    os.system("cls")
else:
    os.system("clear")

class Download:
    def __init__(self):
        self.error = ""
        self.boards = [ line.rstrip("\n") for line in open("boards_custom.txt") ]
        self.data_threads = {}
        self.data_images = {}
        self.length = 0
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
            self.displayMessage(1, "The DB connection failed!")
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
                self.displayMessage(1, "Fetching data for board {} failed, skipping".format(board))
                continue

            if result.status_code != 200:
                self.displayMessage(1, "Fetching board /{}/ returned stauts code {}".format(board, result.status_code))
                continue

            result = result.json()

            self.data_threads[board] = [ thread for thread in result["threads"] if "cock" not in thread["posts"][0]["semantic_url"] and "dick" not in thread["posts"][0]["semantic_url"] and "trap" not in thread["posts"][0]["semantic_url"] ]

            self.displayMessage(0, "Done fetching data for /{}/, sleeping one second".format(board))

            sleep(1)

        return True # Kinda useless

    def fetchContent(self):
        for board, threads in self.data_threads.items():
            for thread in threads:
                thread_name = str(thread["posts"][0]["no"]) + "-" + thread["posts"][0]["semantic_url"]
                url = "http://a.4cdn.org/{}/thread/{}.json".format(board, thread["posts"][0]["no"])

                try:
                    result = requests.get(url)
                except Exception as e:
                    self.displayMessage(1, "Fetching images for thread {} on board {} failed, skipping".format(thread["posts"][0]["no"], board))
                    continue

                if result.status_code != 200:
                    continue

                result = result.json()

                files = []
                comments = []
                i = 0

                for post in result['posts']:
                    if "tim" in post:
                        if ".webm" not in post['ext']:
                            files.append(board + "-" + str(post['tim']) + post['ext'])
                        else:
                            files.append("{}-".format(board))
                    else:
                        files.append(None)
                    if "com" in post:
                        comments.append(post['com'])
                    else:
                        comments.append(None)

                    self.length += 1

                    i += 1

                self.data_images[thread_name] = {}
                self.data_images[thread_name]['images'] = files
                self.data_images[thread_name]['comments'] = comments

                # Insert query
                self.displayMessage(0, "Inserting {} into DB".format(int(thread["posts"][0]["no"])))
                try:
                    insert_query = "INSERT INTO threads(thread_no, thread_title) VALUES({}, '{}')".format(int(thread["posts"][0]["no"]), thread["posts"][0]["semantic_url"])
                    self.cur.execute(insert_query)
                except Exception as e:
                    self.displayMessage(2, "Post exists in database or insert failed!")

                self.displayMessage(3, "Done fetching data for thread {} on board /{}/".format(thread_name, board))

    def createDirectories(self):
        i = 0
        for board, threads in self.data_threads.items():
            for thread in threads:
                dir_name = "images/" + board + "/" + str(thread["posts"][0]["no"]) + "-" + thread["posts"][0]["semantic_url"]

                if not os.path.exists(dir_name) and not os.path.isdir(dir_name):
                        try:
                            os.makedirs(dir_name)
                        except Exception as e:
                            self.displayMessage(1, "Making directory {} failed".format(dir_name))
                            continue

                i += 1

    def downloadImages(self):
        self.createDirectories()
        self.displayMessage(3, "Found {} images, downloading in 2 seconds.".format(self.length))
        sleep(2)

        i = 0
        t = []

        for threads, posts in self.data_images.items():
            for (image, comment) in zip(posts['images'], posts['comments']):
                t.append(threading.Thread(target=self.writeImages, args=(image, comment, threads,)))
                t[i].start()
                if (i%10) == 0:
                    t[i].join()
                self.displayMessage(3, "Images left {}".format(self.length))
                self.length -= 1
                i += 1

        i = 0

        for threads, posts in self.data_images.items():
            for (image, comment) in zip(posts['images'], posts['comments']):
                self.insertIntoDB(image, comment, threads, i)
                i += 1
        self.displayMessage(3, "Inserts done, some files may still be processing")
        self.displayMessage(0, "Closing database connection")
        self.cur.close()

    def writeImages(self, image, comment, threads):
        if image != None:
            no = image.find("-")
            board = image[0:no]
            filename = image[(no+1):]
            threadno = int(threads[0:threads.find("-")])
            url = "http://i.4cdn.org/{}/{}".format(board, filename)
            path = "images/" + board + "/" + threads + "/" + filename

            if not os.path.exists(path) and not os.path.isfile(path):
                try:
                    res = requests.get(url, stream=True)

                    if res.status_code == 200:
                        with open(path, "wb") as f:
                            shutil.copyfileobj(res.raw, f)
                    else:
                        pass
                except Exception as e:
                    self.displayMessage(1, "Writing file failed")
            else:
                self.displayMessage(2, "Skipping file {}".format(path))

    def insertIntoDB(self, image, comment, threads, i):
        if image != None:
            no = image.find("-")
            board = image[0:no]
            filename = image[(no+1):]
            threadno = int(threads[0:threads.find("-")])
            path = "images/" + board + "/" + threads + "/" + filename

            self.displayMessage(0, "Inserting image {} into db".format(path))
            try:
                insert_query = "INSERT INTO comments(tid, comment) VALUES({}, '{}')".format(threadno, comment)
                self.cur.execute(insert_query)

                if not i == 0: # Get the id of the latest db entry
                    cid = self.db.insert_id()
                else:
                    cid = self.cur.execute("SELECT cid FROM comments ORDER BY cid DESC LIMIT 1")

                insert_query = "INSERT INTO images(cid, image) VALUES({}, '{}')".format(int(cid), path)
                self.cur.execute(insert_query)
            except Exception as e:
                self.displayMessage(1, "Insert for {} failed!".format(path))
        else:
            self.displayMessage(3, "Skipping None file.")

    def displayMessage(self, type, message):
        types = [ 0, 1, 2, 3 ] # 0 = Succes; 1 = Error; 2 = Warning; 3 = Info
        numToType = [ "[+]", "[-]", "[!]", "[?]" ]

        if type not in types:
            self.displayMessage(1, "Wrong usage!")
            return False

        print("******************************************",
              "{} {}".format(numToType[type], message),
              "******************************************\n", sep="\n")


def main():
    # Create new instance
    download = Download()

    download.fetchImages()
    download.downloadImages()

if __name__ == "__main__":
    main()
