# Author: STS-Mining

from customtkinter import *
import tkinter as tk
from pytube import YouTube

def on_entry_click(event):
    """Function to clear the placeholder text when the entry widget is clicked."""
    if entry.get() == placeholder_text:
        entry.delete(0, tk.END)
        entry.configure(fg_color='black')

def on_focus_out(event):
    """Function to restore the placeholder text if the entry widget loses focus without input."""
    if not entry.get():
        entry.insert(0, placeholder_text)
        entry.configure(fg_color='grey')

def download_video(download_dir):
    url = entry.get()
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(download_dir)
        status_label.config(text="Download Successful!\n\nIf you like our app, please make a donation!\nBTC: bc1qnxsj7tvvczztsl7hdvy0e2wprd9na2ev840mh9")
    except Exception as e:
        status_label.config(text=f"Invalid YouTube URL...")

app = CTk()
app.geometry("700x550")
app.title("STS-Mining")
app.iconbitmap("pmp.ico")

set_appearance_mode("dark")

btn = CTkButton(master=app, text="Download", command=lambda: download_video("."), corner_radius=32, fg_color="transparent", hover_color="#4158D0", border_color="#FFCC70", border_width=2)
btn.place(relx=0.5, rely=0.5, anchor="center")

placeholder_text = "Paste URL address here..."

entry = CTkEntry(app, width=350, fg_color='grey', font=('Helvetica', 10))
entry.insert(0, placeholder_text)
entry.bind("<FocusIn>", on_entry_click)
entry.bind("<FocusOut>", on_focus_out)
entry.pack(pady=185)

status_label = tk.Label(app, text="", fg='#FF0000', font=('Helvetica', 10, 'italic'))
status_label.pack(side=tk.BOTTOM, pady=125)

app.mainloop()
