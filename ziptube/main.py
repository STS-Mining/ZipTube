# Author: STS-Mining
# Python-Version 3.12.3

import tkinter.messagebox as messagebox
from tkinter import filedialog
from bs4 import BeautifulSoup
import customtkinter as ctk
from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitize_filename
from PIL import Image
import webbrowser
import threading
import pyperclip
import requests
import time
import sys
import os
import re
import queue
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse, urljoin
from packaging.version import Version

# https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
def resource_path(relative_path):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative_path.replace("\\", "/"))

# Define global variables here #
app_name = "ZipTube"
buttons_centered = 130
current_version = "1.31" # Make sure to update this version here
feedback_email = "info@ziptube.com.au"
website_url = "https://ziptube.sts-media.org/"
discord_link = "https://discord.gg/nVMgU9yQcw"
icon = resource_path("assets\\images\\icon.ico")
logo = resource_path("assets\\images\\logo.png")
github_url = "https://github.com/STS-Mining/ZipTube"
ffmpeg_path = resource_path("assets\\ffmpeg\\bin\\ffmpeg.exe")
custom_theme = resource_path("assets\\themes\\ziptube-custom.json")

latest_version_link = None
latest_version_number = None
def extract_version_from_link(link):
    match = re.search(r"ziptube_windows_setup_(\d+(?:\.\d+)+)\.exe", link)
    return match.group(1) if match else None

def update_ziptube_version():
    try:
        response = requests.get(website_url, timeout=15)
        response.raise_for_status()
        links = BeautifulSoup(response.content, "html.parser").find_all("a", href=True)
        versions = [(extract_version_from_link(a["href"]), urljoin(website_url, a["href"])) for a in links]
        versions = [(version, link) for version, link in versions if version]
        if versions:
            version, link = max(versions, key=lambda item: Version(item[0]))
            ui_events.put(("update", (version, link)))
    except Exception as exc:
        # An unavailable update website must not block downloads or startup.
        print(f"Update check unavailable: {exc}", file=sys.stderr)

# Function that runs at the start of the program being opened up
def check_for_updates():
    threading.Thread(target=update_ziptube_version, daemon=True).start()

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
    elif Version(current_version) >= Version(latest_version_number):
        latest_text += f"Latest Version: {current_version}\nYou are currently running the latest version of ZipTube."
        update_button.configure(text=f"Version {current_version}")
    else:
        latest_text += f"You are running version {current_version}\nPlease download the latest version {latest_version_number}."
        update_button.configure(text="Update")
    latest_version_label.configure(text=latest_text)
    if latest_version_number and Version(current_version) < Version(latest_version_number):
        download_update_button.pack(padx=10, pady=10)
    main_menu_button()

# Function to link website to main screen in a button #
def open_webpage(url):
    webbrowser.open(url, new=2)  # new=2: open in a new tab, if possible

def share_to_twitter():
    message = "Check out this awesome program!"
    url = website_url
    twitter_url = f"https://twitter.com/intent/tweet?text={message}&url={url}"
    webbrowser.open(twitter_url)

def share_to_facebook():
    url = website_url
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={url}"
    webbrowser.open(facebook_url)

def share_to_instagram():
    message = "Check out this awesome program!"
    url = website_url
    instagram_url = f"https://www.instagram.com/sharing?url={url}&text={message}"
    webbrowser.open(instagram_url)

def share_to_whatsapp():
    message = "Check out this awesome program!"
    url = website_url
    whatsapp_url = f"https://api.whatsapp.com/send?text={message}%20{url}"
    webbrowser.open(whatsapp_url)

def show_social_media_window():
    hide_start_menu_frame()
    hide_footer_frame()
    social_media_frame.pack(padx=10, pady=buttons_centered)
    twitter_button.grid(row=0, column=0, padx=5, pady=5)
    facebook_button.grid(row=0, column=1, padx=5, pady=5)
    whatsapp_button.grid(row=0, column=2, padx=5, pady=5)
    instagram_button.grid(row=0, column=3, padx=5, pady=5)
    main_menu_button()

def hide_social_media_window():
    social_media_frame.pack_forget()
    twitter_button.grid_forget()
    facebook_button.grid_forget()
    whatsapp_button.grid_forget()
    instagram_button.grid_forget()
    show_start_menu_frame()
    show_footer_frame()

