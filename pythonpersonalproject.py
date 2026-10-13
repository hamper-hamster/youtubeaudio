import yt_dlp
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import threading
import json
import os
import subprocess
import sys
import re
import getpass
from datetime import datetime

def updateprogram():
    if getattr(sys, 'frozen', False):
        return False
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "--quiet"], check=True, capture_output=True)
        return True
    except Exception:
        return False
updateprogram()

def entryplaceholder(entry, placeholder):
    entry.insert(0, placeholder)
    entry.config(fg = "gray")
    def onfocus(event):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg= "black")
    def offfocus(event):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg = "gray")
    entry.bind("<FocusIn>", onfocus)
    entry.bind("<FocusOut>", offfocus)

def choosedefault():
    if usedefault.get():
        singlename.config(state= "disabled", disabledbackground= "#FF4F2B")
        singleartist.config(state= "disabled", disabledbackground= "#FF4F2B")
    else:
        singlename.config(state= "normal")
        singleartist.config(state= "normal")

def playlist(link):
    return bool(re.search(r'[?&]list=', link))

if getattr(sys, 'frozen', False):
    basepath = os.path.join(os.getenv("APPDATA"), "youtubeaudiodownloader")
    os.makedirs(basepath, exist_ok = True)
    ffmpegpath = os.path.join(sys._MEIPASS, "ffmpeg.exe")
else:
    basepath = os.path.dirname(os.path.abspath(__file__))
    ffmpegpath = os.path.join(basepath, "ffmpeg.exe")
settings = os.path.join(basepath, "settings.json")
defaultfolder = os.path.expanduser("~/Downloads")
ffmpegfound = os.path.exists(ffmpegpath)

def loadsettings():
    if os.path.exists(settings):
        try:
            with open(settings, "r") as s:
                return json.load(s)
        except Exception:
            return{}
    return{}

def savesettings(newdata):
    try:
        data = loadsettings()
        data.update(newdata)
        with open(settings, "w") as s:
            json.dump(data, s)
    except Exception:
        pass

def lastfolder():
    return loadsettings().get("lastfolder", defaultfolder)

def savefolder(folder):
    savesettings({"lastfolder": folder})

root = tk.Tk()
root.config(bg = "#000000")
root.title("Youtube Audio Downloader")
root.geometry("600x600")
title = tk.Frame(root, bg = "#000000")
title.pack(side = "top", pady = (15, 10))
tk.Label(title, text = "Youtube", font = ("Calibri", 20, "bold"), fg = "#FF2500", bg = "#000000").pack(side = "left")
tk.Label(title, text = "Audio", font = ("Calibri", 20, "bold"), fg = "#FFFFFF", bg = "#000000").pack(side = "left")
tk.Label(title, text = "Downloader", font = ("Calibri", 20, "bold"), fg = "#00E6FF", bg = "#000000").pack(side = "left")
usedefault = tk.BooleanVar(value = False)


def getdisplayname():
    data = loadsettings()
    name = data.get("displayname")
    if name:
        return name
    entered = simpledialog.askstring("Welcome!", "What should I call you?", parent = root)
    if entered and entered.strip():
        entered = entered.strip()
        savesettings({"displayname": entered})
        return entered
    return getpass.getuser()

def greetuser():
    username = getdisplayname()
    hour = datetime.now().hour
    if hour > 5 and hour <= 12:
        return f"Hello there {username} the early bird! \U0001F426" 
    elif hour > 12 and hour <= 19:
        return f"Let's download something for today, {username}! \u2600\uFE0F"
    elif hour > 0 and hour <= 5:
        return f"Yo, {username}, why are you still not sleeping? \U0001F480"
    else:
        return f"What's up, night owl {username}? \U0001F989"

def changename():
    entered = simpledialog.askstring("Change name", "What should I call you?", parent = root)
    if entered and entered.strip():
        savesettings({"displayname": entered.strip()})
        greeting.config(text = greetuser())

