import os
import psutil
import cpuinfo
import customtkinter as ctk

def start_countdown(seconds, countdown_label, app):
    if seconds > 0:
        countdown_label.configure(text=f"Closing window in {seconds} seconds...")
        app.after(1000, start_countdown, seconds - 1, countdown_label, app)
    else:
        app.destroy()

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

def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    return {
        'brand': info['brand_raw'],
        'cores': psutil.cpu_count(logical=False),
        'threads': psutil.cpu_count(logical=True)
    }

def disks():
    ''' Icon and logo location on system '''
    app_name = "ZipTube"
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
    min_max_height = 600
    min_max_width = 550
    app.geometry(f"{min_max_width}x{min_max_height}")
    app.minsize(min_max_width, min_max_height)
    app.maxsize(min_max_width, min_max_height)

    ''' Create a frame to hold the content '''
    main_frame = ctk.CTkFrame(app)
    main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    ''' Create the labels '''
    status_label = ctk.CTkLabel(main_frame, font=("calibri", 18, "normal"), text="")
    status_label.pack(pady=10)
    countdown_label = ctk.CTkLabel(main_frame, font=("calibri", 18, "normal"), text="")
    countdown_label.pack(side='bottom', pady=10)

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
    start_countdown(20, countdown_label, app)

    # Start the main loop
    app.mainloop()

if __name__ == "__main__":
    disks()
