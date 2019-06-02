import requests as req
import shutil
import os
import threading
import re
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

# JSON Parse Function
def extract_values(obj, key):
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

    return results

def downloadImages(url, board, threadnumber, result_title, filename, text_var, i, frame):
    while True:
        try:
            res = req.get(url, stream=True)
        except Exception as e:
            continue
        break # No error happened we're good

    if res.status_code != 200:
        exit(1)

    with open("images/" + board + "/" + str(threadnumber) + "-" + result_title + "/" + filename, 'wb') as f:
        shutil.copyfileobj(res.raw, f)

def getImages(board, threadnumber, text_var, root, frame, photo_preview, var):
    if(len(board) == 0 or len(threadnumber) == 0):
        messagebox.showinfo("Forgot field", "Please fill both fields!")
        return False

    board = board.lower()
    url = "http://a.4cdn.org/" + board + "/thread/" + str(threadnumber) + ".json" # JSON of each thread
    result = req.get(url)

    if result.status_code != 200: # Check exit code
        messagebox.showerror("Error", "Thread or Board not found!")
        return False

    text = result.json()

    try:
        result_title = text["posts"][0]["com"].replace(" ", "").lower().replace("/", "").replace(".", "").replace(",", "")[:4]

        # Check if bad chars are in title (causes bad error message :-()
        expression = "^[<>/\\,\.\-'\"]$"
        if re.search(expression, result_title):
            result_title = "title"

    except KeyError:
        result_title = "title"

    result_filename = extract_values(text, "tim") # Extract the imagename from JSON nested object of thread
    result_extension = extract_values(text, "ext") # Extract the extension form JSON

    total_files = len(result_filename)

    i = 0

    if not os.path.exists("images/" + board + "/") and not os.path.isdir("images/" + board + "/"):
        os.mkdir("images/" + board + "/")

    if not os.path.exists("images/" + board + "/" + str(threadnumber) + "-" + result_title) and not os.path.isdir("images/" + board + "/" + str(threadnumber) + "-" + result_title): # Check if thread got ripped already
        os.mkdir("images/" + board + "/" + str(threadnumber) + "-" + result_title)
    else:
        messagebox.showinfo("Already ripped", "Thread already got ripped! Please delete the folder \"images/" + board + "/" + str(threadnumber) + "-" + result_title + "\" to redownload it.")

        if messagebox.askokcancel("Delete folder", "Delete folder and redownload?"):
            folder = "images/" + board + "/" + str(threadnumber) + "-" + result_title + "/"
            for the_file in os.listdir(folder):
                    file_path = os.path.join(folder, the_file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                            continue
        else:
            return False

    if not messagebox.askokcancel("Images found", str(total_files) + " images have been found. Download now?"):
        messagebox.showinfo("Aborted", "Download aborted.")
        return False

    t = []

    if var == 0:
        check_mode = False
    else:
        check_mode = True

    for r in result_filename: # For each file in the thread
        filename = str(r) + result_extension[i]
        url = "http://i.4cdn.org/" + board + "/" + filename

        text_var.config(text=str(total_files - 1) + " images left please don't close the application!")

        t.append(threading.Thread(target=downloadImages, args=(url, board, threadnumber, result_title, filename, text_var, i, frame,)))

        try:
            t[i].start()
        except Exception as e:
            continue

        t[i].join() # Commenting this out speeds things up a lot

        if result_extension[i] != ".webm":
            try: # To avoid nasty errors
                if os.path.isfile("images/" + board + "/" + str(threadnumber) + "-" + result_title + "/" + filename):
                    # Display thumbnail image
                    file = Image.open("images/" + board + "/" + str(threadnumber) + "-" + result_title + "/" + filename)

                    # Resize image
                    if file.width > file.height:
                        w = 300;
                        h = int((file.height * w) / file.width)
                    else:
                        h = 300;
                        w = int((file.width * h) / file.height)

                    file = file.resize((w, h), Image.ANTIALIAS)
                    photo = ImageTk.PhotoImage(file)
                    photo_preview.configure(image=photo)
                    photo_preview.image = photo
            except Exception as e:
                print(e)
                continue

            if check_mode:
                if not messagebox.askyesno("Image", "Keep image?", master=frame):
                    os.unlink("images/" + board + "/" + str(threadnumber) + "-" + result_title + "/" + filename)

        frame.update()
        root.update()

        if i == (len(result_filename)-1): # Last image
            text_var.config(text="Please don't close, writing data into files!")
            frame.update()
            root.update()

        i += 1
        total_files -= 1

    text_var.config(text="Thread has successfully been downloaded.")
    messagebox.showinfo("Success", str(i) + " files have successfully been downloaded!")

def on_closing(root):
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

def main():
    # Initialize GUI
    root = Tk()
    root.title("Thread Ripper")
    root.grid_rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.configure(background="grey")
    root.resizable(False, False)
    var = IntVar()

    # Set window icon
    img = PhotoImage(file="images/app/ico.png")
    root.tk.call("wm", "iconphoto", root._w, img)

    # Set main frame
    frame = Frame(root, bg="gray")
    frame.grid(sticky="news")

    # Set labels
    Label(frame, text = "Thread Ripper v1.0 Beta", bg="gray", padx=10, pady=10).grid(row=0, column=2)
    Label(frame, text = "Enter board", font=("Helvetica", 12), bg="gray").grid(row=2, column=2)
    Label(frame, text = "Enter thread number", font=("Helvetica", 12), bg="gray").grid(row=4, column=2)
    Checkbutton(frame, text = "Check image before downloading", bg="gray", activebackground="gray", variable=var).grid(row=6, column=2, padx=10, pady=10)


    # Label for photo preview
    placeholder = PhotoImage(file="images/app/ico.png")
    photo_preview = Label(frame, image=placeholder, bg="gray", width=256, height=256)
    photo_preview.image = placeholder
    photo_preview.grid(row=9, column=2, pady=20, padx=20)

    # Set input fields board
    input_board = Entry(frame, width=27)
    input_board.grid(row=3, column=2)
    # Set input fields thread
    input_threadno = Entry(frame, width=27)
    input_threadno.grid(row=5, column=2)

    Button(frame, text="Load Thread", command=(lambda: getImages(input_board.get(), input_threadno.get(), status, root, frame, photo_preview, var.get())), bg="grey", font=("Helvetica", 10), width=20).grid(row=7, column=2, padx=5, pady=5)

    # Label which we'll print the status to
    status = Label(bg="gray", wraplength=170, justify=LEFT)
    status.grid(row=8, column=0, padx=20, pady=20)

    root.protocol("WM_DELETE_WINDOW", (lambda: on_closing(root)))
    root.mainloop()

if __name__ == "__main__":
    main()
