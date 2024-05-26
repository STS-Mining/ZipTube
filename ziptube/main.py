''' 
Author: STS-Mining
Download YouTube videos to MP4 format,
Download only audio from YouTube videos,
Convert Audio files to various different formats.

+------------------+-------------------------------------------------+
| Version          | Description                                     |
+==================+=================================================+
| Version 1.25     | Download Youtube Videos, download only audio    |
|                  | from videos on youtube also.                    |
|                  | Convert audio files from mp4 (video) to mp3     |
|                  | Convert audio files from mp3 to wav, flac & wma |
|                  | Convert audio files from wav to flac, mp3 & wma |
|                  | Convert audio files from flac to mp3, wav & wma |
|                  | Convert audio files from wma to mp3, wav & flac |
|                  | Create function for the main menu button,       |
|                  | add custom theme from local assets directory    |
|                  | Add website button at bottom of main screen     |
|                  | Change button sizes and colors throughout app   |
+------------------+-------------------------------------------------+
| Version 1.24     | Download Youtube Videos, download only audio    |
|                  | from videos on youtube also.                    |
|                  | Convert audio files from mp4 (video) to mp3     |
|                  | Convert audio files from mp3 to wav, flac & wma |
|                  | Convert audio files from wav to flac, mp3 & wma |
|                  | Convert audio files from flac to mp3, wav & wma |
|                  | Convert audio files from wma to mp3, wav & flac |
|                  | Create function for the main menu button,       |
|                  | add custom theme from local assets directory    |
+------------------+-------------------------------------------------+
| Version 1.23     | Download Youtube Videos, download only audio    |
|                  | from videos on youtube also.                    |
|                  | Convert audio files from mp4 (video) to mp3     |
|                  | Convert audio files from mp3 to wav, flac & wma |
|                  | Convert audio files from wav to flac, mp3 & wma |
|                  | Convert audio files from flac to mp3, wav & wma |
|                  | Convert audio files from wma to mp3, wav & flac |
+------------------+-------------------------------------------------+
'''

import customtkinter as ctk
from pytube import YouTube
import time
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import pyperclip
from PIL import Image
import os
import re
import webbrowser
from tkinter import filedialog
import moviepy.editor as mp
from convertors import (
    flac_to_mp3, flac_to_wav, flac_to_wma, mp3_to_flac,
    mp3_to_wav, mp3_to_wma, wav_to_flac, wav_to_mp3,
    wav_to_wma, wma_to_flac, wma_to_mp3, wma_to_wav
)

''' Icon and logo location on system '''
app_name = "ZipTube"
icon = "ziptube/assets/images/icon.ico"
logo = "ziptube/assets/images/logo.png"
custom_theme = "ziptube/assets/themes/custom.json"
website_url = "https://sts-mining.github.io/website/"
discord_link = "https://discord.gg/Fd5uEgs4"
github_url = "https://github.com/STS-Mining"
feedback_email = "sts@github.com"

''' Function to link website to main screen in a button '''
def open_webpage(url):
    webbrowser.open(url, new=2)  # new=2: open in a new tab, if possible

def open_feedback_email():
    subject = f"{app_name} Feedback"
    webbrowser.open(f"mailto:{feedback_email}?subject={subject}")

''' Save location for all files downloaded '''
def choose_save_location():
    save_location = filedialog.askdirectory()
    return save_location


''' Function to download only audio files '''
def download_audio():
    global download_audio_button, output_path
    url = entry_url.get()
    youtube_url_pattern = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$"
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL.")
    elif not re.match(youtube_url_pattern, url):
        messagebox.showerror("Error", "Please enter a valid YouTube URL.")
    else:
        progress_label.pack(pady="10p")
        status_label.pack(pady="10p")
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            audio_stream = yt.streams.filter(only_audio=True, abr="128kbps").first()
            print(audio_stream.default_filename)
            save_dir = choose_save_location()
            output_path = save_dir
            filename = audio_stream.default_filename
            filename = filename.replace(".mp4", ".mp3")
            file_path = os.path.join(save_dir, filename)
            if os.path.exists(file_path):
                new_filename = simpledialog.askstring(
                    "Rename File",
                    "A file with this name already exists. Please enter a new filename:",
                    initialvalue=filename,
                )
                if new_filename is None:
                    return
            audio_stream.download(output_path=save_dir, filename=filename)
            status_label.configure(text=f"File saved as: {filename}")
        except Exception:
            status_label.configure(
                text=f"Error, Audio selected can't be downloaded ...",
                text_color="red",
            )
            app.after(2000, hide_labels)


