import os
import customtkinter as ctk
import pyperclip

icon = "ziptube\\assets\\images\\icon.ico"
custom_theme = "ziptube\\assets\\themes\\custom.json"

# Function for donation window #
def open_donation_window():
    donation_window = ctk.CTk()
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme(custom_theme)
    donation_window.title("Please Donate ...")
    new_width = int(500)
    new_height = int(320)
    donation_window.geometry(f"{new_width}x{new_height}")
    donation_window.minsize(new_width, new_height)
    donation_window.maxsize(new_width, new_height)
    
    # Check if the icon file exists
    if os.path.exists(icon):
        donation_window.iconbitmap(icon)
    else:
        print(f"Icon file not found: {icon}")

    # Create a frame to hold the content #
    donation_frame = ctk.CTkFrame(donation_window)
    donation_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    # Create a label with the donation message #
    donation_label = ctk.CTkLabel(
        donation_frame,
        text="Enjoy using our app?? \nWould you like us to keep it well maintained? \n\nThen making a donation to one of our following wallets, \nwould help us out and would be greatly appreciated.",
        font=("calibri", 18),
        wraplength=new_width - 20
    )
    donation_label.pack(padx=10, pady=10)

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
    button_frame = ctk.CTkFrame(donation_frame)
    button_frame.pack(pady=10)

    # Create buttons to copy wallet addresses #
    for i, wallet in enumerate(wallets):
        copy_button = ctk.CTkButton(
            button_frame,
            text=f"{wallet['name']} Address",
            command=lambda name=wallet["name"], addr=wallet["address"]: copy_address(name, addr),
            font=("calibri", 15, "normal"),
            height=40, width=120, corner_radius=33, border_color="blue"
        )
        copy_button.grid(row=0, column=i, padx=5, pady=5)

    # Label to display "Copied to Clipboard" message #
    copied_label = ctk.CTkLabel(donation_frame, text="")
    copied_label.pack(pady=5)

    # Start the donation window's main loop #
    donation_window.mainloop()

if __name__ == "__main__":
    open_donation_window()