greeting = tk.Label(root, text = greetuser(), fg = "#AAAAAA", bg = "#000000", font = ("Arial", 11, "italic"))
greeting.pack(side = "top", pady = (0, 10))
tk.Button(root, text = "Change name", command = changename, cursor = "hand2", font = ("Arial", 8)).pack(side = "top", pady = (0,10))
mode = tk.StringVar(value = "single")
menubar = tk.Frame(root, bg = "#000000")
menubar.pack(side = "top", pady = (0,10))

def choosemode(newmode):
    mode.set(newmode)
    if newmode == "single":
        playlistcontainer.pack_forget()
        singlecontainer.pack(fill = "x", padx = 20)
        singlebutton.config(bg = "#00E6FF", fg = "#000000")
        playlistbutton.config(bg = "#333333", fg = "#FFFFFF")
    else:
        singlecontainer.pack_forget()
        playlistcontainer.pack(fill = "x", padx = 20)
        playlistbutton.config(bg = "#00E6FF", fg = "#000000")
        singlebutton.config(bg = "#333333", fg = "#FFFFFF")
    status.config(text = "")
singlebutton = tk.Button(menubar, text = "Single Video", width=  16, cursor= "hand2", command = lambda: choosemode("single"))
singlebutton.grid(row = 0, column = 0, padx = 5)
playlistbutton = tk.Button(menubar, text = "Playlist", width =16, cursor = "hand2", command = lambda: choosemode("playlist"))
playlistbutton.grid(row=  0, column = 1, padx = 5)
singlecontainer = tk.Frame(root, bg = "#000000")
tk.Label(singlecontainer, text = "Youtube link: ", fg = "#FFFFFF", bg = "#000000", font = ("Arial", 14)).grid(row = 0, column = 0, sticky = "w", pady = 5)
singlelink = tk.Entry(singlecontainer, width = 35, bg = "#BABABA", font = ("Times New Roman", 12))
singlelink.grid(row = 0, column = 1, pady = 5)
entryplaceholder(singlelink, "Example: https://youtube.com/watch......")
tk.Label(singlecontainer, text = "Song name: ", fg = "#FFFFFF", bg = "#000000", font = ("Arial", 14)).grid(row = 1, column = 0, sticky = "w", pady = 5)
singlename = tk.Entry(singlecontainer, width = 35, bg = "#BABABA", font = ("Times New Roman", 12))
singlename.grid(row = 1, column = 1, pady = 5)
entryplaceholder(singlename, "Example: Imagine")
tk.Label(singlecontainer, text = "Artist name: ", fg = "#FFFFFF", bg = "#000000", font = ("Arial", 14)).grid(row = 2, column = 0, sticky = "w", pady = 5)
singleartist = tk.Entry(singlecontainer, width = 35, bg = "#BABABA", font = ("times New Roman", 12))
singleartist.grid(row = 2, column = 1, pady = 5)
entryplaceholder(singleartist, "Example: John Lennon")
tk.Checkbutton(singlecontainer, text="Use original Youtube title & artist", variable=usedefault, command=choosedefault, fg="#FFFFFF", bg="#000000", selectcolor= "#333333", activebackground="#000000", activeforeground="#FFFFFF").grid(row=3, column=0, columnspan=2, sticky="w", pady=(0,10))
playlistcontainer = tk.Frame(root, bg = "#000000")
tk.Label(playlistcontainer, text = "Playlist link: ", fg = "#FFFFFF", bg = "#000000", font = ("Arial", 14)).grid(row = 0, column = 0, sticky = "w", pady = 5)
playlistlink = tk.Entry(playlistcontainer, width = 35, bg = "#BABABA", font = ("Times New Roman", 12))
playlistlink.grid(row = 0, column = 1, pady = 5)
entryplaceholder(playlistlink, "Example: https://youtube.com/playlist......")
tk.Label(playlistcontainer, text = "*Song name and artist cannot be customized for playlists\nOriginal details will be used.", fg = "#FF0000", bg = "#000000", font = ("Arial", 9, "italic"), justify = "left").grid(row = 1, column = 0, columnspan = 2, sticky = "w", pady = (2,0))