''' Function that downloads the video once the download button is pressed '''
def download_video(resolutions_var):
    global download_button, output_path
    url = entry_url.get()
    resolution = resolutions_var.get()
    ''' Check if the resolution has not been selected '''
    if not resolution:
        messagebox.showerror("Error", "Please select a resolution.")
        return

    progress_label.pack(pady="10p")
    status_label.pack(pady="10p")
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(res=resolution).first()
        save_dir = choose_save_location()
        output_path = save_dir
        filename = stream.default_filename
        filename_with_resolution = f"{os.path.splitext(filename)[0]}-{resolution}{os.path.splitext(filename)[1]}"
        file_path = os.path.join(save_dir, filename_with_resolution)
        if os.path.exists(file_path):
            new_filename = simpledialog.askstring(
                "Rename File",
                "A file with this name already exists. Please enter a new filename:",
                initialvalue=filename_with_resolution,
            )
            if new_filename is None:
                return
            filename_with_resolution = new_filename
        stream.download(output_path=save_dir, filename=filename_with_resolution)
        status_label.configure(text=f"File saved as: {filename_with_resolution}")
        to_main_menu()
    except Exception:
        status_label.configure(
            text=f"Error, resolution selected doesn't exist for video ...",
            text_color="red",
        )
        app.after(2000, hide_labels)

''' Function while the download is in progress '''
def on_progress(stream, chunk, bytes_remaining):
    global start_time, bytes_downloaded_prev, download_button, output_path, download_audio_button
    download_button.configure(state="disabled")
    download_audio_button.configure(state="disabled")
    resolutions_button.configure(state="disabled")
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percentage = (bytes_downloaded / total_size) * 100
    download_finished = bytes_downloaded == total_size
    to_main_menu()
    if download_finished:
        download_button.configure(text="Download Complete!", border_color="#00d11c")
        download_audio_button.configure(text="Download Complete!", border_color="#00d11c")
        app.after(3000, hide_labels)
    else:
        download_button.configure(text=f"Downloading ... {int(progress_percentage)}%", border_color="yellow")
        download_audio_button.configure(text=f"Downloading ... {int(progress_percentage)}%", border_color="yellow")
        current_time = time.time()
        time_elapsed = current_time - start_time
        bytes_downloaded_since_last = bytes_downloaded - bytes_downloaded_prev
        download_speed = (bytes_downloaded_since_last / time_elapsed / 1_000_000)  
        start_time = current_time
        bytes_downloaded_prev = bytes_downloaded
        progress_label.configure(
            text="{} / {} Download Speed: {:.2f} MB/sec".format(
                bytes_to_nearest_measurement(int(bytes_downloaded)),
                bytes_to_nearest_measurement(int(total_size)),
                download_speed,
            )
        )
        progress_label.update()
        status_label.configure(text=f"Saving to local location ... {output_path}")
        to_main_menu()

''' Function to ask for confirmation before closing the window '''
def on_close():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to close the application?"):
        app.destroy()

''' Function convert video to audio '''
def convert_video_to_audio():
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select Video File",
        filetypes=(("Video files", "*.mp4 *.avi *.mkv"), ("all files", "*.*")),
    )
    if filename:
        convert_to_audio(filename)

''' Generic Function that runs all the 
audio convertors with same information '''
def convert_audio_file(filetypes, conversion_function):
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select Audio File",
        filetypes=filetypes
    )
    if filename:
        conversion_function(filename)

