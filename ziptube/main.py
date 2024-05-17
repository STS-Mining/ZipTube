# Author: STS-Mining
# ZipTube Version 1.21
# Download YouTube videos, audio and convert videos to audio

import customtkinter as ctk
from pytube import YouTube
import time
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
import pyperclip
from PIL import Image
import os
import re
from tkinter import filedialog
import moviepy.editor as mp
from pydub import AudioSegment

# Icon and logo location on system
icon = "ziptube/assets/images/icon.ico"
logo = "ziptube/assets/images/logo.png"

# Save location for all files downloaded
def choose_save_location():
    save_location = filedialog.askdirectory()
    return save_location


# Function to download only audio files
def download_audio():
    global download_audio_button, output_path
    url = entry_url.get()
    # Regular expression pattern to match YouTube URLs
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
            # This is the directory where the file will be saved
            save_dir = choose_save_location()
            output_path = save_dir
            # Get the filename with extension
            filename = audio_stream.default_filename
            # Rename file to mp3 from mp4
            filename = filename.replace(".mp4", ".mp3")
            # Check if the file already exists
            file_path = os.path.join(save_dir, filename)
            if os.path.exists(file_path):
                # Ask the user to enter a new filename
                new_filename = simpledialog.askstring(
                    "Rename File",
                    "A file with this name already exists. Please enter a new filename:",
                    initialvalue=filename,
                )
                if new_filename is None:
                    # User canceled renaming, so stop the download process
                    return
            # Download the file with the modified filename
            audio_stream.download(output_path=save_dir, filename=filename)
            status_label.configure(text=f"File saved as: {filename}")
        except Exception:
            status_label.configure(
                text=f"Error, Audio selected can't be downloaded ...",
                text_color="red",
            )
            # Schedule hiding labels after 2 seconds
            app.after(2000, hide_labels)


# Function that downloads the video once the download button is pressed
def download_video(resolutions_var):
    global download_button, output_path
    url = entry_url.get()
    resolution = resolutions_var.get()
    if not resolution:  # Check if resolution is not selected
        messagebox.showerror("Error", "Please select a resolution.")
        return

    progress_label.pack(pady="10p")
    status_label.pack(pady="10p")
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(res=resolution).first()
        # This is the directory where the file will be saved
        save_dir = choose_save_location()
        output_path = save_dir
        # Get the filename with extension
        filename = stream.default_filename
        # Append resolution to the filename
        filename_with_resolution = f"{os.path.splitext(filename)[0]}-{resolution}{os.path.splitext(filename)[1]}"
        # Check if the file already exists
        file_path = os.path.join(save_dir, filename_with_resolution)
        if os.path.exists(file_path):
            # Ask the user to enter a new filename
            new_filename = simpledialog.askstring(
                "Rename File",
                "A file with this name already exists. Please enter a new filename:",
                initialvalue=filename_with_resolution,
            )
            if new_filename is None:
                # User canceled renaming, so stop the download process
                return
            filename_with_resolution = new_filename
        # Download the file with the modified filename
        stream.download(output_path=save_dir, filename=filename_with_resolution)
        status_label.configure(text=f"File saved as: {filename_with_resolution}")
    except Exception:
        status_label.configure(
            text=f"Error, resolution selected doesn't exist for video ...",
            text_color="red",
        )
        # Schedule hiding labels after 2 seconds
        app.after(2000, hide_labels)


# Function while the download is in progress
def on_progress(stream, chunk, bytes_remaining):
    global start_time, bytes_downloaded_prev, download_button, donation_button, output_path, download_audio_button
    download_button.configure(state="disabled")  # Disable the download button
    download_audio_button.configure(state="disabled")  # Disable the download button
    resolutions_button.configure(state="disabled")  # Disable the resolutions button
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percentage = (bytes_downloaded / total_size) * 100
    download_finished = bytes_downloaded == total_size
    donation_button.pack(pady="10p")
    if download_finished:
        download_button.configure(text="Download Complete!", border_color="#00d11c")
        download_audio_button.configure(
            text="Download Complete!", border_color="#00d11c"
        )
        # Schedule hiding labels after 3 seconds
        app.after(3000, hide_labels)
    else:
        download_button.configure(
            text=f"Downloading ... {int(progress_percentage)}%", border_color="yellow"
        )
        download_audio_button.configure(
            text=f"Downloading ... {int(progress_percentage)}%", border_color="yellow"
        )
        current_time = time.time()
        time_elapsed = current_time - start_time
        bytes_downloaded_since_last = bytes_downloaded - bytes_downloaded_prev
        download_speed = (
            bytes_downloaded_since_last / time_elapsed / 1_000_000
        )  # Convert to Mbps
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


