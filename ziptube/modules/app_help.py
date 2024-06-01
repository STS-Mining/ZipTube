import os
import customtkinter as ctk

def start_countdown(seconds, countdown_label, app, callback):
    if seconds > 0:
        countdown_label.configure(text=f"Returning to menu in {seconds} seconds...")
        app.after(1000, start_countdown, seconds - 1, countdown_label, app, callback)
    else:
        callback()

def about_app():
    ''' Icon and logo location on system '''
    app_name = "ZipTube - Help"
    icon_path = "ziptube\\assets\\images\\icon.ico"
    custom_theme = "ziptube\\assets\\themes\\custom.json"

    ''' Create a app window '''
    app = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(custom_theme)

    ''' Title of the window '''
    app.title(app_name)

    ''' Check if the icon file exists '''
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)
    else:
        print(f"Icon file not found: {icon_path}")

    ''' Set min and max width and height '''
    min_max_height = 300
    min_max_width = 600
    app.geometry(f"{min_max_width}x{min_max_height}")
    app.minsize(min_max_width, min_max_height)
    app.maxsize(min_max_width, min_max_height)

    ''' Create a frame to hold the content '''
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    # Initialize the main menu frame #
    start_menu_frame = ctk.CTkFrame(main_frame)
    start_menu_frame.pack(padx=10, pady=100)

    # Label to display help information
    info_label = ctk.CTkLabel(main_frame, font=("calibri", 17, "normal"), text="")
    info_label.pack(pady=10)

    # Buttons for opening the sub-menus #
    youtube_downloader_help_button = ctk.CTkButton(start_menu_frame, text="Download Help", command=lambda: show_youtube_downloader_help(info_label, app), font=("calibri", 15, "normal"), height=40, width=120, corner_radius=33, border_color="green")
    converters_help_button = ctk.CTkButton(start_menu_frame, text="Convertor Help", command=lambda: show_converters_help(info_label, app), font=("calibri", 15, "normal"), height=40, width=120, corner_radius=33, border_color="green")
    disk_info_help_button = ctk.CTkButton(start_menu_frame, text="Disk Space Help", command=lambda: check_disk_space_help(info_label, app), font=("calibri", 15, "normal"), height=40, width=120, corner_radius=33, border_color="green")
    youtube_downloader_help_button.grid(row=0, column=0, padx=5, pady=5)
    converters_help_button.grid(row=0, column=1, padx=5, pady=5)
    disk_info_help_button.grid(row=0, column=2, padx=5, pady=5)

    ''' Create the countdown label '''
    countdown_label = ctk.CTkLabel(main_frame, font=("calibri", 17, "normal"), text="")
    countdown_label.pack(side='bottom', pady=10)
    countdown_timer = 15  # set timer in seconds for screen to go back to menu

    def reset_to_menu():
        app.title(app_name)
        info_label.pack_forget()
        countdown_label.pack_forget()
        info_label.configure(text="")
        countdown_label.configure(text="")
        start_menu_frame.pack(padx=10, pady=100)

    # Function to display YouTube downloader help
    def show_youtube_downloader_help(label, app):
        app.title("ZipTube - Help - Downloader")
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
        start_menu_frame.pack_forget()
        label.configure(text=info_text)
        info_label.pack(pady=10)
        countdown_label.pack(side='bottom', pady=10)
        start_countdown(countdown_timer, countdown_label, app, reset_to_menu)

    # Function to display converters help
    def show_converters_help(label, app):
        app.title("ZipTube - Help - Convertor")
        info_text = (
            "\nHow to use the convertors:\n\n"
            "Here you can convert almost any audio file to almost any other audio file.\n"
            "You can choose where you want the files saved on your pc.\n"
            "All files converted will be done in the best available bitrate.\n"
        )
        start_menu_frame.pack_forget()
        label.configure(text=info_text)
        info_label.pack(pady=10)
        countdown_label.pack(side='bottom', pady=10)
        start_countdown(countdown_timer, countdown_label, app, reset_to_menu)

    # Function to display disk space help
    def check_disk_space_help(label, app):
        app.title("ZipTube - Help - Disk Space")
        info_text = (
            "\nHow to use the disk space utility:\n\n"
            "This option will give you basic information about your device.\n"
            "This will include all available disk drives, space available,\n"
            "and what cpu / processor is currently installed on your machine.\n"
        )
        start_menu_frame.pack_forget()
        label.configure(text=info_text)
        info_label.pack(pady=10)
        countdown_label.pack(side='bottom', pady=10)
        start_countdown(countdown_timer, countdown_label, app, reset_to_menu)

    # Start the main loop
    app.mainloop()

if __name__ == "__main__":
    about_app()