''' Conversion functions using the generic function '''
def convert_flac_to_mp3():
    convert_audio_file([("Audio files", "*.flac"), ("all files", "*.*")], flac_to_mp3.convert)

def convert_flac_to_wav():
    convert_audio_file([("Audio files", "*.flac"), ("all files", "*.*")], flac_to_wav.convert)

def convert_flac_to_wma():
    convert_audio_file([("Audio files", "*.flac"), ("all files", "*.*")], flac_to_wma.convert)

def convert_mp3_to_flac():
    convert_audio_file([("Audio files", "*.mp3"), ("all files", "*.*")], mp3_to_flac.convert)

def convert_mp3_to_wav():
    convert_audio_file([("Audio files", "*.mp3"), ("all files", "*.*")], mp3_to_wav.convert)

def convert_mp3_to_wma():
    convert_audio_file([("Audio files", "*.mp3"), ("all files", "*.*")], mp3_to_wma.convert)

def convert_wav_to_flac():
    convert_audio_file([("Audio files", "*.wav"), ("all files", "*.*")], wav_to_flac.convert)

def convert_wav_to_mp3():
    convert_audio_file([("Audio files", "*.wav"), ("all files", "*.*")], wav_to_mp3.convert)

def convert_wav_to_wma():
    convert_audio_file([("Audio files", "*.wav"), ("all files", "*.*")], wav_to_wma.convert)

def convert_wma_to_flac():
    convert_audio_file([("Audio files", "*.wma"), ("all files", "*.*")], wma_to_flac.convert)

def convert_wma_to_mp3():
    convert_audio_file([("Audio files", "*.wma"), ("all files", "*.*")], wma_to_mp3.convert)

def convert_wma_to_wav():
    convert_audio_file([("Audio files", "*.wma"), ("all files", "*.*")], wma_to_wav.convert)

''' Function to convert video to audio '''
def convert_to_audio(video_file):
    global progress_label, status_label
    progress_label.pack(pady="10p")
    status_label.pack(pady="10p")
    audio_file = video_file.replace(".mp4", ".mp3")
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)
    video.close()
    progress_label.configure(text=f"File saved as: {audio_file}")
    status_label.configure(text=f"File saved as: {audio_file}")
    to_main_menu()
    