# Function to ask for confirmation before closing the window
def on_close():
    if messagebox.askokcancel(
        "Confirmation", "Are you sure you want to close the application?"
    ):
        # Close the app
        app.destroy()


# Function for the window for renaming the file
def rename_file(filename_with_resolution):
    rename_file_window = ctk.CTk()
    rename_file_window.title("Rename File")
    rename_file_window.geometry("600x150")
    rename_file_window.minsize(600, 150)
    rename_file_window.maxsize(600, 150)
    rename_file_window.iconbitmap(icon)
    rename_file_label = ctk.CTkLabel(
        rename_file_window,
        text="A file with this name already exists. Please enter a new filename:",
        initialvalue=filename_with_resolution,
    )
    rename_file_label.pack(padx="10p", pady="10p")
    rename_file_window.mainloop()


# Function to open window on users pc
def open_file_dialog():
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select Video File",
        filetypes=(("Video files", "*.mp4 *.avi *.mkv"), ("all files", "*.*")),
    )
    if filename:
        convert_to_audio(filename)


# Function to convert video to audio
def convert_to_audio(video_file):
    global progress_label, status_label
    progress_label.pack(pady="10p")
    status_label.pack(pady="10p")
    audio_file = video_file.replace(".mp4", ".mp3")  # Change extension to mp3
    video = mp.VideoFileClip(video_file)
    video.audio.write_audiofile(audio_file)
    video.close()
    progress_label.configure(text=f"File saved as: {audio_file}")
    status_label.configure(text=f"File saved as: {audio_file}")

# def convert_to_audio(mp3_file):
#     global progress_label, status_label
#     progress_label.pack(pady="10p")
#     status_label.pack(pady="10p")
#     flac_file = mp3_file.replace(".mp3", ".flac")  # Change extension to flac
#     audio = AudioSegment.from_mp3(mp3_file)
#     audio.export(flac_file, format="flac")
#     progress_label.configure(text=f"File saved as: {flac_file}")
#     status_label.configure(text=f"File saved as: {flac_file}")

# Function for donation window
def open_donation_window():
    donation_window = ctk.CTk()
    donation_window.title("Notification")
    donation_window.geometry("600x360")
    donation_window.minsize(600, 360)
    donation_window.maxsize(720, 480)
    donation_window.iconbitmap(icon)

    # Create a label with the donation message
    donation_label = ctk.CTkLabel(
        donation_window,
        text="Enjoy using our app?? \nWould you like us to keep it well maintained? \n\nThen making a donation to one of our following wallets, \nwould help us out and would be greatly appreciated.",
        font=("Helvetica", 18),
    )
    donation_label.pack(padx=10, pady=10)

    # Define wallet addresses and labels
    wallets = [
        {"name": "BTC", "address": "12pGQNkdk8C3H32GBtUzXjxgZvxVZLRxsB"},
        {"name": "ETH", "address": "0x7801af1b2acd60e56f9bf0d5039beb3d99ba8bc4"},
        {"name": "DOGE", "address": "D6TE4ZgBfjJ1neYztZFQWiihPZNBS418P5"},
    ]

    # Function to copy wallet address to clipboard
    def copy_address(name, address):
        pyperclip.copy(address)
        copied_label.configure(
            text=f"\n{name} Address Copied to Clipboard\n\n{address}"
        )
        copied_label.pack()
        copied_label.after(2000, copied_label.pack_forget)

    # Create buttons to copy wallet addresses
    for wallet in wallets:
        copy_button = ctk.CTkButton(
            donation_window,
            text=f"{wallet['name']} Address",
            command=lambda name=wallet["name"], addr=wallet["address"]: copy_address(
                name, addr
            ),
        )
        copy_button.pack(pady=5)

    # Label to display "Copied to Clipboard" message
    copied_label = ctk.CTkLabel(donation_window, text="")
    copied_label.pack(pady=5)

    # Start the donation window's main loop
    donation_window.mainloop()


