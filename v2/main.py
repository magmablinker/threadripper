import requests
import threading
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
        t = []
        for board, threads in self.data_threads.items():
            thread_name = self.data_threads[board][i]["posts"][0]["no"]
            t.append(threading.Thread(target=self.fetchPosts, args=(threads, i, thread_name, board,)))
            t[i].start()

            if (i%5) == 0:
                t[i].join()

            print(
                "***************************************************",
                "Done fetching data for thread {} on board /{}/".format(thread_name, board),
                "***************************************************", sep="\n")
            i += 1

    def fetchPosts(self, threads, i, thread_name, board):
            for thread in threads:
                url = "http://a.4cdn.org/{}/thread/{}.json".format(board, thread["posts"][0]["no"])

                try:
                    result = requests.get(url)
                except Exception as e:
                    print("=-=-=ERROR=-=-=",
                          "Fetching images for thread {} on board {} failed, skipping".format(thread["posts"][0]["no"], board),
                          "=-=-=-=-=-=-=-=", sep="\n")
                    continue

                if result.status_code != 200:
                    continue

                result = result.json()

                files = []

                for post in result['posts']:
                    if "tim" in post:
                        files.append(str(post['tim']) + post['ext'])

                self.data_images[thread_name] = [ f for f in files ]

    def downloadImages(self):
        pass

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
