# Author: STS-Mining
# Python-Version 3.12.3

import customtkinter as ctk
from pytube import YouTube
import time
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
from PIL import Image
import os
import sys
import psutil
import pyperclip
import cpuinfo
import subprocess
import re
import webbrowser
import threading
from tkinter import filedialog
import moviepy.editor as mp
import assets.ffmpeg as ffmpeg
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Icon and logo location on system #
current_version = "1.27" # Make sure to update this version here
app_name = "ZipTube"
icon = resource_path("assets\\images\\icon.ico")
logo = resource_path("assets\\images\\logo.png")
custom_theme = resource_path("assets\\themes\\ziptube-custom.json")
website_url = "https://www.ziptube.com.au/"
discord_link = "https://discord.gg/nVMgU9yQcw"
github_url = "https://github.com/STS-Mining/ZipTube"
feedback_email = "stsmining.ziptube@gmail.com"
ffmpeg_path = resource_path("assets\\ffmpeg\\bin\\ffmpeg.exe")
chromedriver_path = resource_path("assets\\chromedriver\\chromedriver.exe")  # Ensure this path is correct

latest_version_link = None
latest_version_number = None
def extract_version_from_link(link):
    """ Extracts the version number from the given link. """
    match = re.search(r'(\d+\.\d+)', link)
    if match:
        return match.group(1)
    return None

def update_ziptube_version():
    global latest_version_link, latest_version_number
    service = ChromeService(executable_path=chromedriver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(website_url)
        latest_version_link_element = driver.find_element(By.XPATH, "//div[@class='download-link']//a[contains(text(), 'Windows_Setup')]")
        latest_version_link = latest_version_link_element.get_attribute('href')
        latest_version_number = extract_version_from_link(latest_version_link)
    except Exception as e:
        print(f"An error occurred: {e}")
        latest_version_number = None
    finally:
        driver.quit()

# Function that runs at the start of the program being opened up
def check_for_updates():
    update_thread = threading.Thread(target=update_ziptube_version)
    check_cpu_thread = threading.Thread(target=get_cpu_info)
    check_disks_thread = threading.Thread(target=get_disk_info)
    check_cpu_thread.start()
    check_cpu_thread.join()
    check_disks_thread.start()
    check_disks_thread.join()
    update_thread.start()
    update_thread.join()

# Function to run the updates after the program is opened and show a loading screen
def delayed_update():
    print("App has started. Waiting for a few seconds before running updates...")
    time.sleep(5)  # Sleep for 5 seconds or any other delay you want
    check_for_updates()

# Function that runs the update button on the main screen
def latest_version():
    global latest_version_frame, latest_version_link, latest_version_label
    hide_start_menu_frame()
    hide_footer_frame()
    latest_version_label.pack(padx=10, pady=10)
    latest_version_frame.pack(padx=10, pady=100)
    latest_text = ""
    if latest_version_number is None:
        latest_text += "Unable to check for updates at this time."
    elif float(current_version) >= float(latest_version_number):
        latest_text += f"Latest Version: {current_version}\nYou are currently running the latest version of ZipTube."
    else:
        latest_text += f"You are running version {current_version}\nPlease download the latest version {latest_version_number}."
    latest_version_label.configure(text=latest_text)
    if latest_version_number and float(current_version) < float(latest_version_number):
        download_update_button.pack(padx=10, pady=10)
    main_menu_button()

# Function to link website to main screen in a button #
def open_webpage(url):
    webbrowser.open(url, new=2)  # new=2: open in a new tab, if possible

# Save location for all files downloaded #
def choose_save_location():
    save_location = filedialog.askdirectory()
    return save_location

# Function to download only audio files #
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

# Function that downloads the video once the download button is pressed #
def download_video(resolutions_var):
    global download_button, output_path
    url = entry_url.get()
    resolution = resolutions_var.get()
    # Check if the resolution has not been selected #
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
        main_menu_button()
    except Exception:
        status_label.configure(
            text=f"Error, resolution selected doesn't exist for video ...",
            text_color="red",
        )
        app.after(2000, hide_labels)

# Function while the download is in progress #
def on_progress(stream, chunk, bytes_remaining):
    global start_time, bytes_downloaded_prev, download_button, output_path, download_audio_button
    download_button.configure(state="disabled")
    download_audio_button.configure(state="disabled")
    resolutions_button.configure(state="disabled")
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_percentage = (bytes_downloaded / total_size) * 100
    download_finished = bytes_downloaded == total_size
    main_menu_button()
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
                bytes_conversion(int(bytes_downloaded)),
                bytes_conversion(int(total_size)),
                download_speed,
            )
        )
        progress_label.update()
        status_label.configure(text=f"Saving to local location ... {output_path}")
        main_menu_button()