# Hide the labels after 3 seconds
def hide_labels():
    global resolutions_var
    # resolutions_var.set("")  # Clear the resolutions variable
    status_label.pack_forget()  # Hide the status label
    progress_label.pack_forget()  # Hide the progress label
    resolutions_button.pack_forget()  # Hide the resolutions button
    cancel_button.pack_forget()  # Hide the cancel button
    download_button.configure(state="normal")  # Enable the download button
    download_button.configure(text="Download Another Video", command=start_app_again)
    download_audio_button.configure(state="normal")  # Enable the download button
    download_audio_button.configure(
        text="Download Another Song", command=download_audio_only
    )
    donation_button.pack_forget()  # Hide the donation button
    resolutions_frame.pack_forget()  # Hide the resolutions frame
    entry_url.delete(0, ctk.END)  # Clear the entry URL
    donation_button.pack(pady="10p")  # Show the donation button
    convert_to_audio_button.pack(pady=10)  # Show the convert to audio button


# Function to print all available resolutions for a YouTube video
def print_available_resolutions(url):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter()
        resolutions = sorted(
            set([stream.resolution for stream in streams if stream.resolution]),
            key=lambda x: int(x[:-1]),
        )
        resolutions_var = ctk.StringVar()

        # Function to handle resolution selection
        def select_resolution(resolution):
            resolutions_var.set(resolution)

        # Create a frame to hold the resolution buttons
        selected_resolution = ctk.StringVar()
        resolutions_frame.pack(pady=10)

        # Create a radio button for each available resolution
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

        return resolutions_var
    except Exception as e:
        print(f"Error fetching resolutions for URL {url}: {e}")


# Function to load the resolutions for a YouTube video
def load_resolutions():
    global resolutions_var
    url = entry_url.get().strip()  # Get the URL and remove leading/trailing whitespace

    # Regular expression pattern to match YouTube video URLs
    youtube_url_pattern = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+$"

    if not url:
        messagebox.showerror("Error", "Please enter a YouTube video URL.")
    elif not re.match(youtube_url_pattern, url):
        messagebox.showerror("Error", "Please enter a valid YouTube video URL.")
    else:
        # Call print_available_resolutions to print available resolutions
        resolutions_var = print_available_resolutions(url)
        download_button.pack(pady=10)
        cancel_button.pack(pady=10)


# Function to start a new download
def start_app_again():
    global resolutions_var
    resolutions_var.set("")  # Clear the resolutions variable
    donation_button.pack_forget()  # Hide the donation button
    download_button.pack_forget()  # Hide the download button
    convert_to_audio_button.pack_forget()  # Hide the convert to audio button
    resolutions_button.configure(state="normal")  # Enable the resolutions button
    resolutions_button.configure(text="Load Resolutions", command=load_resolutions)
    resolutions_button.pack(pady=10)  # Show the resolutions button
    download_button.configure(
        text="Download", command=lambda: download_video(resolutions_var)
    )


# Calculate the nearest measurement for bytes
def bytes_to_nearest_measurement(bytes):
    megabytes = bytes / (1024 * 1024)
    gigabytes = bytes / (1024 * 1024 * 1024)
    if gigabytes >= 1:
        return "{} GB".format(round(gigabytes))
    else:
        return "{} MB".format(round(megabytes))


# Function to load entry widget for the video url and resolutions button
def load_entry_and_resolutions_button():
    global entry_url, resolutions_button, resolutions_frame, download_button, cancel_button, convert_to_audio_button
    resolutions_button.pack_forget()  # Hide the resolutions button
    resolutions_frame.pack_forget()  # Hide the resolutions frame
    entry_url.delete(0, ctk.END)  # Clear the entry URL
    donation_button.pack_forget()  # Hide the donation button
    download_button.pack_forget()  # Hide the download button
    convert_to_audio_button.pack_forget()  # Hide the convert to audio button
    cancel_button.pack_forget()  # Hide the cancel button
    entry_url.pack(pady=10)  # Show the entry URL
    resolutions_button.pack(pady="10p")  # Show the resolutions button
    start_menu_frame.pack_forget()  # Hide the start menu frame
    want_to_download_button.pack_forget()  # Hide the want to download button
    want_to_convert_to_audio_button.pack_forget()  # Hide the want to convert to audio button


