import requests as req
import time
import shutil
import os
import threading

# Menu
def menu():
    print("+----------------------------+")
    print("|        Choose Board        |")
    print("+============================+")
    print("| [1] - /b/                  |")
    print("| [2] - /g/                  |")
    print("| [3] - /pol/                |")
    print("| [4] - other                |")
    print("+----------------------------+")

    return input("Choose board: ")

# Function to check the board the user entered
def checkBoard(board):
    try:
        board = int(board)
    except ValueError:
        print("Invalid choice! Restart the script retard!")
        exit(1)

    return board

def transformBoard(board): # Transform the menu choice into board
    boards = [ "b", "g", "pol" ]

    if(board == 4):
        board = input("Enter custom board: ")
    elif(board > 4):
        print("Choose a value that's mentioned in the menu.")
        exit(1)
    else:
        board = boards[board - 1]

    return board

# JSON Parse Function
def extract_values(obj, key):
    s = time.time()
    # Pull all values of specified key from nested JSON.
    arr = []

    def extract(obj, arr, key):
        # Recursively search for values of key in JSON tree.
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    print("Time to extract values: %s seconds" % (time.time() - s))
    return results

def downloadImages(url, board, threadnumber, result_title, filename):
    res = req.get(url, stream=True)

    if res.status_code != 200:
        print("[-] An error occured while getting the image")
        os.sys.exit(1)

    with open("images/thread-" + board + "-" + str(threadnumber) + "-" + result_title + "/" + filename, 'wb') as f:
        print("[+] Writing image into file")
        shutil.copyfileobj(res.raw, f)

def getImages(board, threadnumber):
    url = "http://a.4cdn.org/" + board + "/thread/" + str(threadnumber) + ".json" # JSON of each thread
    result = req.get(url)

    if result.status_code != 200: # Check exit code
        print("Thread or Board not found.")
        exit(1)

    text = result.json()

    try:
        result_title = text["posts"][0]["com"].replace(" ", "").lower().replace("/", "").replace(".", "").replace(",", "")[:6]
    except KeyError:
        result_title = "title"

    result_filename = extract_values(text, "tim") # Extract the imagename from JSON nested object of thread
    result_extension = extract_values(text, "ext") # Extract the extension form JSON

    total_files = len(result_filename)

    i = 0

    if not os.path.exists("images/thread-" + board + "-" + str(threadnumber)) and not os.path.isdir("images/thread-" + board + "-" + str(threadnumber)): # Check if thread got ripped already
        os.mkdir("images/thread-" + board + "-" + str(threadnumber) + "-" + result_title)
    else:
        print("[!] Thread already got ripped!")
        return False

    start = time.localtime(time.time())

    t = []

    print("\n[ " + str(start.tm_hour) + ":" + str(start.tm_min) + ":" + str(start.tm_sec) + " ] Starting to fetch images\n")

    for r in result_filename: # For each file in the thread
        filename = str(r) + result_extension[i]
        url = "http://i.4cdn.org/" + board + "/" + filename

        print("************GET**************")
        print("[?] Images left " + str(total_files - 1))
        print("[+] Getting Image " + str(i + 1))
        print("[+] " + url)

        t.append(threading.Thread(target=downloadImages, args=(url, board, threadnumber, result_title, filename,)))
        t[i].start()

        i += 1
        total_files -= 1

        print("+=+=+=+=+=+=DONE+=+=+=+=+=+=+\n")

    end = time.localtime(time.time())

def main():
    # Clear the screen
    os.system("cls")

    # Let the user choose the board he wants to watch
    board = menu()
    board = transformBoard(checkBoard(board))

    try: # Try to get the thread number yote
        threadnumber = int(input("Enter thread no: "))
    except ValueError:
        print("Not a number retard!")
        exit(1)

    processTime = time.time()

    getImages(board, threadnumber)

if __name__ == "__main__":
    main()