# Function to get disk info #
def get_disk_info():
    partitions = psutil.disk_partitions()
    disk_info = []
    for partition in partitions:
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent_used = usage.percent
            disk_info.append({
                'device': partition.device,
                'mountpoint': partition.mountpoint,
                'total_gb': total_gb,
                'used_gb': used_gb,
                'free_gb': free_gb,
                'percent_used': percent_used
            })
        except Exception as e:
            print(f"Could not get usage for {partition.device}: {e}\n")
    return disk_info

# Function to get cpu info #
def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    return {
        'brand': info['brand_raw'],
        'cores': psutil.cpu_count(logical=False),
        'threads': psutil.cpu_count(logical=True)
    }

# Function to run both disk and cpu info at the same time and to open the window #
def check_disk_space():
    disks_app_name = "ZipTube - Disk Space"
    disks_app = ctk.CTk()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(custom_theme)

    disks_app.title(disks_app_name)

    if os.path.exists(icon):
        disks_app.iconbitmap(icon)
    else:
        print(f"Icon file not found: {icon}")

    disks_frame = ctk.CTkFrame(disks_app)
    disks_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    status_label = ctk.CTkLabel(disks_frame, font=("calibri", 18, "normal"), text="")
    status_label.pack(padx=20, pady=10)
    # Gather information to display
    info_text = ""
    # CPU Information
    info_text += "CPU Information:\n"
    cpu = get_cpu_info()
    info_text += f"Brand: {cpu['brand']}\n"
    info_text += f"Cores: {cpu['cores']}\n"
    info_text += f"Threads: {cpu['threads']}\n\n"
    # Disk Information
    info_text += "Disk Information:\n"
    disks = get_disk_info()
    for disk in disks:
        info_text += f"Device: {disk['device']}\n"
        info_text += f"Total Space: {disk['total_gb']:.2f} GB\n"
        info_text += f"Used Space: {disk['used_gb']:.2f} GB ({disk['percent_used']}%)\n"
        info_text += f"Free Space: {disk['free_gb']:.2f} GB\n\n"
    # Set the gathered information to the status_label
    status_label.configure(text=info_text)
    disks_app.mainloop()

def show_help_menu_buttons():
    help_menu_frame.pack(padx=10, pady=130)
    downloader_help_button.grid(row=0, column=0, padx=5, pady=5)
    converters_help_button.grid(row=0, column=1, padx=5, pady=5)
    disk_info_help_button.grid(row=0, column=2, padx=5, pady=5)

# Function to go back to the help menu
def back_to_help_menu():
    info_label_frame.pack_forget()
    info_label.pack_forget()
    back_menu_frame.pack_forget()
    back_button.pack_forget()
    show_help_menu_buttons()
    main_menu_button()

# Function to open the help window #
def open_help_window():
    hide_start_menu_frame()
    hide_footer_frame()
    show_help_menu_buttons()
    main_menu_button()

def show_back_menu_button():
    back_menu_frame.pack(side='bottom', pady=10)
    back_button.pack(pady=5)

def show_info_labels():
    info_label_frame.pack(padx=20, pady=50)
    info_label.pack(padx=20, pady=10)

