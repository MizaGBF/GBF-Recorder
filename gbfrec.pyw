# -*- coding: utf-8 -*-
import time
import tkinter as Tk
import tkinter.ttk as ttk
import subprocess
import signal
import os
import json
from datetime import datetime, timedelta
import win32gui
import keyboard

app = None

class simpleui(Tk.Tk):
    def __init__(self, parent): # the UI is built here
        Tk.Tk.__init__(self,parent)
        self.parent = parent
        self.running = True
        self.recording = False
        self.prc = None

        Tk.Label(self, text="ffmpeg path").grid(row=0, column=0, sticky="ne")

        self.ffmpegvar = Tk.StringVar()
        self.ffmpegvar.trace("w", lambda name, index, mode, sv=self.ffmpegvar: self.ffmpegupdate())
        Tk.Entry(self, textvariable=self.ffmpegvar).grid(row=0, column=1, columnspan=10, sticky="ne")

        #Tk.Button(self, text="Start", command=self.startRecord).grid(row=1, column=1, sticky="ews") # clicked color button
        #Tk.Button(self, text="Stop", command=self.stopRecord).grid(row=1, column=2, sticky="ews") # clicked color button
        Tk.Label(self, text="Ctrl+1 : start").grid(row=1, column=0, sticky="ne")
        Tk.Label(self, text="Ctrl+2 : stop").grid(row=2, column=0, sticky="ne")

    def ffmpegupdate(self):
        self.ffmpeg = self.ffmpegvar.get()

    def load(self): # same thing but for save.json
        try:
            with open('save.json') as f:
                data = json.load(f)
                if 'ffmpeg' in data:
                    self.ffmpegvar.set(data['ffmpeg'])
                    self.ffmpegupdate()
                return True
        except Exception as e:
            print('load(): ' + str(e))
            return False

    def save(self, sortBackup=True): # saving
        try:
            with open('save.json', 'w') as outfile:
                data = {}
                data['ffmpeg'] = self.ffmpegvar.get()
                json.dump(data, outfile)
            return True
        except Exception as e:
            print('save(): ' + str(e))
            return False

    def close(self):
        self.appRunning = False
        self.stopRecord()
        self.save()
        self.destroy()

    def checkForChrome(self):
        hwnd = win32gui.GetForegroundWindow()
        if win32gui.GetWindowText(hwnd).find("- Google Chrome") != -1:
            return win32gui.GetWindowRect(hwnd)
        else:
            return None

    def startRecord(self):
        if self.recording: return

        rect = self.checkForChrome()
        if rect is None: return

        print(self.ffmpeg + "\ffmpeg.exe")
        #sound: -f dshow -i audio="Microphone (High Definition Aud"
        self.prc = subprocess.Popen([self.ffmpeg + "\\ffmpeg.exe", "-y", "-rtbufsize", "150M", "-f", "gdigrab", "-framerate", "30", "-offset_x", str(rect[0]+67), "-offset_y", str(rect[1]+112), "-video_size", "320x450", "-draw_mouse", "0", "-i", "desktop", "-i", "image.png", "-filter_complex", "[0:v]scale=-1:720 [ovrl], [1:v][ovrl] overlay=384:0", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-r", "30", "-preset", "ultrafast", "-tune", "zerolatency", "-crf", "28", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "output_{0:%Y_%m_%d-%H%M}.flv".format(datetime.now())], shell=False)
        self.recording = True
        print("started")

    def stopRecord(self):
        if not self.recording: return
        try:
            pid = self.prc.pid
            os.kill(pid, signal.SIGINT)
        except:
            pass
        self.recording = False
        print("stopped")

# =============================================================================================
# entry point
# =============================================================================================
if __name__ == "__main__":
    # create the UI
    app = simpleui(None)
    app.title("GBF Recorder alpha 0.1")
    app.resizable(width=False, height=False) # not resizable
    app.protocol("WM_DELETE_WINDOW", app.close) # call close() if we close the window
    app.load()

    keyboard.add_hotkey('Ctrl+1', app.startRecord)
    keyboard.add_hotkey('Ctrl+2', app.stopRecord)

    # main loop
    while app.running:
        app.update()
        time.sleep(0.02)