# Save location for all files downloaded #
def choose_save_location():
    save_location = filedialog.askdirectory()
    return save_location

# Function to download only audio files #
def download_audio():
    start_download(audio_only=True)

# Function that downloads the video once the download button is pressed #
def download_video(resolutions_var):
    if resolutions_var is None or not resolutions_var.get():
        messagebox.showerror("Download", "Load and select a resolution first.")
        return
    start_download(audio_only=False, height=int(resolutions_var.get().rstrip("p")))

# Function while the download is in progress #
def on_progress(data):
    # Worker threads only send messages; Tk widgets are updated by poll_events.
    if data.get("status") == "downloading":
        now = time.monotonic()
        if now - getattr(on_progress, "last_update", 0) < 0.2:
            return
        on_progress.last_update = now
        total = data.get("total_bytes") or data.get("total_bytes_estimate")
        downloaded = data.get("downloaded_bytes", 0)
        percent = f"{downloaded / total * 100:.1f}%" if total else bytes_conversion(downloaded)
        speed = data.get("speed")
        rate = f" — {bytes_conversion(speed)}/s" if speed else ""
        ui_events.put(("progress", f"Downloading: {percent}{rate}"))
    elif data.get("status") == "finished":
        ui_events.put(("progress", "Download received. Processing media…"))

def show_help_menu_buttons():
    help_menu_frame.pack(padx=10, pady=buttons_centered)
    downloader_help_button.grid(row=0, column=0, padx=5, pady=5)
    # disk_info_help_button.grid(row=0, column=2, padx=5, pady=5)

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
    info_label_frame.pack(padx=20, pady=80)
    info_label.pack(padx=20, pady=10)

# Function to display YouTube downloader help
def downloader_help():
    help_menu_frame.pack_forget()
    back_to_menu_frame.pack_forget()
    show_info_labels()
    info_text = (
        "Choose Download Video or Download Audio on the main screen.\n\n"
        "Video: paste a YouTube link, load resolutions, choose quality,\n"
        "then click Download and select where to save the MP4.\n\n"
        "Audio: paste a YouTube link, then click Download to save an MP3.\n"
        "The suggested filename includes the YouTube title and quality.\n"
        "Wait for Download complete before opening the saved file."
    )
    info_label.configure(text=info_text)
    show_back_menu_button()