# Function to display YouTube downloader help
def downloader_help():
    help_menu_frame.pack_forget()
    back_to_menu_frame.pack_forget()
    show_info_labels()
    info_text = (
        "How to use the download function:\n\n"
        "Here you can download almost any video from YouTube.\n"
        "Choose the resolution of the video you want to download.\n"
        "Choose where you want the files saved on your pc.\n"
        "Once complete you can download another video, or convert video to audio.\n"
        "This option will strip the audio from the video, and save it in mp3 format only.\n"
        "You can also choose to only download the audio instead of the video.\n"
        "This is useful when downloading music files that you like.\n"
    )
    info_label.configure(text=info_text)
    show_back_menu_button()

# Function to display converters help
def converters_help():
    help_menu_frame.pack_forget()
    back_to_menu_frame.pack_forget()
    show_info_labels()
    info_text = (
        "\nHow to use the convertors:\n\n"
        "Here you can convert almost any audio file to almost any other audio file.\n"
        "You can choose where you want the files saved on your pc.\n"
        "All files converted will be done in the best available bitrate.\n"
    )
    info_label.configure(text=info_text)
    show_back_menu_button()

# Function to display disk space help
def disk_space_help():
    help_menu_frame.pack_forget()
    back_to_menu_frame.pack_forget()
    show_info_labels()
    info_text = (
        "\nHow to use the disk space utility:\n\n"
        "This option will give you basic information about your device.\n"
        "This will include all available disk drives, space available,\n"
        "and what cpu / processor is currently installed on your machine.\n"
    )
    info_label.configure(text=info_text)
    show_back_menu_button()

# Function for donation window #
def open_donation_window():
    hide_start_menu_frame()
    hide_footer_frame()
    donation_frame.pack(padx=20, pady=50)
    donation_label.pack(padx=20, pady=10)
    # Define wallet addresses and labels #
    wallets = [
        {"name": "BTC", "address": "12pGQNkdk8C3H32GBtUzXjxgZvxVZLRxsB"},
        {"name": "ETH", "address": "0x7801af1b2acd60e56f9bf0d5039beb3d99ba8bc4"},
        {"name": "DOGE", "address": "D6TE4ZgBfjJ1neYztZFQWiihPZNBS418P5"},
    ]
    # Function to copy wallet address to clipboard #
    def copy_address(name, address):
        pyperclip.copy(address)
        copied_label.configure(
            text=f"\n{name} address copied to clipboard\n\n{address}"
        )
        copied_label.pack()
        copied_label.after(2000, copied_label.pack_forget)
    # Create a frame for the buttons to align them properly #
    donation_button_frame.pack(pady=10)
    # Create buttons to copy wallet addresses #
    for i, wallet in enumerate(wallets):
        copy_button = ctk.CTkButton(
            donation_button_frame,
            text=f"{wallet['name']} Address",
            command=lambda name=wallet["name"], addr=wallet["address"]: copy_address(name, addr),
            font=("calibri", 15, "normal"),
            height=40, width=120, corner_radius=33, border_color="green"
        )
        copy_button.grid(row=0, column=i, padx=5, pady=5)
    # Label to display "Copied to Clipboard" message #
    copied_label = ctk.CTkLabel(donation_frame, text="")
    copied_label.pack(pady=5)
    main_menu_button()

# Generic Function that runs all the audio convertors with same information #
def convert_audio_file(filetypes, conversion_function):
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select Audio File",
        filetypes=filetypes
    )
    if filename:
        conversion_function(filename)

def convert_start_countdown(seconds, convert_countdown_label, convert_app):
    if seconds > 0:
        convert_countdown_label.configure(text=f"Closing window in {seconds} seconds...")
        convert_app.after(1000, convert_start_countdown, seconds - 1, convert_countdown_label, convert_app)
    else:
        convert_app.destroy()

