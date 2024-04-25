# Author: STS-Mining
# Version 1.11

import customtkinter as ctk
from pytube import YouTube
import time
import tkinter.messagebox as messagebox
import pyperclip
from PIL import Image
import os

def download_video(resolutions_var):
    global download_button, donation_button
    url = entry_url.get()
    resolution = resolutions_var.get()
    progress_label.pack(pady="10p")
    status_label.pack(pady="10p")
    donation_button.pack(pady="10p")
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(res=resolution).first()
        # This is the directory where the file will be saved
        save_dir = os.path.expanduser("~/Downloads")
        # Get the filename with extension
        filename = stream.default_filename
        # Append resolution to the filename
        filename_with_resolution = f"{os.path.splitext(filename)[0]}-{resolution}{os.path.splitext(filename)[1]}"
        # Download the file with the modified filename
        stream.download(output_path=save_dir, filename=filename_with_resolution)
        status_label.configure(text=f"File saved as: {yt.title}-{resolution}")
    except Exception:
        status_label.configure(text=f"Error, resolution selected doesn't exist for video ...", text_color="red")
        # Schedule hiding labels after 10 seconds
        app.after(5000, hide_labels)

def on_progress(stream, chunk, bytes_remaining):
    global start_time, bytes_downloaded_prev, download_button
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percentage = (bytes_downloaded / total_size) * 100
    download_finished = (bytes_downloaded == total_size)
    if download_finished:
        download_button.configure(text="Download Complete!")
        # Schedule hiding labels after 10 seconds
        app.after(10000, hide_labels)
    else:
        download_button.configure(text=f"Downloading ... {int(progress_percentage)}%")
        current_time = time.time()
        time_elapsed = current_time - start_time
        bytes_downloaded_since_last = bytes_downloaded - bytes_downloaded_prev
        download_speed = bytes_downloaded_since_last / time_elapsed / 1_000_000  # Convert to Mbps
        # Update global variables for next iteration
        start_time = current_time
        bytes_downloaded_prev = bytes_downloaded
        progress_label.configure(text="{} of {}\nDownload Speed: {:.2f} MB/sec".format(
                    bytes_to_nearest_measurement(int(bytes_downloaded)),
                    bytes_to_nearest_measurement(int(total_size)),
                    download_speed
                ))
        progress_label.update()
        status_label.configure(text=f"Saving to local Downloads folder ...")


# Function to ask for confirmation before closing the window
def on_close():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to close the application?"):
        # Close the app
        app.destroy()

def open_donation_window():
    donation_window = ctk.CTk()
    donation_window.title("Notification")
    donation_window.geometry("600x360")
    donation_window.minsize(600, 360)
    donation_window.maxsize(720, 480)
    donation_window.iconbitmap("C:/Python/Stuff/youtube/img/pmp.ico")
    # Create a label with the donation message
    donation_label = ctk.CTkLabel(donation_window, text="Enjoy using our app?? \nWould you like us to keep it well maintained? \n\nThen making a donation to one of our following wallets, \nwould help us out and would be greatly appreciated.", font=("Helvetica", 18))
    donation_label.pack(padx=10, pady=10)
    
    # Define wallet addresses and labels
    wallets = [
        {"name": "BTC", "address": "34789bnsjdfhksnfsFSFSfjh4uhrnsjnfjens993"},
        {"name": "ETH", "address": "0x0000000000000000000000000000000000000000"},
        {"name": "DOGE", "address": "9x999999999999999999999999"},
        {"name": "SHIB", "address": "8888888888888888888888888888"}
    ]

    # Function to copy wallet address to clipboard
    def copy_address(name, address):
        pyperclip.copy(address)
        copied_label.configure(text=f"\n{name} Address Copied to Clipboard\n\n{address}")
        copied_label.pack()
        copied_label.after(2000, copied_label.pack_forget)

    # Create buttons to copy wallet addresses
    for wallet in wallets:
        copy_button = ctk.CTkButton(donation_window, text=f"{wallet['name']} Address", command=lambda name=wallet['name'], addr=wallet['address']: copy_address(name, addr))
        copy_button.pack(pady=5)

    # Label to display "Copied to Clipboard" message
    copied_label = ctk.CTkLabel(donation_window, text="")
    copied_label.pack(pady=5)

    # Start the donation window's main loop
    donation_window.mainloop()