# Function to display disk space help
def disk_space_help():
    help_menu_frame.pack_forget()
    back_to_menu_frame.pack_forget()
    show_info_labels()
    info_text = (
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
    for child in donation_button_frame.winfo_children():
        child.destroy()
    for child in donation_frame.winfo_children():
        if child not in (donation_label, donation_button_frame):
            child.destroy()
    donation_button_frame.pack(pady=10)
    # Create buttons to copy wallet addresses #
    for i, wallet in enumerate(wallets):
        copy_button = ctk.CTkButton(
            donation_button_frame,
            text=f"{wallet['name']} Address",
            command=lambda name=wallet["name"], addr=wallet["address"]: copy_address(name, addr),
            font=("calibri", 15, "normal"),
            height=30, width=90, corner_radius=33, border_color="green"
        )
        copy_button.grid(row=0, column=i, padx=5, pady=5)
    # Label to display "Copied to Clipboard" message #
    copied_label = ctk.CTkLabel(donation_frame, text="")
    copied_label.pack(pady=5)
    main_menu_button()


# Function to ask for confirmation before closing the window #
def on_close():
    if busy:
        messagebox.showinfo("ZipTube", "Please wait for the current download to finish.")
        return
    if messagebox.askokcancel("Confirmation", "Close ZipTube?"):
        app.destroy()


# Hide the labels after 3 seconds #
def hide_labels():
    status_label.pack_forget()
    progress_label.pack_forget()

# Function to print all available resolutions for a YouTube video #
def print_available_resolutions(url):
    with YoutubeDL(base_download_options()) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info or info.get("_type") in ("playlist", "multi_video"):
        raise ValueError("Please use a single video link, not a playlist.")
    heights = sorted({int(f["height"]) for f in info.get("formats", [])
                      if f.get("height") and f.get("vcodec") not in (None, "none")})
    if not heights:
        raise ValueError("No downloadable video resolutions were found.")
    return {"url": url, "title": info.get("title", "Video"), "heights": heights}

# Function to load the resolutions for a YouTube video #
def load_resolutions():
    global loaded_url
    if busy:
        return
    try:
        url = validated_url()
    except ValueError as exc:
        messagebox.showerror("URL", str(exc))
        return
    loaded_url = None
    resolutions_var.set("")
    for child in resolutions_frame.winfo_children():
        child.destroy()
    download_button.pack_forget()
    run_task(lambda: print_available_resolutions(url), show_resolutions, "Loading resolutions…")

# Function to start a new download #
def download_another_video():
    resolutions_var.set("")
    download_button.pack_forget()
    resolutions_button.configure(state="normal", text="Load Resolutions", command=load_resolutions)
    resolutions_button.pack(pady=10)
    hide_labels()

# Calculate the nearest measurement for bytes #
def bytes_conversion(bytes):
    for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB"]:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024

# Function to load entry widget for the video url and resolutions button #
def load_entry_and_resolutions_button():
    global entry_url, resolutions_button, resolutions_frame, download_button
    hide_footer_frame()
    hide_labels()
    download_audio_button.pack_forget()
    resolutions_button.pack_forget()
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    resolutions_var.set("")
    download_button.pack_forget()
    entry_url.pack(pady=10)
    resolutions_button.pack(pady="10p")
    start_menu_frame.pack_forget()
    main_menu_button()

# function to download audio file only #
def download_audio_only():
    global entry_url, resolutions_button, resolutions_frame, download_button
    hide_footer_frame()
    hide_labels()
    download_audio_button.pack_forget()
    resolutions_button.pack_forget()
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    resolutions_var.set("")
    download_button.pack_forget()
    entry_url.pack(pady=10)
    download_audio_button.configure(text="Download", command=download_audio)
    download_audio_button.pack(pady=10)
    start_menu_frame.pack_forget()
    main_menu_button()


# Function to show the download buttons available #

def back_main_menu_button():
    hide_start_menu_frame()
    hide_footer_frame()
    back_to_menu_frame.pack_forget()
    hide_footer_frame()
    hide_labels()
    download_audio_button.pack_forget()
    resolutions_button.pack_forget()
    resolutions_frame.pack_forget()
    entry_url.delete(0, ctk.END)
    resolutions_var.set("")
    entry_url.pack_forget()
    download_button.pack_forget()
    download_audio_button.pack_forget()
    latest_version_frame.pack_forget()
    latest_version_label.pack_forget()
    download_update_button.pack_forget()
    help_menu_frame.pack_forget()
    info_label_frame.pack_forget()
    back_menu_frame.pack_forget()
    hide_labels()
    donation_frame.pack_forget()
    donation_label.pack_forget()
    donation_button_frame.pack_forget()
    hide_social_media_window()
    show_start_menu_frame()
    show_footer_frame()

# Function to go back to the main menu screen #
def main_menu_button():
    back_to_menu_frame.pack(side='bottom', pady=10)
    back_to_menu_button.pack(pady=5)

def show_start_menu_frame():
    start_menu_frame.pack(padx=10, pady=buttons_centered)

def hide_start_menu_frame():
    start_menu_frame.pack_forget()

def show_footer_frame():
    footer_frame.pack(side="bottom", pady=10)

def hide_footer_frame():
    footer_frame.pack_forget()

# Function to toggle appearance mode
def toggle_appearance_mode():
    ctk.set_appearance_mode("light" if ctk.get_appearance_mode() == "Dark" else "dark")

# Download workers never touch Tk. The main thread drains this queue.
ui_events = queue.Queue()
busy = False
saved_widget_states = []
loaded_url = None
loaded_title = ""
AUDIO_BITRATE = 192


def show_status(text):
    status_label.configure(text=text, text_color=("gray10", "gray90"), wraplength=680)
    status_label.pack(pady=10)


def set_busy(value):
    global busy, saved_widget_states
    busy = value
    if value:
        saved_widget_states = []
        def disable(parent):
            for widget in parent.winfo_children():
                if isinstance(widget, (ctk.CTkButton, ctk.CTkEntry, ctk.CTkRadioButton)):
                    saved_widget_states.append((widget, widget.cget("state")))
                    widget.configure(state="disabled")
                disable(widget)
        disable(app)
    else:
        for widget, state in saved_widget_states:
            if widget.winfo_exists():
                widget.configure(state=state)
        saved_widget_states = []


def run_task(work, success, label):
    if busy:
        return
    set_busy(True)
    show_status(label)
    progress_label.configure(text="")
    progress_label.pack(pady=5)
    def worker():
        try:
            result = work()
            ui_events.put(("success", (success, result)))
        except Exception as exc:
            import traceback
            traceback.print_exc()
            ui_events.put(("error", str(exc)))
    threading.Thread(target=worker, daemon=True).start()


def poll_events():
    global latest_version_number, latest_version_link
    try:
        # Limit each pass so a busy queue cannot starve Tk events.
        for _ in range(100):
            kind, payload = ui_events.get_nowait()
            if kind == "progress":
                progress_label.configure(text=payload)
            elif kind == "success":
                set_busy(False)
                progress_label.configure(text="")
                callback, result = payload
                callback(result)
            elif kind == "error":
                set_busy(False)
                progress_label.configure(text="")
                show_status("Operation failed. See the error details and try again.")
                messagebox.showerror("ZipTube error", payload)
            elif kind == "update":
                latest_version_number, latest_version_link = payload
    except queue.Empty:
        pass
    finally:
        app.after(100, poll_events)


def validated_url():
    url = entry_url.get().strip()
    if not url:
        raise ValueError("Paste a YouTube video link first.")
    if "://" not in url:
        url = "https://" + url
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in ("http", "https") or not (
            host in ("youtube.com", "youtu.be", "youtube-nocookie.com")
            or host.endswith(".youtube.com") or host.endswith(".youtube-nocookie.com")):
        raise ValueError("Enter a valid YouTube video link.")
    return url


def find_ffmpeg():
    suffix = ".exe" if os.name == "nt" else ""
    bundled = Path(resource_path("assets/ffmpeg/bin"))
    if all((bundled / (name + suffix)).is_file() for name in ("ffmpeg", "ffprobe")):
        return str(bundled / ("ffmpeg" + suffix)), str(bundled)
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return ffmpeg, None  # yt-dlp will find both using PATH.
    raise RuntimeError(
        "FFmpeg and ffprobe are required. Install both and add their bin folder to PATH, "
        "or put both executables (and any required DLLs) in assets/ffmpeg/bin. "
        "Restart ZipTube after installation.")


def base_download_options():
    options = {"noplaylist": True, "quiet": True, "no_warnings": False,
               "socket_timeout": 30, "retries": 3, "fragment_retries": 3,
               "js_runtimes": {"deno": {}}}
    # Explicitly enable supported alternatives if Deno is absent.
    if not shutil.which("deno") and shutil.which("node"):
        options["js_runtimes"] = {"node": {}}
    return options


def show_resolutions(info):
    global loaded_url, loaded_title
    loaded_url = info["url"]
    loaded_title = info["title"]
    for child in resolutions_frame.winfo_children():
        child.destroy()
    resolutions_var.set("")
    resolutions_frame.pack(pady=10)
    for i, height in enumerate(info["heights"]):
        value = f"{height}p"
        ctk.CTkRadioButton(resolutions_frame, text=value, variable=resolutions_var,
                          value=value, width=95).grid(row=i // 5, column=i % 5, padx=7, pady=6)
    download_button.configure(text="Download", state="normal",
                              command=lambda: download_video(resolutions_var))
    download_button.pack(pady=10)
    show_status(info["title"] + " — select a resolution.")


def start_download(audio_only=False, height=None):
    if busy:
        return
    try:
        url = validated_url()
        if not audio_only and url != loaded_url:
            raise ValueError("The video link changed. Load its resolutions again.")
        _, ffmpeg_location = find_ffmpeg()
    except (ValueError, RuntimeError) as exc:
        messagebox.showerror("Download", str(exc))
        return
    if url == loaded_url and loaded_title:
        choose_download_filename(url, loaded_title, audio_only, height, ffmpeg_location)
    else:
        run_task(lambda: fetch_download_title(url),
                 lambda title: choose_download_filename(url, title, audio_only, height, ffmpeg_location),
                 "Reading YouTube title…")


def fetch_download_title(url):
    with YoutubeDL(base_download_options()) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info or info.get("_type") in ("playlist", "multi_video"):
        raise ValueError("Please use a single video link, not a playlist.")
    return info.get("title") or info.get("id") or "YouTube"


def download_filename(title, audio_only, height=None):
    # Preserve spaces and Unicode; replace characters that Windows cannot save.
    title = sanitize_filename(title, restricted=False)
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", title).strip(" .") or "YouTube"
    # Leave room for the suffix and directory within typical Windows path limits.
    title = title[:150].rstrip(" .")
    if audio_only:
        return f"{title}_audio_{AUDIO_BITRATE}kbps.mp3"
    return f"{title}_video_{height}p.mp4"


def choose_download_filename(url, title, audio_only, height, ffmpeg_location):
    extension = ".mp3" if audio_only else ".mp4"
    destination = filedialog.asksaveasfilename(
        title="Save audio" if audio_only else "Save video",
        initialfile=download_filename(title, audio_only, height),
        defaultextension=extension, filetypes=[(extension[1:].upper(), "*" + extension)])
    if not destination:
        show_status("Download cancelled.")
        return
    if Path(destination).suffix.lower() != extension:
        messagebox.showerror("Filename", f"Please choose a filename ending in {extension}.")
        return
    run_task(lambda: perform_download(url, destination, audio_only, height, ffmpeg_location),
             lambda path: show_status(f"Download complete: {path}"), "Starting download…")


def perform_download(url, destination, audio_only, height, ffmpeg_location):
    # Separate temporary directory prevents clashes and protects an existing destination
    # until the entire operation succeeds. The save dialog handles overwrite consent.
    with tempfile.TemporaryDirectory(prefix="ziptube-", dir=str(Path(destination).parent)) as temp:
        options = base_download_options()
        options.update({"outtmpl": str(Path(temp) / "media.%(ext)s").replace("%", "%%").replace("%%(ext)s", "%(ext)s"),
                        "progress_hooks": [on_progress],
                        "postprocessor_hooks": [lambda data: ui_events.put(("progress", "Processing media…"))]})
        if ffmpeg_location:
            options["ffmpeg_location"] = ffmpeg_location
        if audio_only:
            options.update({"format": "bestaudio/best", "postprocessors": [
                {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": str(AUDIO_BITRATE)}]})
            extension = "mp3"
        else:
            # Require the exact selected height and audio. Prefer MP4-compatible streams.
            options.update({
                "format": (f"bestvideo[height={height}][ext=mp4]+bestaudio[ext=m4a]/"
                           f"best[height={height}][ext=mp4]/"
                           f"bestvideo[height={height}]+bestaudio/best[height={height}]"),
                "merge_output_format": "mp4",
                "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]})
            extension = "mp4"
        with YoutubeDL(options) as ydl:
            result = ydl.download([url])
        output = Path(temp) / ("media." + extension)
        if result or not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError("Download did not produce the requested file. See the terminal for details.")
        os.replace(output, destination)
    return destination


# Create a app window #
app = ctk.CTk()
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme(custom_theme if os.path.isfile(custom_theme) else "blue")

# Title of the window #
app.title(f"{app_name} {current_version} — Downloads")
if os.name == "nt" and os.path.isfile(icon):
    app.wm_iconbitmap(icon)

# Set min and max width and height #
min_max_height = 550
min_max_width = 750
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
    'start_menu': {'border_color': "orange"},
    'footer': {
        'font': ctk.CTkFont(family="calibri", size=11, weight="normal"),
        'border_color': "red",
        'height': 20,
        'width': 65
    }
}

def button_configurations(button_type):
    if button_type not in button_specifics:
        raise ValueError("Invalid button type")
    config = base_config.copy()
    config.update(button_specifics[button_type])
    return config

main_button_config = button_configurations('main')
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
start_menu_frame.pack(padx=10, pady=buttons_centered)

# Buttons for opening the sub-menus #
main_audio_button = ctk.CTkButton(start_menu_frame, text="Download Audio", command=download_audio_only, **start_menu_button_config)
main_video_button = ctk.CTkButton(start_menu_frame, text="Download Video", command=load_entry_and_resolutions_button, **start_menu_button_config)
main_video_button.grid(row=0, column=0, padx=5, pady=5)
main_audio_button.grid(row=0, column=1, padx=5, pady=5)

# Initialize the main frame #
footer_frame = ctk.CTkFrame(main_frame)
footer_frame.pack(side="bottom", pady=10)

# Bottom of the main screen donation and website buttons #
website_button = ctk.CTkButton(footer_frame, text="Website", command=lambda: open_webpage(website_url), **footer_button_config)
github_button = ctk.CTkButton(footer_frame, text="GitHub", command=lambda: open_webpage(github_url), **footer_button_config)
discord_button = ctk.CTkButton(footer_frame, text="Discord", command=lambda: open_webpage(discord_link), **footer_button_config)
donation_button = ctk.CTkButton(footer_frame, text="Donate", command=open_donation_window, **footer_button_config)
help_button = ctk.CTkButton(footer_frame, text="Help", command=open_help_window, **footer_button_config)
social_media_button = ctk.CTkButton(footer_frame, text="Share", command=show_social_media_window, **footer_button_config)
update_button = ctk.CTkButton(footer_frame, text="Update", command=latest_version, **footer_button_config)
color_theme_button = ctk.CTkButton(footer_frame, text="Dark / Light", command=toggle_appearance_mode, **footer_button_config)
website_button.grid(row=0, column=0, padx=5, pady=5)
github_button.grid(row=0, column=1, padx=5, pady=5)
discord_button.grid(row=0, column=2, padx=5, pady=5)
donation_button.grid(row=0, column=3, padx=5, pady=5)
help_button.grid(row=0, column=4, padx=5, pady=5)
social_media_button.grid(row=0, column=6, padx=5, pady=5)
update_button.grid(row=0, column=7, padx=5, pady=5)
color_theme_button.grid(row=0, column=8, padx=5, pady=5)

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
# disk_info_help_button = ctk.CTkButton(help_menu_frame, text="Disk Space Help", command=disk_space_help, font=("calibri", 15, "normal"), height=40, width=120, corner_radius=33, border_color="green")

# Create a button to always get the user back to the main menu #
back_to_menu_frame = ctk.CTkFrame(main_frame)
back_to_menu_button = ctk.CTkButton(back_to_menu_frame, text="Main Menu", command=back_main_menu_button, **main_button_config)

# Create a label and the entry widget for the video url #
entry_url = ctk.CTkEntry(main_frame, width=450, placeholder_text=("Paste URL here..."))

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
resolutions_var = ctk.StringVar(value="")

# Create a label and the progress bar to display the download progress #
progress_label = ctk.CTkLabel(main_frame, text="")

# Create the status label #
status_label = ctk.CTkLabel(main_frame, text="")

# Add social media sharing options
socials_image_sizes = size=(40, 40)
twitter_image = Image.open(resource_path("assets\\images\\twitter.png"))
twitter_image_pil = ctk.CTkImage(twitter_image, size=socials_image_sizes)
facebook_image = Image.open(resource_path("assets\\images\\facebook.png"))
facebook_image_pil = ctk.CTkImage(facebook_image, size=socials_image_sizes)
whatsapp_image = Image.open(resource_path("assets\\images\\whatsapp.png"))
whatsapp_image_pil = ctk.CTkImage(whatsapp_image, size=socials_image_sizes)
instagram_image = Image.open(resource_path("assets\\images\\instagram.png"))
instagram_image_pil = ctk.CTkImage(instagram_image, size=socials_image_sizes)

social_media_frame = ctk.CTkFrame(main_frame)
social_button_config = {
    'border_width': 0,
    'width': 0,
    'hover_color': ["gray86", "gray17"],
    'border_spacing': 0,
    'fg_color': "transparent",
}
twitter_button = ctk.CTkButton(social_media_frame, image=twitter_image_pil, text="", command=share_to_twitter, **social_button_config)
facebook_button = ctk.CTkButton(social_media_frame, image=facebook_image_pil, text="", command=share_to_facebook, **social_button_config)
instagram_button = ctk.CTkButton(social_media_frame, image=instagram_image_pil, text="", command=share_to_instagram, **social_button_config)
whatsapp_button = ctk.CTkButton(social_media_frame, image=whatsapp_image_pil, text="", command=share_to_whatsapp, **social_button_config)

# Add the on_close function to the close button #
app.protocol("WM_DELETE_WINDOW", on_close)

# Start the app #
if __name__ == "__main__":
    print(f"Running ZipTube {current_version} Downloads: {os.path.abspath(__file__)}")
    app.after(100, poll_events)
    check_for_updates()
    app.mainloop()