def create_conversion_window(file_path, convert_from, convert_to):
    convert_app_name = f"ZipTube - {convert_from.upper()} to {convert_to.upper()}"
    icon = resource_path("assets\\images\\icon.ico")
    convert_app = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(custom_theme)
    convert_app.title(convert_app_name)
    convert_app.wm_iconbitmap(icon)
    convert_main_frame = ctk.CTkFrame(convert_app)
    convert_main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
    ''' Create the labels '''
    convert_status_label = ctk.CTkLabel(convert_main_frame, font=("calibri", 18, "normal"), text=f"Converting {convert_from} file to {convert_to} file ...")
    convert_status_label.pack(padx=20, pady=10)
    convert_countdown_label = ctk.CTkLabel(convert_main_frame, font=("calibri", 18, "normal"), text="")
    convert_countdown_label.pack(pady=10)
    convert_app.after(100, run_conversion, file_path, convert_from, convert_to, convert_status_label, convert_countdown_label, convert_app)  # Delay the conversion to ensure the UI is fully rendered
    convert_app.mainloop()

def run_conversion(file_path, convert_from, convert_to, convert_status_label, convert_countdown_label, convert_app):
    root_path, filename = os.path.split(file_path)
    new_filename = os.path.splitext(filename)[0] + "." + convert_to
    new_path = os.path.join(root_path, new_filename)
    completed = subprocess.run([ffmpeg_path,
                                "-loglevel",
                                "quiet",
                                "-hide_banner",
                                "-y",
                                "-i",
                                file_path,
                                new_path],
                                stderr=subprocess.DEVNULL,
                                stdout=subprocess.DEVNULL,
                                stdin=subprocess.PIPE)
    if completed.returncode == 0:
        convert_status_label.configure(text=f"Successfully Converted ... \n\n{new_filename}")
    else:
        convert_status_label.configure(text=f"Conversion failed ... \n\n{new_filename}")
    convert_start_countdown(5, convert_countdown_label, convert_app)  # Start the countdown after the conversion is complete

def mp3_to_flac(file_path):
    create_conversion_window(file_path, "mp3", "flac")

def mp3_to_wav(file_path):
    create_conversion_window(file_path, "mp3", "wav")

def mp3_to_wma(file_path):
    create_conversion_window(file_path, "mp3", "wma")

def flac_to_mp3(file_path):
    create_conversion_window(file_path, "flac", "mp3")

def flac_to_wav(file_path):
    create_conversion_window(file_path, "flac", "wav")

def flac_to_wma(file_path):
    create_conversion_window(file_path, "flac", "wma")

def wav_to_flac(file_path):
    create_conversion_window(file_path, "wav", "flac")

def wav_to_mp3(file_path):
    create_conversion_window(file_path, "wav", "mp3")

def wav_to_wma(file_path):
    create_conversion_window(file_path, "wav", "wma")

def wma_to_flac(file_path):
    create_conversion_window(file_path, "wma", "flac")

def wma_to_mp3(file_path):
    create_conversion_window(file_path, "wma", "mp3")

def wma_to_wav(file_path):
    create_conversion_window(file_path, "wma", "wav")

# Function to ask for confirmation before closing the window #
def on_close():
    if messagebox.askokcancel("Confirmation", "Are you sure you want to close the application?"):
        app.destroy()

# Function convert video to audio #
def convert_video_to_audio():
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select Video File",
        filetypes=(("Video files", "*.mp4 *.avi *.mkv"), ("all files", "*.*")),
    )
    if filename:
        convert_to_audio(filename)

