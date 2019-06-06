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

            self.data_threads[board] = [ thread for thread in result['threads'][0]['posts'] ]

            print(
                "***************************************************",
                "Done fetching data for /{}/, sleeping one second".format(board),
                "***************************************************", sep="\n")

            sleep(1)

        return True # Kinda useless

    def fetchContent(self):
        i = 0
        for board, threads in self.data_threads.items():
            print(board)
            pprint(self.data_threads)
            thread_name = self.data_threads[board]["no"][i]
            for thread in threads:
                url = "http://a.4cdn.org/{}/thread/{}.json".format(board, thread["no"])

                try:
                    result = requests.get(url)
                except Exception as e:
                    print("=-=-=ERROR=-=-=",
                          "Fetching images for thread {} on board {} failed, skipping".format(thread["no"], board),
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

                print(self.data_images[thread_name])

                print(
                    "***************************************************",
                    "Done fetching data for thread {} on board /{}/, sleeping one second".format(thread_name, board),
                    "***************************************************", sep="\n")

                sleep(1)
            i += 1

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