# function to download audio file only
def download_audio_only():
    global entry_url, resolutions_button, resolutions_frame, download_button, cancel_button, convert_to_audio_button
    resolutions_button.pack_forget()  # Hide the resolutions button
    resolutions_frame.pack_forget()  # Hide the resolutions frame
    entry_url.delete(0, ctk.END)  # Clear the entry URL
    donation_button.pack_forget()  # Hide the donation button
    download_button.pack_forget()  # Hide the download button
    convert_to_audio_button.pack_forget()  # Hide the convert to audio button
    cancel_button.pack_forget()  # Hide the cancel button
    entry_url.pack(pady=10)  # Show the entry URL
    download_audio_button.configure(text="Download", command=download_audio)
    download_audio_button.pack(pady=10)
    start_menu_frame.pack_forget()  # Hide the start menu frame
    want_to_download_button.pack_forget()  # Hide the want to download button
    want_to_convert_to_audio_button.pack_forget()  # Hide the want to convert to audio button


# Create a app window
app = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("custom")

# Title of the window
app.title("ZipTube")
app.iconbitmap(icon)

# Set min and max width and height
min_max_height = 550
min_max_width = 650
app.geometry(f"{min_max_width}x{min_max_height}")
app.minsize(min_max_width, min_max_height)
app.maxsize(min_max_width, min_max_height)

# Create a frame to hold the content
content_frame = ctk.CTkFrame(app)
content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

# Define global variables to track download progress
start_time = time.time()
bytes_downloaded_prev = 0

# Create a label and the entry widget for the video url
pil_image = Image.open(logo)
logo_image = ctk.CTkImage(pil_image, size=(250, 60))
heading = ctk.CTkLabel(content_frame, image=logo_image, text="")
heading.pack(pady="10p")

# Create new buttons as a start menu
start_menu_frame = ctk.CTkFrame(content_frame)
start_menu_frame.pack(padx=10, pady=150)
want_to_download_button = ctk.CTkButton(
    start_menu_frame, text="Download Video", command=load_entry_and_resolutions_button
)
download_audio_button = ctk.CTkButton(
    start_menu_frame, text="Download Audio", command=download_audio_only
)
want_to_convert_to_audio_button = ctk.CTkButton(
    start_menu_frame, text="Convert Video 2 Audio", command=open_file_dialog
)
want_to_download_button.grid(row=0, column=0, padx=5, pady=5)
download_audio_button.grid(row=0, column=1, padx=5, pady=5)
want_to_convert_to_audio_button.grid(row=0, column=2, padx=5, pady=5)

# Create a label and the entry widget for the video url
entry_url = ctk.CTkEntry(
    content_frame, width=390, placeholder_text=("Paste URL here...")
)

# Create a resolutions frame to hold the resolutions
resolutions_frame = ctk.CTkFrame(content_frame)

# Create a download button
download_button = ctk.CTkButton(
    content_frame, text="Download", command=lambda: download_video(resolutions_var)
)

# Create a download audio button
download_audio_button = ctk.CTkButton(
    content_frame, text="Download", command=download_audio
)

# Create a resolutions button
resolutions_button = ctk.CTkButton(
    content_frame, text="Load Resolutions", command=load_resolutions
)

# Define resolutions_var globally
resolutions_var = None

# Create a cancel button
cancel_button = ctk.CTkButton(content_frame, text="Cancel / Clear", command=hide_labels)

# Create and position GUI elements
convert_to_audio_button = ctk.CTkButton(
    content_frame, text="Convert Video 2 Audio", command=open_file_dialog
)

# Create a label and the progress bar to display the download progress
progress_label = ctk.CTkLabel(content_frame, text="")

# Create the status label
status_label = ctk.CTkLabel(content_frame, text="")

# Create a donate button
donation_button = ctk.CTkButton(
    content_frame, text="Donate", command=open_donation_window
)

# Add the on_close function to the close button
app.protocol("WM_DELETE_WINDOW", on_close)

# Start the app
if __name__ == "__main__":
    app.mainloop()