def convert_to_audio(video_file):
    convert_to_audio_app_name = "ZipTube - Video to Audio"
    icon = resource_path("assets\\images\\icon.ico")
    convert_to_audio_app = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(custom_theme)
    convert_to_audio_app.title(convert_to_audio_app_name)
    convert_to_audio_app.wm_iconbitmap(icon)
    convert_main_frame = ctk.CTkFrame(convert_to_audio_app)
    convert_main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)
    # Create the labels
    convert_status_label = ctk.CTkLabel(convert_main_frame, font=("calibri", 18, "normal"), text="Converting Video file to Audio file ...")
    convert_status_label.pack(padx=20, pady=10)
    convert_countdown_label = ctk.CTkLabel(convert_main_frame, font=("calibri", 18, "normal"), text="")
    convert_countdown_label.pack(pady=10)
    # Run the conversion after the UI is fully rendered
    convert_to_audio_app.after(100, video_to_audio_conversion, video_file, convert_status_label, convert_countdown_label, convert_to_audio_app)
    convert_to_audio_app.mainloop()

def video_to_audio_conversion(video_file, convert_status_label, convert_countdown_label, convert_to_audio_app):
    try:
        audio_file = video_file.replace(".mp4", ".mp3")
        video = mp.VideoFileClip(video_file)
        video.audio.write_audiofile(audio_file)
        video.close()
        convert_status_label.configure(text=f"Successfully Converted:\n\n{audio_file}")
    except Exception as e:
        convert_status_label.configure(text=f"Conversion failed: {str(e)}")
    convert_start_countdown(5, convert_countdown_label, convert_to_audio_app)  # Start the countdown after the conversion is complete

# Hide the labels after 3 seconds #
def hide_labels():
    global resolutions_var
    # resolutions_var.set("")
    status_label.pack_forget()
    progress_label.pack_forget()
    resolutions_button.pack_forget()
    download_button.configure(state="normal")
    download_button.configure(text="Download Another Video", command=download_another_video)
    download_audio_button.configure(state="normal")
    download_audio_button.configure(text="Download Another Song", command=download_audio_only)
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    convert_to_audio_button.pack(pady=10)
    main_menu_button()

# Function to print all available resolutions for a YouTube video #
def print_available_resolutions(url):
    try:
        yt = YouTube(url)
        streams = yt.streams.filter()
        resolutions = sorted(
            set([stream.resolution for stream in streams if stream.resolution]),
            key=lambda x: int(x[:-1]),
        )
        resolutions_var = ctk.StringVar()
        # Function to handle resolution selection #
        def select_resolution(resolution):
            resolutions_var.set(resolution)
        # Create a frame to hold the resolution buttons #
        selected_resolution = ctk.StringVar()
        resolutions_frame.pack(pady=10)
        # Create a radio button for each available resolution #
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
            main_menu_button()
        return resolutions_var
    except Exception as e:
        print(f"Error fetching resolutions for URL {url}: {e}")

# Function to load the resolutions for a YouTube video #
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
        main_menu_button()

# Function to start a new download #
def download_another_video():
    global resolutions_var
    resolutions_var.set("")
    download_button.pack_forget()
    convert_to_audio_button.pack_forget()
    resolutions_button.configure(state="normal")
    resolutions_button.configure(text="Load Resolutions", command=load_resolutions)
    resolutions_button.pack(pady=10)
    download_button.configure(text="Download", command=lambda: download_video(resolutions_var))
    main_menu_button()

# Calculate the nearest measurement for bytes #
def bytes_conversion(bytes):
    for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024

# Function to load entry widget for the video url and resolutions button #
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
    start_menu_frame.pack_forget()
    want_to_download_button.pack_forget()
    # want_to_convert_to_audio_button.pack_forget()
    main_menu_button()

# function to download audio file only #
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
    start_menu_frame.pack_forget()
    want_to_download_button.pack_forget()
    # want_to_convert_to_audio_button.pack_forget()
    main_menu_button()

# Function to show all the available convertors #
def show_converters():
    hide_start_menu_frame()
    hide_footer_frame()
    convertors_frame.pack(padx=10, pady=85)
    # want_to_convert_to_audio_button.grid(row=0, column=1, padx=5, pady=5)
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
    main_menu_button()

# Function to show all the available convertors #
def hide_converters():
    hide_start_menu_frame()
    hide_footer_frame()
    convertors_frame.pack_forget()

