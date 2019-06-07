import requests
import threading
import os
import shutil
from pprint import pprint
from time import sleep

class Download:
    def __init__(self):
        self.error = []
        self.boards = [ line.rstrip("\n") for line in open("boards2.txt") ]
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

            self.data_threads[board] = [ thread for thread in result['threads'] ]

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

                print(dir_name)

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

        for thread, posts in self.data_images.items():
            for file in posts:
                no = file.find("-")
                board = file[0:no]
                filename = file[(no+1):]
                url = "http://i.4cdn.org/{}/{}".format(board, filename)

                try:
                    result = requests.get(url, stream=True)
                except Exception as e:
                    continue

                with open("images/" + board + "/" + thread + "/" + filename, 'wb') as f:
                    print("images/" + board + "/" + thread + "/" + filename)
                    shutil.copyfileobj(result.raw, f)
                    f.close()



def main():
    # Create new instance
    download = Download()

    if not download.fetchImages():
        if not download.downloadImages():
            pass
        else:
            pass
    else:
        pass

if __name__ == "__main__":
    main()