def choosefolder():
    folder = filedialog.askdirectory()
    if folder:
        folderpath.set(folder)
        savefolder(folder)

folderpath = tk.StringVar(value = lastfolder())

def progresshook(d):
    info = d.get('info_dict', {})
    idx = info.get('playlist_index')
    count = info.get('playlist_count')
    vidtitle = info.get('title', '')
    if d['status'] == 'downloading':
        if idx and count:
            text = f"Downloading {idx}/{count}: {vidtitle}"
        else:
            text = "Downloading..."
        root.after(0, lambda: status.config(text = text, fg = "blue"))
    elif d['status'] == 'finished':
        if idx and count:
            root.after(0, lambda: status.config(text = f"Converting {idx}/{count}: {vidtitle}", fg = "blue"))

def allowtext(text):
    cleaned = re.sub(r'[\\/*?:"<>|]', "", text)
    return cleaned.strip()

def downloadaudio():
    ytlink = singlelink.get().strip()
    filelocation = folderpath.get().strip() or defaultfolder
    if not ytlink or ytlink == "Example: https://youtube.com/watch......":
        messagebox.showerror("Error detected", "Please enter a valid Youtube link.")
        return
    if "youtube.com" not in ytlink and "youtu.be" not in ytlink:
        messagebox.showerror("Error Detected", "Please enter a valid Youtube link.")
        return
    usingdefault = usedefault.get()
    if not usingdefault:
        ytname = allowtext(singlename.get().strip())
        ytartist = allowtext(singleartist.get().strip())
        if not ytname or ytname == "Example: Imagine" or not ytartist or ytartist == "Example: John Lennon":
            messagebox.showerror("Error detected", "Please enter song name and artist.")
            return
    singledownloadbutton.config(state = "disabled")
    status.config(text = "Downloading...", fg = "blue")
    def rundownload():
        if usingdefault: 
            download = {'format': 'bestaudio/best','outtmpl': f'{filelocation}/%(title)s.%(ext)s', 'ffmpeg_location': ffmpegpath,'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality':'192', }, {'key':'FFmpegMetadata'}]}
        else:   
            download = {'format': 'bestaudio/best','outtmpl': f'{filelocation}/{ytname}.%(ext)s', 'ffmpeg_location': ffmpegpath,'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality':'192', }, {'key':'FFmpegMetadata'}], 'postprocessor_args':['-metadata', f'artist={ytartist}','-metadata', f'title={ytname}']}
        try:
            with yt_dlp.YoutubeDL(download) as dl:
                dl.download([ytlink])
            root.after(0, lambda: status.config(text = f"Done! Saved to {filelocation}.", fg = "green"))
        except Exception as e:
            error = str(e)
            root.after(0, lambda: status.config(text = "Download failed.", fg = "red"))
            root.after(0, lambda: messagebox.showerror("Download error", error))
        finally:
            root.after(0, lambda: singledownloadbutton.config(state = "normal"))
    threading.Thread(target = rundownload, daemon = True).start()

def clearfieldvideo():
    singlelink.delete(0, tk.END)
    singlename.delete(0, tk.END)
    singleartist.delete(0, tk.END)
    singlename.config(state="normal")
    singleartist.config(state="normal")
    status.config(text = "")

