# Author: STS-Mining

import customtkinter as ctk
from tkinter import ttk
from pytube import YouTube
import os

def download_video():
    url = entry_url.get()
    resolutions = resolutions_var.get()
    progress_label.pack(pady="10p")
    progress_bar.pack(pady="10p")
    status_label.pack(pady="10p")

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(res=resolutions).first()

        # Download the video to specific directory
        os.path.join("downloads", f"{yt.title}")
        stream.download(output_path="downloads")
        status_label.configure(
            text=f"{yt.title}",
            text_color="white",
            fg_color="transparent",
            font=("Helvetica", 17, "underline")
            )


    except Exception as e:
        status_label.configure(text=f"Error {str(e)}", text_color="white", fg_color="red")

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percentage = (bytes_downloaded / total_size) * 100
    progress_label.configure(text="{} % of {} | {}".format(int(progress_percentage), bytes_to_nearest_measurement(int(bytes_downloaded)), bytes_to_nearest_measurement(int(total_size))))
    progress_label.update()
    progress_bar.set(float(progress_percentage / 100))

def bytes_to_nearest_measurement(bytes):
    megabytes = bytes / (1024 * 1024)
    gigabytes = bytes / (1024 * 1024 * 1024)
    if gigabytes >= 1:
        return "{} GB".format(round(gigabytes))
    else:
        return "{} MB".format(round(megabytes))


# Create a root window
root = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Title of the window
root.title("STS Mining")
root.iconbitmap("pmp.ico")

# Set min and max width and the height
root.geometry("720x480")
root.minsize(720, 480)
root.maxsize(1080, 720)

# Create a frame to hold the content
content_frame = ctk.CTkFrame(root)
content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

# Create a label fand the entry widget for the video url
url_label = ctk.CTkLabel(content_frame, text="YouTube Downloader")
entry_url = ctk.CTkEntry(content_frame, width=400, height=40, placeholder_text=("Paste URL here..."))
url_label.pack(pady="10p")
entry_url.pack(pady="10p")

# Create a resolutions combo box
resolutions = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
resolutions_var = ctk.StringVar()
resolutions_combobox = ttk.Combobox(content_frame, values=resolutions, textvariable=resolutions_var)
resolutions_combobox.pack(pady="10p")
resolutions_combobox.set("720p")

# Create a download button
download_button = ctk.CTkButton(content_frame, width=300, height=40, text="Download", command=download_video, fg_color="transparent", hover_color="#333030", border_color="#FFCC70", border_width=2)
download_button.pack(pady="10p")

# Create a label and the progress bar to display the download progress
progress_label = ctk.CTkLabel(content_frame, text="0%")
progress_bar = ctk.CTkProgressBar(content_frame, width=200, height=20, border_color="#FFCC70", border_width=2)
progress_bar.set(0)

# Create the status label
status_label = ctk.CTkLabel(content_frame, text="")

# Start the app
root.mainloop()
