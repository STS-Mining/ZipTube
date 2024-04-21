# Author: STS-Mining
# Version 1.04

import customtkinter as ctk
from pytube import YouTube
import os
import time
import tkinter.messagebox as messagebox
import pyperclip
from PIL import Image

def download_video():
    global download_button, cancel_download
    url = entry_url.get()
    resolution = resolutions_var.get()
    progress_bar.pack(pady="10p")
    progress_label.pack(pady="10p")
    download_speed_label.pack(pady="5")
    status_label.pack(pady="10p")
    
    # Change button to Cancel
    cancel_download = False  # Reset the flag
    download_button.configure(text="CANCEL", command=cancel_download, border_color="#fa0303")
    
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.filter(res=resolution).first()
        # Download the video to specific directory
        os.path.join("downloads", f"{yt.title}")
        stream.download(output_path="downloads")
        
        if not cancel_download:
            status_label.configure(
                text=f"{yt.title}",
                text_color="white",
                fg_color="transparent",
                font=("Helvetica", 17, "underline")
            )
        else:
            status_label.configure(text="Download Canceled")
    except Exception as e:
        if not cancel_download:
            status_label.configure(text=f"Error {str(e)}", text_color="white", fg_color="red")
        else:
            status_label.configure(text="Download Canceled")

def cancel_download():
    global cancel_download
    cancel_download = True

def on_progress(stream, chunk, bytes_remaining):
    global start_time, bytes_downloaded_prev, download_button, cancel_download
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percentage = (bytes_downloaded / total_size) * 100
    
    # Check if download should be canceled
    if cancel_download:
        status_label.configure(text="Download Canceled")
        return
    
    download_finished = (bytes_downloaded == total_size)
    if download_finished:
        download_button.configure(text="Download Complete!", border_color="#00d11c")
        progress_bar.pack_forget()  # Hide the progress bar
        # Schedule hiding labels after 10 seconds
        app.after(10000, hide_labels)
        
    else:
        # Change button to Cancel
        download_button.configure(text="CANCEL", command=cancel_download, border_color="#fa0303")
        current_time = time.time()
        time_elapsed = current_time - start_time
        bytes_downloaded_since_last = bytes_downloaded - bytes_downloaded_prev
        download_speed = bytes_downloaded_since_last / time_elapsed / 1_000_000  # Convert to Mbps
        download_speed_label.configure(text=f"Download Speed: {download_speed:.2f} Mbps")
        # Update global variables for next iteration
        start_time = current_time
        bytes_downloaded_prev = bytes_downloaded
        progress_label.configure(text="Downloading ... {} % of {} \n{} downloaded".format(
            int(progress_percentage),
            bytes_to_nearest_measurement(int(total_size)),
            bytes_to_nearest_measurement(int(bytes_downloaded))
        ))
        progress_label.update()
        progress_bar.set(progress_percentage / 100)

# Function to ask for confirmation before closing the window
def on_close():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to close the application?"):
        # Close the app
        app.destroy()
        # Open donation window after the app is closed
        open_donation_window()

def open_donation_window():
    donation_window = ctk.CTk()
    donation_window.title("Please Donate")
    donation_window.geometry("600x360")
    donation_window.minsize(600, 360)
    donation_window.maxsize(720, 480)
    # Create a label with the donation message
    donation_label = ctk.CTkLabel(donation_window, text="Did you enjoy using our app?? \nWould you like us to keep it well maintained & updated? \n\nThen making a donation to one of our following wallets, \nwould help us out and would be greatly appreciated.", font=("Helvetica", 20))
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
        copy_button = ctk.CTkButton(donation_window, text=f"{wallet['name']} Address", command=lambda name=wallet['name'], addr=wallet['address']: copy_address(name, addr), fg_color="transparent", hover_color="#423e3e", border_color="#00d11c", border_width=2)
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
    download_button.configure(text="DOWNLOAD", command=download_video, border_color="#00d11c")


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
ctk.set_default_color_theme("green")

# Title of the window
app.title("STS Mining")
app.iconbitmap("img/pmp.ico")

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
pil_image = Image.open("img/Logoname2.png")
logo_image = ctk.CTkImage(pil_image, size=(600, 75))
heading = ctk.CTkLabel(content_frame, image=logo_image)
entry_url = ctk.CTkEntry(content_frame, width=400, height=40, placeholder_text=("Paste URL here..."))
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
    button = ctk.CTkButton(resolutions_frame, text=resolution, corner_radius=15, command=lambda r=resolution: select_resolution(r), width=15, height=5, fg_color="transparent", hover_color="#423e3e", border_color="#FFCC70", border_width=2)
    button.grid(row=i//8, column=i%8, padx=5, pady=5)

# Create a download button
download_button = ctk.CTkButton(content_frame, width=200, height=40, text="DOWNLOAD", font=("Helvetica", 16), command=download_video, fg_color="transparent", hover_color="#423e3e", border_color="#00d11c", border_width=2)
download_button.pack(pady="10p")

# Create a label for the download speed
download_speed_label = ctk.CTkLabel(content_frame, text="")

# Create a label and the progress bar to display the download progress
progress_label = ctk.CTkLabel(content_frame, text="0%")
progress_bar = ctk.CTkProgressBar(content_frame, width=200, height=20, border_color="#00d11c", progress_color="#00d11c", border_width=2)

# Create the status label
status_label = ctk.CTkLabel(content_frame, text="")

# Add the on_close function to the close button
app.protocol("WM_DELETE_WINDOW", on_close)

# Start the app
app.mainloop()