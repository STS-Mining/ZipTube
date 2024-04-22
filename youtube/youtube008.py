# Author: STS-Mining
# Version 1.08

import customtkinter as ctk
from pytube import YouTube
import time
import tkinter.messagebox as messagebox
import pyperclip
from PIL import Image
from tkinter import filedialog

def download_video(save_path=None):
    global download_button
    url = entry_url.get()
    resolution = resolutions_var.get()
    progress_label.pack(pady="10p")
    download_speed_label.pack(pady="5")
    status_label.pack(pady="10p")
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(res=resolution).first()
        if save_path:
            stream.download(output_path=save_path)
        else:
            # If save_path is not provided, use filedialog to get save location
            save_dir = open_file_dialog()
            if save_dir:
                stream.download(output_path=save_dir)
            else:
                # If no save location is selected, cancel download
                raise ValueError("Invalid save location")
        status_label.configure(
            text=f"{yt.title}",
            text_color="white",
            fg_color="transparent",
            font=("Helvetica", 17, "underline")
        )
    except Exception as e:
        status_label.configure(text=f"Error {str(e)}", text_color="white", fg_color="red")

def open_file_dialog():
    folder = filedialog.askdirectory()
    if folder:
        return folder
    return None

def on_progress(stream, chunk, bytes_remaining):
    global start_time, bytes_downloaded_prev, download_button, cancel_download
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percentage = (bytes_downloaded / total_size) * 100
    download_finished = (bytes_downloaded == total_size)
    if download_finished:
        download_button.configure(text="Download Complete!")
        # Schedule hiding labels after 10 seconds
        app.after(10000, hide_labels)
    else:
        download_button.configure(text="Downloading ...")
        current_time = time.time()
        time_elapsed = current_time - start_time
        bytes_downloaded_since_last = bytes_downloaded - bytes_downloaded_prev
        download_speed = bytes_downloaded_since_last / time_elapsed / 1_000_000  # Convert to Mbps
        download_speed_label.configure(text=f"Download Speed: {download_speed:.2f} Mbps")
        # Update global variables for next iteration
        start_time = current_time
        bytes_downloaded_prev = bytes_downloaded
        progress_label.configure(text="{} % of {} \n{} complete".format(
            int(progress_percentage),
            bytes_to_nearest_measurement(int(total_size)),
            bytes_to_nearest_measurement(int(bytes_downloaded))
        ))
        progress_label.update()

# Function to ask for confirmation before closing the window
def on_close():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to close the application?"):
        # Close the app
        app.destroy()
        # Open donation window after the app is closed
        open_donation_window()

def open_donation_window():
    donation_window = ctk.CTk()
    donation_window.title("Notification")
    donation_window.geometry("600x360")
    donation_window.minsize(600, 360)
    donation_window.maxsize(720, 480)
    donation_window.iconbitmap("C:/Python/Stuff/youtube/img/pmp.ico")
    # Create a label with the donation message
    donation_label = ctk.CTkLabel(donation_window, text="Did you enjoy using our app?? \nWould you like us to keep it well maintained & updated? \n\nThen making a donation to one of our following wallets, \nwould help us out and would be greatly appreciated.", font=("Helvetica", 18))
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
    download_speed_label.pack_forget()  # Hide the download speed label
    progress_label.pack_forget()  # Hide the progress label
    # Change button back to Download
    download_button.configure(text="Download", command=download_video)

def bytes_to_nearest_measurement(bytes):
    megabytes = bytes / (1024 * 1024)
    gigabytes = bytes / (1024 * 1024 * 1024)
    if gigabytes >= 1:
        return "{} GB".format(round(gigabytes))
    else:
        return "{} MB".format(round(megabytes))

# Create a app window
app = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("custom")

# Title of the window
app.title("STS Mining")
app.iconbitmap("C:/Python/Stuff/youtube/img/pmp.ico")

# Set min and max width and the height
app.geometry("720x480")
app.minsize(720, 480)
app.maxsize(1080, 720)

# Create a frame to hold the content
content_frame = ctk.CTkFrame(app)
content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

# Define global variables to track download progress
start_time = time.time()
bytes_downloaded_prev = 0

# Create a label and the entry widget for the video url
pil_image = Image.open("C:/Python/Stuff/youtube/img/Logoname2.png")
logo_image = ctk.CTkImage(pil_image, size=(600, 75))
heading = ctk.CTkLabel(content_frame, image=logo_image, text="")
entry_url = ctk.CTkEntry(content_frame, placeholder_text=("Paste URL here..."))
heading.pack(pady="5p")
entry_url.pack(pady="10p")

# Create a resolutions combo box
resolutions_label = ctk.CTkLabel(content_frame, font=("Helvetica", 20), text="Pick Resolution (optional)")
resolutions_label.pack(pady="1p")
resolutions = ["2160p", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"]
resolutions_var = ctk.StringVar()

# Function to handle resolution selection
def select_resolution(resolution):
    resolutions_var.set(resolution)

# Create a resolutions frame
resolutions_frame = ctk.CTkFrame(content_frame)
resolutions_frame.pack(pady="5p")

# Create buttons for each resolution
for i, resolution in enumerate(resolutions):
    button = ctk.CTkButton(resolutions_frame, text=resolution, command=lambda r=resolution: select_resolution(r), width=15, height=5, border_color="#FFCC70")
    button.grid(row=i//8, column=i%8, padx=5, pady=5)

# Create a download button
download_button = ctk.CTkButton(content_frame, text="Download", command=download_video)
download_button.pack(pady="10p")

# Create a label for the download speed
download_speed_label = ctk.CTkLabel(content_frame, text="")

# Create a label and the progress bar to display the download progress
progress_label = ctk.CTkLabel(content_frame, text="")

# Create the status label
status_label = ctk.CTkLabel(content_frame, text="")

# Add the on_close function to the close button
app.protocol("WM_DELETE_WINDOW", on_close)

# Start the app
if __name__ == "__main__":
    app.mainloop()