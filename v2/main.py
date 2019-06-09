import requests
import threading
import os
import re
import urllib.request
from time import sleep

os.system("cls")

class Download:
    def __init__(self):
        self.error = []
        self.boards = [ line.rstrip("\n") for line in open("boards_custom.txt") ]
        self.data_threads = {}
        self.data_images = {}

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

                print(thread_name)

                for post in result['posts']:
                    if "tim" in post:
                        files.append(board + "-" + str(post['tim']) + post['ext'])

                self.data_images[thread_name] = [ f for f in files ]

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

        t = []
        i = 0

        for thread, posts in self.data_images.items():
            t.append(threading.Thread(target=self.writeImages, args=(posts, thread,)))
            t[i].start()

            i += 1

    def writeImages(self, posts, thread):
        for file in posts:
            no = file.find("-")
            board = file[0:no]
            filename = file[(no+1):]
            url = "http://i.4cdn.org/{}/{}".format(board, filename)

            path = "images/" + board + "/" + thread + "/" + filename
            if not os.path.exists(path) and not os.path.isfile(path):
                #try:
                #    result = requests.get(url, stream=True)
                #except Exception as e:
                #    continue

                print("Writing image {} to file".format(path))
                try:
                    urllib.request.urlretrieve(url, path)
                except Exception as e:
                    continue
                #with open(path, 'wb') as f:
                #    shutil.copyfileobj(result.raw, f)
                #    f.close()
            else:
                print("Skipping file {}, exists".format(path))


def main():
    # Create new instance
    download = Download()

    download.fetchImages()
    download.downloadImages()

    print("=-=-=DONE=-=-=")

if __name__ == "__main__":
    main()
