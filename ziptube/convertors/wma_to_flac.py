#!\\usr\\bin\\env python3

'''This module will convert a single wma file to flac using ffmpeg'''

import os
import subprocess
import customtkinter as ctk
from tkinter import filedialog

FFMPEG_PATH = "ziptube\\assets\\ffmpeg\\bin\\ffmpeg.exe"  # Specify the full path to ffmpeg.exe here
CONVERT_FROM = "wma"
CONVERT_TO = "flac"

def start_countdown(seconds, countdown_label, app):
    if seconds > 0:
        countdown_label.configure(text=f"Closing window in {seconds} seconds...")
        app.after(1000, start_countdown, seconds - 1, countdown_label, app)
    else:
        app.destroy()

def convert(file_path):
    ''' Icon and logo location on system '''
    app_name = f"ZipTube - {CONVERT_FROM.upper()} to {CONVERT_TO.upper()}"
    icon = "ziptube\\assets\\images\\icon.ico"
    custom_theme = "ziptube\\assets\\themes\\custom.json"

    ''' Create a app window '''
    app = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(custom_theme)

    ''' Title of the window '''
    app.title(app_name)
    app.iconbitmap(icon)

    ''' Set min and max width and height '''
    min_max_height = 175
    min_max_width = 600
    app.geometry(f"{min_max_width}x{min_max_height}")
    app.minsize(min_max_width, min_max_height)
    app.maxsize(min_max_width, min_max_height)

    ''' Create a frame to hold the content '''
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    ''' Create the labels '''
    status_label = ctk.CTkLabel(main_frame, font=("calibri", 18, "normal"), text=f"Converting {CONVERT_FROM} file to {CONVERT_TO} file ...")
    status_label.pack(pady=10)
    countdown_label = ctk.CTkLabel(main_frame, font=("calibri", 18, "normal"), text="")
    countdown_label.pack(pady=10)

    ''' Start the conversion process '''
    def run_conversion():
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
        if completed.returncode == 0:
            status_label.configure(text=f"Successfully Converted ... \n\n{new_filename}")
        else:
            status_label.configure(text=f"Conversion failed ... \n\n{new_filename}")
        start_countdown(5, countdown_label, app)  # Start the countdown after the conversion is complete

    app.after(100, run_conversion)  # Delay the conversion to ensure the UI is fully rendered
    app.mainloop()

if __name__ == "__main__":
    root = ctk.CTk()
    root.withdraw()  # Hide the root window

    file_path = filedialog.askopenfilename(filetypes=[(f"{CONVERT_FROM.upper()} files", f"*.{CONVERT_FROM.lower()}"), ("All files", "*.*")])
    if file_path:
        print(f"Converting {file_path} to {CONVERT_TO.capitalize()}...")
        convert(file_path)
    else:
        print("No file selected.")