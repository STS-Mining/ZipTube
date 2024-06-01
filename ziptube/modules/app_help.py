import os
import customtkinter as ctk

def start_countdown(seconds, countdown_label, app):
    if seconds > 0:
        countdown_label.configure(text=f"Closing window in {seconds} seconds...")
        app.after(1000, start_countdown, seconds - 1, countdown_label, app)
    else:
        app.destroy()

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
    min_max_height = 680
    min_max_width = 700
    app.geometry(f"{min_max_width}x{min_max_height}")
    app.minsize(min_max_width, min_max_height)
    app.maxsize(min_max_width, min_max_height)

    ''' Create a frame to hold the content '''
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    ''' Create the labels '''
    status_label = ctk.CTkLabel(main_frame, font=("calibri", 17, "normal"), text="")
    status_label.pack(pady=10)
    countdown_label = ctk.CTkLabel(main_frame, font=("calibri", 17, "normal"), text="")
    countdown_label.pack(side='bottom', pady=10)

    # Gather information to display
    info_text = ""

    # About App Information
    info_text += "Download:\n"
    info_text += "-----------------------------------\n"
    info_text += "Here you can download almost any video from YouTube.\n"
    info_text += "Choose the resolution of the video you want to download.\n"
    info_text += "Choose where you want the files saved on your pc.\n"
    info_text += "Once complete you can download another video, or\n"
    info_text += "convert video to audio.\n"
    info_text += "This option will strip the audio from the video,\n"
    info_text += "and save it in mp3 format only.\n"
    info_text += "You can also choose to only download the audio only\n"
    info_text += "instead of the video.\n"
    info_text += "This is useful when downloading music files that you like.\n"
    info_text += "===============================================================\n"

    info_text += "\nConvertor:\n"
    info_text += "-----------------------------------\n"
    info_text += "Here you can convert almost any audio file to almost any other audio file.\n"
    info_text += "You can choose where you want the files saved on your pc.\n"
    info_text += "All files converted will be done in the best available bitrate.\n"
    info_text += "===============================================================\n"

    info_text += "\nDisk Space:\n"
    info_text += "-----------------------------------\n"
    info_text += "This option will give you basic information about your device.\n"
    info_text += "This will include all available disk drives,\n"
    info_text += "space available, and what cpu / processor is current.\n"
    info_text += "===============================================================\n"

    # Set the gathered information to the status_label
    status_label.configure(text=info_text)
    start_countdown(30, countdown_label, app)

    # Start the main loop
    app.mainloop()

if __name__ == "__main__":
    about_app()
