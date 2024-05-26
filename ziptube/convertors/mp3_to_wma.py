#!/usr/bin/env python3

'''This module will convert a single mp3 file to wma using ffmpeg'''

import os
import subprocess
import tkinter as tk
from tkinter import filedialog

FFMPEG_PATH = "ziptube/assets/ffmpeg/bin/ffmpeg.exe"  # Specify the full path to ffmpeg.exe here
CONVERT_TO = "wma"
CONVERT_FROM = "mp3"

def convert(file_path):
    root_path, filename = os.path.split(file_path)
    new_filename = os.path.splitext(filename)[0] + "." + CONVERT_TO
    new_path = os.path.join(root_path, new_filename)

    completed = subprocess.run([FFMPEG_PATH,
                                "-loglevel",
                                "quiet",
                                "-hide_banner",
                                "-y",
                                "-i",
                                file_path,
                                "-codec:a",
                                CONVERT_TO,
                                new_path],
                               stderr=subprocess.DEVNULL,
                               stdout=subprocess.DEVNULL,
                               stdin=subprocess.PIPE)
    print(f"'{new_path}' - Conversion Successful ...")
    if completed.returncode != 0:
        print(f"Conversion failed for {file_path}")
    return completed


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    file_path = filedialog.askopenfilename(filetypes=[(f"{CONVERT_FROM.upper()} files", f"*.{CONVERT_FROM.lower()}"), ("All files", "*.*")])
    if file_path:
        print(f"Converting {file_path} to {CONVERT_TO.capitalize}...")
        result = convert(file_path)
        if result.returncode == 0:
            print("Conversion successful!")
        else:
            print("Conversion failed.")
    else:
        print("No file selected.")