def hide_labels():
    status_label.pack_forget()  # Hide the status label
    progress_label.pack_forget()  # Hide the progress label
    download_button.pack_forget()  # Hide the download button
    donation_button.pack_forget()  # Hide the donation button

def bytes_to_nearest_measurement(bytes):
    megabytes = bytes / (1024 * 1024)
    gigabytes = bytes / (1024 * 1024 * 1024)
    if gigabytes >= 1:
        return "{} GB".format(round(gigabytes))
    else:
        return "{} MB".format(round(megabytes))

def print_available_resolutions(url):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter()
        resolutions = sorted(set([stream.resolution for stream in streams if stream.resolution]), key=lambda x: int(x[:-1]))
        resolutions_var = ctk.StringVar()
        print(f"Available Resolutions: {resolutions}")

        # Function to handle resolution selection
        def select_resolution(resolution):
            resolutions_var.set(resolution)
            print(f"Selected resolution: {resolution}")

        selected_resolution = ctk.StringVar()
        resolutions_frame = ctk.CTkFrame(content_frame)
        resolutions_frame.pack(pady=10)

        for i, resolution in enumerate(resolutions):
            button = ctk.CTkRadioButton(resolutions_frame, text=resolution, variable=selected_resolution, value=resolution, command=lambda: select_resolution(selected_resolution.get()), width=2, height=2)
            button.grid(row=0, column=i, padx=5, pady=5)

        return resolutions_var
    except Exception as e:
        print(f"Error fetching resolutions for URL {url}: {e}")

# Function to print all available resolutions for a YouTube video
def load_resolutions():
    global resolutions_var
    # Call print_available_resolutions to print available resolutions
    resolutions_var = print_available_resolutions(entry_url.get())
    download_button.pack(pady=10)

# Create a app window
app = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("custom")

# Title of the window
app.title("ZipTube")
app.iconbitmap("C:/Python/Stuff/youtube/img/icon.ico")

# Set min and max width and the height
app.geometry("620x500")
app.minsize(620, 500)
app.maxsize(620, 500)

# Create a frame to hold the content
content_frame = ctk.CTkFrame(app)
content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

# Define global variables to track download progress
start_time = time.time()
bytes_downloaded_prev = 0

# Create a label and the entry widget for the video url
pil_image = Image.open("C:/Python/Stuff/youtube/img/logo.png")
logo_image = ctk.CTkImage(pil_image, size=(400, 85))
heading = ctk.CTkLabel(content_frame, image=logo_image, text="")
heading.pack(pady="10p")

entry_url = ctk.STsEntry(content_frame, placeholder_text=("Paste URL here..."))
entry_url.pack(pady="10p")

# Create a download button
download_button = ctk.CTkButton(content_frame, text="Download", command=lambda: download_video(resolutions_var))

# Create a resolutions button
resolutions_button = ctk.CTkButton(content_frame, text="Load Resolutions", command=load_resolutions)
resolutions_button.pack(pady="10p")

# Define resolutions_var globally
resolutions_var = None

# Create a label and the progress bar to display the download progress
progress_label = ctk.CTkLabel(content_frame, text="")

# Create the status label
status_label = ctk.CTkLabel(content_frame, text="")

# Create a donate button
donation_button = ctk.CTkButton(content_frame, text="Donate", command=open_donation_window, border_color="#00d11c")

# Add the on_close function to the close button
app.protocol("WM_DELETE_WINDOW", on_close)

# Start the app
if __name__ == "__main__":
    app.mainloop()