# Author: STS-Mining
# Version 1.0

import tkinter as tk
from pytube import YouTube

def on_entry_click(event):
    """Function to clear the placeholder text when the entry widget is clicked."""
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.config(fg='black')

def on_focus_out(event):
    """Function to restore the placeholder text if the entry widget loses focus without input."""
    if not entry.get():
        entry.insert(0, placeholder_text)
        entry.config(fg='grey')

def toggle_mode():
    global dark_mode
    dark_mode = not dark_mode
    update_colors()

def update_colors():
    if dark_mode:
        root.config(bg="#333333")
        url_label.config(bg="#333333", fg="white")
        entry.config(bg="#555555", fg="white")
        download_button.config(bg="#3C3F41", fg="white", borderwidth=3, relief="raised", bd=3, padx=10, pady=5)
        status_label.config(bg="#333333", fg="white")
        #dark_mode_button.config(bg="#3C3F41", fg="white", borderwidth=3, relief="raised", bd=3)
    else:
        root.config(bg="#F0F0F0")
        url_label.config(bg="#F0F0F0", fg="black")
        entry.config(bg="#D3D3D3", fg="black")
        download_button.config(bg="#3C3F41", fg="white", borderwidth=3, relief="raised", bd=3, padx=10, pady=5)
        status_label.config(bg="#F0F0F0", fg="black")
        #dark_mode_button.config(bg="#3C3F41", fg="white", borderwidth=3, relief="raised", bd=3)

def download_video(download_dir):
    url = entry.get()
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(download_dir)
        status_label.config(text="Download Successful!\n\nIf you like our app, please make a donation!\nBTC: bc1qnxsj7tvvczztsl7hdvy0e2wprd9na2ev840mh9")
    except Exception as e:
        status_label.config(text=f"Invalid YouTube URL...")

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("700x550")

dark_mode = True

placeholder_text = "Paste url address here..."
url_label = tk.Label(root, fg='#9ACD32', font=('Helvetica', 12, 'bold'))
url_label.pack(pady=5)

entry = tk.Entry(root, width=65, fg='grey', font=('Helvetica', 10))
entry.insert(0, placeholder_text)
entry.bind("<FocusIn>", on_entry_click)
entry.bind("<FocusOut>", on_focus_out)
entry.pack(pady=5)

download_button = tk.Button(root, text="Download", command=lambda: download_video("."), bg="#3C3F41", fg="white", font=('Helvetica', 10, 'bold'), borderwidth=3, relief="raised", bd=3)
download_button.pack(pady=5, padx=10)

status_label = tk.Label(root, text="", fg='#FF0000', font=('Helvetica', 10, 'italic'))
status_label.pack(pady=5)

# dark_mode_button = tk.Button(root, text="Toggle Dark Mode", command=toggle_mode, bg="#3C3F41", fg="white", font=('Helvetica', 10, 'bold'), borderwidth=3, relief="raised", bd=3)
# dark_mode_button.pack(pady=5, padx=10)

update_colors()
root.mainloop()