# Function to show the download buttons available #
def show_youtube_downloader():
    hide_start_menu_frame()
    hide_footer_frame()
    youtube_menu_frame.pack(padx=10, pady=130)
    want_to_download_button.grid(row=0, column=0, padx=5, pady=5)
    want_to_download_audio_button.grid(row=0, column=1, padx=5, pady=5)
    main_menu_button()

def hide_start_menu_frame():
    start_menu_frame.pack_forget()

def back_main_menu_button():
    hide_start_menu_frame()
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
    # want_to_convert_to_audio_button.pack_forget()
    download_audio_button.pack_forget()
    latest_version_frame.pack_forget()
    latest_version_label.pack_forget()
    download_update_button.pack_forget()
    help_menu_frame.pack_forget()
    donation_frame.pack_forget()
    donation_label.pack_forget()
    donation_button_frame.pack_forget()
    start_menu_frame.pack(padx=10, pady=130)
    footer_frame.pack(side="bottom", pady=10)

# Function to go back to the main menu screen #
def main_menu_button():
    back_to_menu_frame.pack(side='bottom', pady=10)
    back_to_menu_button.pack(pady=5)

# Function to hide buttons at bottom of screen #
def hide_footer_frame():
    footer_frame.pack_forget()

# Create a app window #
app = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(custom_theme)

# Title of the window #
app.title(app_name)
app.wm_iconbitmap(icon)

# Set min and max width and height #
min_max_height = 550
min_max_width = 650
app.geometry(f"{min_max_width}x{min_max_height}")
app.minsize(min_max_width, min_max_height)
app.maxsize(min_max_width, min_max_height)

# Create a frame to hold the content #
main_frame = ctk.CTkFrame(app)
main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

# Custom button configurations to be set here #
base_config = {
    'font': ctk.CTkFont(family="calibri", size=15, weight="normal"),
    'height': 40,
    'width': 120,
    'corner_radius': 33
}

button_specifics = {
    'main': {'border_color': "blue"},
    'convertors': {
        'font': ctk.CTkFont(family="calibri", size=13, weight="normal"),
        'border_color': "green",
        'height': 30,
        'width': 90
    },
    'start_menu': {'border_color': "orange"},
    'footer': {
        'font': ctk.CTkFont(family="calibri", size=13, weight="normal"),
        'border_color': "red",
        'height': 20,
        'width': 60
    }
}

def button_configurations(button_type):
    if button_type not in button_specifics:
        raise ValueError("Invalid button type")
    config = base_config.copy()
    config.update(button_specifics[button_type])
    return config

main_button_config = button_configurations('main')
convertors_button_config = button_configurations('convertors')
footer_button_config = button_configurations('footer')
start_menu_button_config = button_configurations('start_menu')

# Define global variables to track download progress #
start_time = time.time()
bytes_downloaded_prev = 0

# Create a label and the entry widget for the video url #
pil_image = Image.open(logo)
logo_image = ctk.CTkImage(pil_image, size=(250, 60))
heading = ctk.CTkLabel(main_frame, image=logo_image, text="")
heading.pack(pady="10p")

# Initialize the main menu frame #
start_menu_frame = ctk.CTkFrame(main_frame)
start_menu_frame.pack(padx=10, pady=130)

# Buttons for opening the sub-menus #
converters_button = ctk.CTkButton(start_menu_frame, text="Convert", command=show_converters, **start_menu_button_config)
youtube_downloader_button = ctk.CTkButton(start_menu_frame, text="Download", command=show_youtube_downloader, **start_menu_button_config)
local_info_button = ctk.CTkButton(start_menu_frame, text="Disk Space", command=check_disk_space, **start_menu_button_config)
youtube_downloader_button.grid(row=0, column=0, padx=5, pady=5)
converters_button.grid(row=0, column=1, padx=5, pady=5)
local_info_button.grid(row=0, column=2, padx=5, pady=5)

# Initialize the main frame #
footer_frame = ctk.CTkFrame(main_frame)
footer_frame.pack(side="bottom", pady=10)