def downloadplaylist():
    ytlink = playlistlink.get().strip()
    filelocation = folderpath.get().strip() or defaultfolder
    if not ytlink or ytlink == "Example: https://youtube.com/playlist......":
        messagebox.showerror("Error detected", "Please enter a valid Youtube playlist link.")
        return
    if "youtube.com" not in ytlink and "youtu.be" not in ytlink:
        messagebox.showerror("Error detected", "Please enter a valid Youtube playlist link.")
        return
    if not playlist(ytlink):
        messagebox.showerror("Error detected", "That doesn't look like a Youtube playlist link. Use the Single Video menu for individual videos.")
        return
    playlistdownloadbutton.config(state = "disabled")
    status.config(text = "Starting...", fg = "blue")
    def rundownload():
        download = {
            'format': 'bestaudio/best', 'outtmpl': f'{filelocation}/%(playlist_title)s/%(title)s.%(ext)s', 'ffmpeg_location':ffmpegpath, 'windowsfilenames': True, 'ignoreerrors': True, 'progress_hooks': [progresshook], 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}, {'key': 'FFmpegMetadata'}]}
        try:
            with yt_dlp.YoutubeDL(download) as dl:
                dl.download([ytlink])
            root.after(0, lambda: status.config(text = f"Done! Saved to {filelocation}.", fg = "green"))
        except Exception as e:
            error_message = str(e)
            root.after(0, lambda: status.config(text = "Download failed.", fg = "red"))
            root.after(0, lambda: messagebox.showerror("Download error", error_message))
        finally:
            root.after(0, lambda: playlistdownloadbutton.config(state = "normal"))
    threading.Thread(target = rundownload, daemon = True).start()
 
def clearplaylistfields():
    playlistlink.delete(0, tk.END)
    status.config(text = "")
    
tk.Button(singlecontainer, text = "Choose save folder", command = choosefolder, cursor = "hand2").grid(row = 4, column = 0, columnspan = 2, pady = (10,5))
path = tk.Frame(singlecontainer, bg = "#000000")
path.grid(row = 5, column = 0, columnspan = 2, pady = (0,10))
tk.Label(path, text = "Current download path: ", bg = "#000000", fg = "#FFFFFF", font = ("Arial", 10, "bold")).pack(side = "left")
tk.Label(path, textvariable = folderpath, fg = "#FFFFFF", wraplength = 440, bg = "#000000", font = ("Arial", 10, "underline")).pack(side = "left")
singlebuttonframe = tk.Frame(singlecontainer, bg = "#000000")
singlebuttonframe.grid(row = 6, column = 0, columnspan = 2, pady = 15)
singledownloadbutton = tk.Button(singlebuttonframe, text = "Download MP3", command = downloadaudio, bg = "green", fg = "white", width = 15, cursor = "hand2")
singledownloadbutton.grid(row = 0, column = 0, padx = 5)
tk.Button(singlebuttonframe, text = "Clear fields", command = clearfieldvideo, width = 15, cursor = "hand2").grid(row = 0, column = 1, padx = 5)
tk.Button(playlistcontainer, text = "Choose save folder", command = choosefolder, cursor = "hand2").grid(row = 2, column = 0, columnspan = 2, pady = (10,5))
playlistpath = tk.Frame(playlistcontainer, bg = "#000000")
playlistpath.grid(row = 3, column = 0, columnspan = 2, pady = (0,10))
tk.Label(playlistpath, text = "Current download path: ", bg = "#000000", fg = "#FFFFFF", font = ("Arial", 10, "bold")).pack(side = "left")
tk.Label(playlistpath, textvariable = folderpath, fg = "#FFFFFF", wraplength = 440, bg = "#000000", font = ("Arial", 10, "underline")).pack(side = "left")
playlistbuttonframe = tk.Frame(playlistcontainer,  bg = "#000000")
playlistbuttonframe.grid(row = 4, column = 0, columnspan = 2, pady = 15)
playlistdownloadbutton = tk.Button(playlistbuttonframe, text = "Download playlist", command = downloadplaylist, bg = "green", fg = "white", width = 16, cursor = "hand2")
playlistdownloadbutton.grid(row = 0, column = 0, padx = 5)
tk.Button(playlistbuttonframe, text = "Clear fields", command = clearplaylistfields, width = 16, cursor = "hand2").grid(row = 0, column = 1, padx = 5)
status = tk.Label(root, text = "", bg = "#000000", wraplength = 480)
status.pack(pady = (5,0))
tk.Label(root, text = "Made with <3 by KW.", fg = "gray", bg = "#000000", font = ("Segoe UI", 10)).pack(side = "bottom", pady = 8)
choosemode("single")
root.mainloop()