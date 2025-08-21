import tkinter as tk
from tkinter import messagebox
import csv
import os
from PIL import Image, ImageTk

# File for storing login credentials
CREDENTIALS_FILE = 'login_credentials.csv'

# Ensure credentials file exists
if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['userid', 'fullname', 'password'])
        writer.writeheader()

# Function to verify login credentials
def login():
    userid = userid_entry.get().strip()
    password = password_entry.get().strip()

    if not userid or not password:
        messagebox.showerror("Login Failed", "User ID and Password cannot be empty!")
        return

    with open(CREDENTIALS_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['userid'] == userid and row['password'] == password:
                messagebox.showinfo("Login Success", f"Welcome, {row['fullname']}!")
                root.destroy()  # Close login window
                open_main_window(userid)  # Open main window
                return

    messagebox.showerror("Login Failed", "Invalid User ID or Password!")

# Function to create a new account
def create_account():
    def save_account():
        new_userid = userid_entry_new.get().strip()
        fullname = fullname_entry_new.get().strip()
        new_password = password_entry_new.get().strip()

        if not new_userid or not fullname or not new_password:
            messagebox.showerror("Error", "All fields are required!")
            return

        # Check if User ID already exists
        with open(CREDENTIALS_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['userid'] == new_userid:
                    messagebox.showerror("Error", "User ID already exists!")
                    return

        # Save the new account
        with open(CREDENTIALS_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['userid', 'fullname', 'password'])
            writer.writerow({'userid': new_userid, 'fullname': fullname, 'password': new_password})

        messagebox.showinfo("Success", "Account created successfully!")
        create_window.destroy()

    # Open a new window for account creation
    create_window = tk.Toplevel(root)
    create_window.title("Create New Account")
    create_window.geometry("300x250")

    tk.Label(create_window, text="User ID:").pack(pady=5)
    userid_entry_new = tk.Entry(create_window, width=30)
    userid_entry_new.pack(pady=5)

    tk.Label(create_window, text="Full Name:").pack(pady=5)
    fullname_entry_new = tk.Entry(create_window, width=30)
    fullname_entry_new.pack(pady=5)

    tk.Label(create_window, text="Password:").pack(pady=5)
    password_entry_new = tk.Entry(create_window, show="*", width=30)
    password_entry_new.pack(pady=5)

    tk.Button(create_window, text="Create Account", command=save_account, width=20).pack(pady=10)

# Function to open the main window
def open_main_window(userid):
    import subprocess
    subprocess.Popen(['python', 'Main.py', userid])

# Setup the login UI
root = tk.Tk()
root.title("Login Page")
root.geometry("300x320")

image_path = 'cg.png'
image = Image.open(image_path)

window_width = 360
window_height = 550
image.thumbnail((window_width, window_height))  # Resize keeping aspect ratio
image = image.resize((window_width, window_height))

tk_image = ImageTk.PhotoImage(image)

background_label = tk.Label(root, image=tk_image)
background_label.image = tk_image  # Keep a reference to prevent garbage collection
background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Fill the window

tk.Label(root, text="Expense Tracker Login", font=("Arial", 14),bd=1, relief="solid").pack(pady=30)

tk.Label(root, text="User ID:").pack(side='top',anchor='nw',padx= 59)
userid_entry = tk.Entry(root, width=30)
userid_entry.pack(pady=5)

tk.Label(root, text="Password:").pack(side='top',anchor='nw',padx= 59)
password_entry = tk.Entry(root, show="*", width=30)
password_entry.pack(pady=5)

tk.Button(root, text="Login", command=login, width=15,bd=3, relief="raised").pack(pady=20)
tk.Button(root, text="Create New Account", command=create_account, width=20,bd=3, relief="raised").pack(pady=5)

root.mainloop()