# Bottom of the main screen donation and website buttons #
website_button = ctk.CTkButton(footer_frame, text="Website", command=lambda: open_webpage(website_url), **footer_button_config)
github_button = ctk.CTkButton(footer_frame, text="GitHub", command=lambda: open_webpage(github_url), **footer_button_config)
discord_button = ctk.CTkButton(footer_frame, text="Discord", command=lambda: open_webpage(discord_link), **footer_button_config)
donation_button = ctk.CTkButton(footer_frame, text="Donate", command=open_donation_window, **footer_button_config)
help_button = ctk.CTkButton(footer_frame, text="Help", command=open_help_window, **footer_button_config)
update_button = ctk.CTkButton(footer_frame, text="Update", command=latest_version, **footer_button_config)
website_button.grid(row=0, column=0, padx=5, pady=5)
github_button.grid(row=0, column=1, padx=5, pady=5)
discord_button.grid(row=0, column=2, padx=5, pady=5)
donation_button.grid(row=0, column=3, padx=5, pady=5)
help_button.grid(row=0, column=4, padx=5, pady=5)
update_button.grid(row=0, column=5, padx=5, pady=5)

# Create the latest version frame for the update screen
latest_version_frame = ctk.CTkFrame(main_frame)
latest_version_label = ctk.CTkLabel(latest_version_frame, font=("Calibri", 18, "normal"), text="")
download_update_button = ctk.CTkButton(latest_version_frame, text="Download Now!", command=lambda: webbrowser.open(latest_version_link))

# Create a frame to hold the content
help_menu_frame = ctk.CTkFrame(main_frame)
back_menu_frame = ctk.CTkFrame(main_frame)
info_label_frame = ctk.CTkFrame(main_frame)
info_label = ctk.CTkLabel(info_label_frame, font=("calibri", 17, "normal"), text="")
back_button = ctk.CTkButton(back_menu_frame, text="Back", command=back_to_help_menu, **main_button_config)
downloader_help_button = ctk.CTkButton(help_menu_frame, text="Download Help", command=downloader_help, font=("calibri", 15, "normal"), height=40, width=120, corner_radius=33, border_color="green")
converters_help_button = ctk.CTkButton(help_menu_frame, text="Convertor Help", command=converters_help, font=("calibri", 15, "normal"), height=40, width=120, corner_radius=33, border_color="green")
disk_info_help_button = ctk.CTkButton(help_menu_frame, text="Disk Space Help", command=disk_space_help, font=("calibri", 15, "normal"), height=40, width=120, corner_radius=33, border_color="green")

# Youtube menu frame #
youtube_menu_frame = ctk.CTkFrame(main_frame)

# Define all the other buttons for YouTube menu #
want_to_download_button = ctk.CTkButton(youtube_menu_frame, text="Download Video", command=load_entry_and_resolutions_button, **convertors_button_config)
want_to_download_audio_button = ctk.CTkButton(youtube_menu_frame, text="Download Audio", command=download_audio_only, **convertors_button_config)

# Convertor Frame #
convertors_frame = ctk.CTkFrame(main_frame)