''' Function for donation window '''
def open_donation_window():
    donation_window = ctk.CTk()
    donation_window.title("Please Donate ...")
    new_width = int(min_max_width // 1.25)
    new_height = int(min_max_height // 1.85)
    donation_window.geometry(f"{new_width}x{new_height}")
    donation_window.minsize(new_width, new_height)
    donation_window.maxsize(new_width, new_height)
    donation_window.iconbitmap(icon)

    ''' Create a frame to hold the content '''
    donation_frame = ctk.CTkFrame(donation_window)
    donation_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    ''' Create a label with the donation message '''
    donation_label = ctk.CTkLabel(
        donation_frame,
        text="Enjoy using our app?? \nWould you like us to keep it well maintained? \n\nThen making a donation to one of our following wallets, \nwould help us out and would be greatly appreciated.",
        font=("calibri", 18),
    )
    donation_label.pack(padx=10, pady=10)

    ''' Define wallet addresses and labels '''
    wallets = [
        {"name": "BTC", "address": "12pGQNkdk8C3H32GBtUzXjxgZvxVZLRxsB"},
        {"name": "ETH", "address": "0x7801af1b2acd60e56f9bf0d5039beb3d99ba8bc4"},
        {"name": "DOGE", "address": "D6TE4ZgBfjJ1neYztZFQWiihPZNBS418P5"},
    ]

    ''' Function to copy wallet address to clipboard '''
    def copy_address(name, address):
        pyperclip.copy(address)
        copied_label.configure(
            text=f"\n{name} address copied to clipboard\n\n{address}"
        )
        copied_label.pack()
        copied_label.after(2000, copied_label.pack_forget)

    ''' Create a frame for the buttons to align them properly '''
    button_frame = ctk.CTkFrame(donation_frame)
    button_frame.pack(pady=10)

    ''' Create buttons to copy wallet addresses '''
    for i, wallet in enumerate(wallets):
        copy_button = ctk.CTkButton(
            button_frame,
            text=f"{wallet['name']} Wallet Address",
            command=lambda name=wallet["name"], addr=wallet["address"]: copy_address(
                name, addr
            ),
            **main_button_config
        )
        copy_button.grid(row=0, column=i, padx=5, pady=5)

    ''' Label to display "Copied to Clipboard" message '''
    copied_label = ctk.CTkLabel(donation_frame, text="")
    copied_label.pack(pady=5)

    ''' Start the donation window's main loop '''
    donation_window.mainloop()

''' Hide the labels after 3 seconds '''
def hide_labels():
    global resolutions_var
    # resolutions_var.set("")
    status_label.pack_forget()
    progress_label.pack_forget()
    resolutions_button.pack_forget()
    download_button.configure(state="normal")
    download_button.configure(text="Download Another Video", command=start_app_again)
    download_audio_button.configure(state="normal")
    download_audio_button.configure(text="Download Another Song", command=download_audio_only)
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    convert_to_audio_button.pack(pady=10)
    to_main_menu()

''' Function to print all available resolutions for a YouTube video '''
def print_available_resolutions(url):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter()
        resolutions = sorted(
            set([stream.resolution for stream in streams if stream.resolution]),
            key=lambda x: int(x[:-1]),
        )
        resolutions_var = ctk.StringVar()
        ''' Function to handle resolution selection '''
        def select_resolution(resolution):
            resolutions_var.set(resolution)
        ''' Create a frame to hold the resolution buttons '''
        selected_resolution = ctk.StringVar()
        resolutions_frame.pack(pady=10)
        ''' Create a radio button for each available resolution '''
        for i, resolution in enumerate(resolutions):
            button = ctk.CTkRadioButton(
                resolutions_frame,
                text=resolution,
                variable=selected_resolution,
                value=resolution,
                command=lambda: select_resolution(selected_resolution.get()),
                width=2,
                height=2,
            )
            button.grid(row=0, column=i, padx=5, pady=5)
            to_main_menu()
        return resolutions_var
    except Exception as e:
        print(f"Error fetching resolutions for URL {url}: {e}")

''' Function to load the resolutions for a YouTube video '''
def load_resolutions():
    global resolutions_var
    url = entry_url.get().strip()
    youtube_url_pattern = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$"
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube video URL.")
    elif not re.match(youtube_url_pattern, url):
        messagebox.showerror("Error", "Please enter a valid YouTube video URL.")
    else:
        resolutions_var = print_available_resolutions(url)
        download_button.pack(pady=10)
        to_main_menu()

''' Function to start a new download '''
def start_app_again():
    global resolutions_var
    resolutions_var.set("")
    download_button.pack_forget()
    convert_to_audio_button.pack_forget()
    resolutions_button.configure(state="normal")
    resolutions_button.configure(text="Load Resolutions", command=load_resolutions)
    resolutions_button.pack(pady=10)
    download_button.configure(text="Download", command=lambda: download_video(resolutions_var))
    to_main_menu()

''' Calculate the nearest measurement for bytes '''
def bytes_to_nearest_measurement(bytes):
    for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024

''' Function to load entry widget for the video url and resolutions button '''
def load_entry_and_resolutions_button():
    global entry_url, resolutions_button, resolutions_frame, download_button, convert_to_audio_button
    youtube_menu_frame.pack_forget()
    resolutions_button.pack_forget()
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    download_button.pack_forget()
    convert_to_audio_button.pack_forget()
    want_to_download_audio_button.pack_forget()
    entry_url.pack(pady=10)
    resolutions_button.pack(pady="10p")
    main_menu_frame.pack_forget()
    want_to_download_button.pack_forget()
    want_to_convert_to_audio_button.pack_forget()
    to_main_menu()

''' function to download audio file only '''
def download_audio_only():
    global entry_url, resolutions_button, resolutions_frame, download_button, convert_to_audio_button
    youtube_menu_frame.pack_forget()
    resolutions_button.pack_forget()
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    download_button.pack_forget()
    convert_to_audio_button.pack_forget()
    entry_url.pack(pady=10)
    download_audio_button.configure(text="Download", command=download_audio)
    download_audio_button.pack(pady=10)
    main_menu_frame.pack_forget()
    want_to_download_button.pack_forget()
    want_to_convert_to_audio_button.pack_forget()
    to_main_menu()

''' Function to show all the available convertors '''
def show_converters():
    hide_all_buttons()
    hide_footer_frame()
    convertors_frame.pack(padx=10, pady=90)
    want_to_convert_to_audio_button.grid(row=0, column=1, padx=5, pady=5)
    convert_mp3_to_flac_button.grid(row=1, column=0, padx=5, pady=5)
    convert_mp3_to_wav_button.grid(row=1, column=1, padx=5, pady=5)
    convert_mp3_to_wma_button.grid(row=1, column=2, padx=5, pady=5)
    convert_flac_to_mp3_button.grid(row=2, column=0, padx=5, pady=5)
    convert_flac_to_wav_button.grid(row=2, column=1, padx=5, pady=5)
    convert_flac_to_wma_button.grid(row=2, column=2, padx=5, pady=5)
    convert_wav_to_mp3_button.grid(row=3, column=0, padx=5, pady=5)
    convert_wav_to_flac_button.grid(row=3, column=1, padx=5, pady=5)
    convert_wav_to_wma_button.grid(row=3, column=2, padx=5, pady=5)
    convert_wma_to_mp3_button.grid(row=4, column=0, padx=5, pady=5)
    convert_wma_to_flac_button.grid(row=4, column=1, padx=5, pady=5)
    convert_wma_to_wav_button.grid(row=4, column=2, padx=5, pady=5)
    to_main_menu()

''' Function to show all the available convertors '''
def hide_converters():
    hide_all_buttons()
    hide_footer_frame()
    convertors_frame.pack_forget()

''' Function to show the download buttons available '''
def show_youtube_downloader():
    hide_all_buttons()
    hide_footer_frame()
    youtube_menu_frame.pack(padx=10, pady=130)
    want_to_download_button.grid(row=0, column=0, padx=5, pady=5)
    want_to_download_audio_button.grid(row=0, column=1, padx=5, pady=5)
    to_main_menu()

def hide_all_buttons():
    main_menu_frame.pack_forget()

def back_to_main_menu():
    hide_all_buttons()
    hide_footer_frame()
    back_to_menu_frame.pack_forget()
    convertors_frame.pack_forget()
    youtube_menu_frame.pack_forget()
    resolutions_button.pack_forget()
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    entry_url.pack_forget()
    download_button.pack_forget()
    convert_to_audio_button.pack_forget()
    want_to_download_audio_button.pack_forget()
    want_to_download_button.pack_forget()
    want_to_convert_to_audio_button.pack_forget()
    download_audio_button.pack_forget()
    main_menu_frame.pack(padx=10, pady=130)
    footer_frame.pack(side="bottom", pady=10)

''' Function to go back to the main menu screen '''
def to_main_menu():
    back_to_menu_frame.pack(side='bottom', pady=10)
    back_to_menu_button.pack(pady=5)

''' Function to hide buttons at bottom of screen '''
def hide_footer_frame():
    footer_frame.pack_forget()
    website_button.pack_forget()
    donation_button.pack_forget()

''' Create a app window '''
app = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(custom_theme)

''' Title of the window '''
app.title(app_name)
app.iconbitmap(icon)

''' Set min and max width and height '''
min_max_height = 550
min_max_width = 650
app.geometry(f"{min_max_width}x{min_max_height}")
app.minsize(min_max_width, min_max_height)
app.maxsize(min_max_width, min_max_height)

''' Create a frame to hold the content '''
main_frame = ctk.CTkFrame(app)
main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

''' Define global variables to track download progress '''
start_time = time.time()
bytes_downloaded_prev = 0

''' Create a label and the entry widget for the video url '''
pil_image = Image.open(logo)
logo_image = ctk.CTkImage(pil_image, size=(250, 60))
heading = ctk.CTkLabel(main_frame, image=logo_image, text="")
heading.pack(pady="10p")

''' Initialize the main frame '''
main_menu_frame = ctk.CTkFrame(main_frame)
main_menu_frame.pack(padx=10, pady=130)

''' Custom definitions for start menu only '''
main_menu_font = ctk.CTkFont(family="calibri", size=17, weight="normal")
main_menu_color = "orange"
main_menu_height = 50
main_menu_width = 150
main_menu_corner_radius = 33
main_menu_button_config = {
    'font': main_menu_font,
    'height': main_menu_height,
    'width': main_menu_width,
    'border_color': main_menu_color,
    'corner_radius': main_menu_corner_radius
}

''' Buttons for opening the sub-menus '''
converters_button = ctk.CTkButton(main_menu_frame, text="Convert", command=show_converters, **main_menu_button_config)
youtube_downloader_button = ctk.CTkButton(main_menu_frame, text="Download", command=show_youtube_downloader, **main_menu_button_config)
youtube_downloader_button.grid(row=0, column=0, padx=5, pady=5)
converters_button.grid(row=0, column=1, padx=5, pady=5)

''' Initialize the main frame '''
footer_frame = ctk.CTkFrame(main_frame)
footer_frame.pack(side="bottom", pady=10)

''' Custom definitions for start menu only '''
footer_font = ctk.CTkFont(family="calibri", size=13, weight="normal")
footer_menu_color = "red"
footer_menu_height = 25
footer_menu_width = 75
footer_corner_radius = 33
footer_config = {
    'font': footer_font,
    'height': footer_menu_height,
    'width': footer_menu_width,
    'border_color': footer_menu_color,
    'corner_radius': footer_corner_radius
}

''' Bottom of the main screen donation and website buttons '''
website_button = ctk.CTkButton(footer_frame, text="Website", command=lambda: open_webpage(website_url), **footer_config)
feedback_button = ctk.CTkButton(footer_frame, text="Feedback", command=open_feedback_email, **footer_config)
github_button = ctk.CTkButton(footer_frame, text="GitHub", command=lambda: open_webpage(github_url), **footer_config)
discord_button = ctk.CTkButton(footer_frame, text="Discord", command=lambda: open_webpage(discord_link), **footer_config)
donation_button = ctk.CTkButton(footer_frame, text="Donate", command=open_donation_window, **footer_config)
website_button.grid(row=0, column=0, padx=5, pady=5)
feedback_button.grid(row=0, column=1, padx=5, pady=5)
github_button.grid(row=0, column=2, padx=5, pady=5)
discord_button.grid(row=0, column=3, padx=5, pady=5)
donation_button.grid(row=0, column=4, padx=5, pady=5)

''' Custom definitions for convertor menu '''
convertors_font = ctk.CTkFont(family="Calibri", size=13, weight="normal")
convertors_menu_color = "green"
convertors_menu_height = 30
convertors_menu_width = 90
convertors_corner_radius = 33
convertors_button_config = {
    'font': convertors_font,
    'height': convertors_menu_height,
    'width': convertors_menu_width,
    'border_color': convertors_menu_color,
    'corner_radius': convertors_corner_radius
}

''' Youtube menu frame '''
youtube_menu_frame = ctk.CTkFrame(main_frame)

''' Define all the other buttons for YouTube menu '''
want_to_download_button = ctk.CTkButton(youtube_menu_frame, text="Download Video", command=load_entry_and_resolutions_button, **convertors_button_config)
want_to_download_audio_button = ctk.CTkButton(youtube_menu_frame, text="Download Audio", command=download_audio_only, **convertors_button_config)

''' Convertor Frame '''
convertors_frame = ctk.CTkFrame(main_frame)

''' Define all the other buttons for Converter menu '''
want_to_convert_to_audio_button = ctk.CTkButton(convertors_frame, text="Video to Audio (mp3)", command=convert_video_to_audio, **convertors_button_config)
convert_mp3_to_flac_button = ctk.CTkButton(convertors_frame, text="MP3 to FLAC", command=convert_mp3_to_flac, **convertors_button_config)
convert_mp3_to_wav_button = ctk.CTkButton(convertors_frame, text="MP3 to WAV", command=convert_mp3_to_wav, **convertors_button_config)
convert_mp3_to_wma_button = ctk.CTkButton(convertors_frame, text="MP3 to WMA", command=convert_mp3_to_wma, **convertors_button_config)
convert_flac_to_mp3_button = ctk.CTkButton(convertors_frame, text="FLAC to MP3", command=convert_flac_to_mp3, **convertors_button_config)
convert_flac_to_wav_button = ctk.CTkButton(convertors_frame, text="FLAC to WAV", command=convert_flac_to_wav, **convertors_button_config)
convert_flac_to_wma_button = ctk.CTkButton(convertors_frame, text="FLAC to WMA", command=convert_flac_to_wma, **convertors_button_config)
convert_wav_to_mp3_button = ctk.CTkButton(convertors_frame, text="WAV to MP3", command=convert_wav_to_mp3, **convertors_button_config)
convert_wav_to_flac_button = ctk.CTkButton(convertors_frame, text="WAV to FLAC", command=convert_wav_to_flac, **convertors_button_config)
convert_wav_to_wma_button = ctk.CTkButton(convertors_frame, text="WAV to WMA", command=convert_wav_to_wma, **convertors_button_config)
convert_wma_to_mp3_button = ctk.CTkButton(convertors_frame, text="WMA to MP3", command=convert_wma_to_mp3, **convertors_button_config)
convert_wma_to_flac_button = ctk.CTkButton(convertors_frame, text="WMA to FLAC", command=convert_wma_to_flac, **convertors_button_config)
convert_wma_to_wav_button = ctk.CTkButton(convertors_frame, text="WMA to WAV", command=convert_wma_to_wav, **convertors_button_config)

''' Custom definitions for main menu button only '''
main_menu_font = ctk.CTkFont(family="calibri", size=15, weight="normal")
main_menu_color = "blue"
main_menu_height = 33
main_menu_width = 99
main_corner_radius = 33
main_button_config = {
    'font': main_menu_font,
    'height': main_menu_height,
    'width': main_menu_width,
    'border_color': main_menu_color,
    'corner_radius': main_corner_radius
}

''' Create a button to always get the user back to the main menu '''
back_to_menu_frame = ctk.CTkFrame(main_frame)
back_to_menu_button = ctk.CTkButton(back_to_menu_frame, text="Main Menu", command=back_to_main_menu, **main_button_config)

''' Create a label and the entry widget for the video url '''
entry_url = ctk.CTkEntry(main_frame, width=390, placeholder_text=("Paste URL here..."))

''' Create a resolutions frame to hold the resolutions '''
resolutions_frame = ctk.CTkFrame(main_frame)

''' Create a download button '''
download_button = ctk.CTkButton(main_frame, text="Download", command=lambda: download_video(resolutions_var))

''' Create a download audio button '''
download_audio_button = ctk.CTkButton(main_frame, text="Download", command=download_audio)

''' Create a resolutions button '''
resolutions_button = ctk.CTkButton(main_frame, text="Load Resolutions", command=load_resolutions)

''' Define resolutions_var globally '''
resolutions_var = None

''' Create and position GUI elements '''
convert_to_audio_button = ctk.CTkButton(main_frame, text="Convert Video 2 Audio", command=convert_video_to_audio)

''' Create a label and the progress bar to display the download progress '''
progress_label = ctk.CTkLabel(main_frame, text="")

''' Create the status label '''
status_label = ctk.CTkLabel(main_frame, text="")

''' Add the on_close function to the close button '''
app.protocol("WM_DELETE_WINDOW", on_close)

''' Start the app '''
if __name__ == "__main__":
    app.mainloop()