# Define all the other buttons for Converter menu #
# want_to_convert_to_audio_button = ctk.CTkButton(convertors_frame, text="Video to Audio", command=convert_video_to_audio, **convertors_button_config)
convert_mp3_to_flac_button = ctk.CTkButton(convertors_frame, text="MP3 to FLAC", command=lambda: convert_audio_file([("MP3 files", "*.mp3")], mp3_to_flac), **convertors_button_config)
convert_mp3_to_wav_button = ctk.CTkButton(convertors_frame, text="MP3 to WAV", command=lambda: convert_audio_file([("MP3 files", "*.mp3")], mp3_to_wav), **convertors_button_config)
convert_mp3_to_wma_button = ctk.CTkButton(convertors_frame, text="MP3 to WMA", command=lambda: convert_audio_file([("MP3 files", "*.mp3")], mp3_to_wma), **convertors_button_config)
convert_flac_to_mp3_button = ctk.CTkButton(convertors_frame, text="FLAC to MP3", command=lambda: convert_audio_file([("FLAC files", "*.flac")], flac_to_mp3), **convertors_button_config)
convert_flac_to_wav_button = ctk.CTkButton(convertors_frame, text="FLAC to WAV", command=lambda: convert_audio_file([("FLAC files", "*.flac")], flac_to_wav), **convertors_button_config)
convert_flac_to_wma_button = ctk.CTkButton(convertors_frame, text="FLAC to WMA", command=lambda: convert_audio_file([("FLAC files", "*.flac")], flac_to_wma), **convertors_button_config)
convert_wav_to_mp3_button = ctk.CTkButton(convertors_frame, text="WAV to MP3", command=lambda: convert_audio_file([("WAV files", "*.wav")], wav_to_mp3), **convertors_button_config)
convert_wav_to_flac_button = ctk.CTkButton(convertors_frame, text="WAV to FLAC", command=lambda: convert_audio_file([("WAV files", "*.wav")], wav_to_flac), **convertors_button_config)
convert_wav_to_wma_button = ctk.CTkButton(convertors_frame, text="WAV to WMA", command=lambda: convert_audio_file([("WAV files", "*.wav")], wav_to_wma), **convertors_button_config)
convert_wma_to_mp3_button = ctk.CTkButton(convertors_frame, text="WMA to MP3", command=lambda: convert_audio_file([("WMA files", "*.wma")], wma_to_mp3), **convertors_button_config)
convert_wma_to_flac_button = ctk.CTkButton(convertors_frame, text="WMA to FLAC", command=lambda: convert_audio_file([("WMA files", "*.wma")], wma_to_flac), **convertors_button_config)
convert_wma_to_wav_button = ctk.CTkButton(convertors_frame, text="WMA to WAV", command=lambda: convert_audio_file([("WMA files", "*.wma")], wma_to_wav), **convertors_button_config)

# Create a button to always get the user back to the main menu #
back_to_menu_frame = ctk.CTkFrame(main_frame)
back_to_menu_button = ctk.CTkButton(back_to_menu_frame, text="Main Menu", command=back_main_menu_button, **main_button_config)

# Create a label and the entry widget for the video url #
entry_url = ctk.CTkEntry(main_frame, width=390, placeholder_text=("Paste URL here..."))

# Create a resolutions frame to hold the resolutions #
resolutions_frame = ctk.CTkFrame(main_frame)

# Create a download button #
download_button = ctk.CTkButton(main_frame, text="Download", command=lambda: download_video(resolutions_var))

# Create a download audio button #
download_audio_button = ctk.CTkButton(main_frame, text="Download", command=download_audio)

# Create a resolutions button #
resolutions_button = ctk.CTkButton(main_frame, text="Load Resolutions", command=load_resolutions)

# Create a donation frame and button
donation_frame = ctk.CTkFrame(main_frame)
donation_label = ctk.CTkLabel(donation_frame, font=("calibri", 17, "normal"), text="Enjoy using our app?? \nWould you like us to keep it well maintained? \n\nThen making a donation to one of our following wallets, \nwould help us out and would be greatly appreciated.")
donation_button_frame = ctk.CTkFrame(donation_frame)

# Define resolutions_var globally #
resolutions_var = None

# Create and position GUI elements #
convert_to_audio_button = ctk.CTkButton(main_frame, text="Convert Video to Audio", command=convert_video_to_audio)

# Create a label and the progress bar to display the download progress #
progress_label = ctk.CTkLabel(main_frame, text="")

# Create the status label #
status_label = ctk.CTkLabel(main_frame, text="")

# Add the on_close function to the close button #
app.protocol("WM_DELETE_WINDOW", on_close)

# Start the app #
if __name__ == "__main__":
    update_thread = threading.Thread(target=delayed_update)
    update_thread.start()
    app.mainloop()