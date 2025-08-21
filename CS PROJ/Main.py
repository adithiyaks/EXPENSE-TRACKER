import csv
import sys  # To accept user ID from Login.py
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from PIL import Image, ImageTk
import subprocess
import tkinter.simpledialog as simpledialog

# CSV file setup
CSV_FILE = 'expenses.csv'
FIELDS = ['id','date', 'category', 'amount', 'note', 'userid']

# Get the User ID passed from Login.py
if len(sys.argv) > 1:
    CURRENT_USER = sys.argv[1]
else:
    CURRENT_USER = None


def add_expense():
    """Add new expense to CSV file"""
    if not CURRENT_USER:
        messagebox.showerror("Error", "User ID is missing!")
        return

    date_str = date_entry.get().strip()
    category = category_var.get()

    if category == 'Select Category':
        category = 'Other'
    if not date_str:
        date_str = date.today().strftime("%Y-%m-%d")

    note = note_entry.get("1.0", "end-1c")
    amount = amount_entry.get()

    if not amount.isdigit():
        messagebox.showerror("Invalid Input", "Amount must be a number!")
        return

    # Generate a new unique ID
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            Id = int(rows[-1]['id']) + 1 if rows else 1
            formatted_id = str(Id).zfill(3)

    except FileNotFoundError:
        formatted_id = '001'

    # Write the new expense to the CSV file
    try:
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'date', 'category', 'amount', 'note', 'userid'])
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow({
                'id': formatted_id,
                'date': date_str,
                'category': category,
                'amount': amount,
                'note': note,
                'userid': CURRENT_USER
            })
        messagebox.showinfo("Success", "Expense added successfully")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add expense: {e}")
    
    calculate_total()
    clear_fields()
    csvfile.close()

def view_expenses():
    """Display expenses for the logged-in user with dynamic Serial Numbers"""
    expense_window = tk.Toplevel(root)
    expense_window.title("Your Expenses")

    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader if row['userid'] == CURRENT_USER]  # Filter by logged-in user ID
    except FileNotFoundError:
        rows = []

    # Setup the Treeview
    tree = ttk.Treeview(expense_window, selectmode='browse')

    # Define columns
    tree['columns'] = ('S.No', 'ID', 'Date', 'Category', 'Amount', 'Note')

    # Format columns
    tree.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
    tree.column("S.No", anchor=tk.W, width=50)
    tree.column("ID", anchor=tk.W, width=50)
    tree.column("Date", anchor=tk.W, width=120)
    tree.column("Category", anchor=tk.W, width=100)
    tree.column("Amount", anchor=tk.W, width=80)
    tree.column("Note", anchor=tk.W, width=250)

    # Create column headings
    tree.heading("#0", text='', anchor=tk.W)
    tree.heading("S.No", text='S.No', anchor=tk.W)
    tree.heading("ID", text='ID', anchor=tk.W)
    tree.heading("Date", text='Date', anchor=tk.W)
    tree.heading("Category", text='Category', anchor=tk.W)
    tree.heading("Amount", text='Amount', anchor=tk.W)
    tree.heading("Note", text='Note', anchor=tk.W)

    # Add data to the Treeview with dynamic S.No
    sno = 1 
    for row in rows:
        
        
        tree.insert('', 'end', values=(sno, row['id'], row['date'], row['category'], row['amount'], row['note']))
        sno += 1
    # Pack the Treeview
    tree.pack(fill=tk.BOTH, expand=1, padx=10, pady=10)
    csvfile.close()

def delete_expense():
    """Delete an expense based on the entered ID and user ID."""
    if not CURRENT_USER:
        messagebox.showerror("Error", "User ID is missing!")
        return

    # Prompt the user to enter the ID of the expense to delete
    expense_id = simpledialog.askstring("Delete Expense", "Enter the ID of the expense to delete:")
    if not expense_id:
        messagebox.showerror("Error", "Expense ID is required!")
        return

    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

        # Filter out the expense to delete
        updated_rows = [row for row in rows if not (row['id'] == expense_id and row['userid'] == CURRENT_USER)]

        # Check if the expense with the given ID was found and deleted
        if len(rows) == len(updated_rows):
            messagebox.showinfo("Not Found", "No expense found with the provided ID for the current user!")
            return

    except FileNotFoundError:
        messagebox.showerror("Error", "No expenses recorded yet!")
        return

    # Write the updated rows back to the CSV file
    try:
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'date', 'category', 'amount', 'note', 'userid'])
            writer.writeheader()
            writer.writerows(updated_rows)
        messagebox.showinfo("Success", "Expense deleted successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete expense: {e}")

def edit_expense():
    """Edit an expense based on the unique ID"""
    from tkinter import simpledialog

    if not CURRENT_USER:
        messagebox.showerror("Error", "User ID is missing!")
        return

    # Ask the user for the ID of the expense to edit
    expense_id = simpledialog.askstring("Edit Expense", "Enter the ID of the expense to edit:")
    
    if not expense_id:
        return

    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

        expense_found = False
        for row in rows:
            if int(row['id']) == int(expense_id) and row['userid'] == CURRENT_USER:
                expense_found = True
                # Prompt the user for new details
                new_date = simpledialog.askstring("Edit Expense", "Enter new date (YYYY-MM-DD):", initialvalue=row['date'])
                new_category = simpledialog.askstring("Edit Expense", "Enter new category:", initialvalue=row['category'])
                new_amount = simpledialog.askfloat("Edit Expense", "Enter new amount:", initialvalue=row['amount'])
                new_note = simpledialog.askstring("Edit Expense", "Enter new note:", initialvalue=row['note'])
                
                # Update the row
                row['date'] = new_date or row['date']
                row['category'] = new_category or row['category']
                row['amount'] = new_amount or row['amount']
                row['note'] = new_note or row['note']
                break

        if not expense_found:
            messagebox.showerror("Error", "Expense not found or you don't have permission to edit it!")
            return

        # Save updated data back to the file
        with open(CSV_FILE, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['id', 'date', 'category', 'amount', 'note', 'userid'])
            writer.writeheader()
            writer.writerows(rows)

        messagebox.showinfo("Success", "Expense updated successfully!")

    except FileNotFoundError:
        messagebox.showerror("Error", "Expense file not found!")

def calculate_total():
    """Calculate total spend from CSV file for a specific user"""
    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            # Filter rows by the current user's ID and sum the 'amount' column
            total_spend = sum(float(row['amount']) for row in reader if row['userid'] == CURRENT_USER)
    except FileNotFoundError:
        total_spend = 0

    total_label.config(text=f"Total Spend: ₹{total_spend:.2f}")

def clear_fields():
    """Clear input fields"""
    category_var.set("Select Category")
    amount_entry.delete(0, tk.END)
    note_entry.delete("1.0", tk.END)
    date_entry.delete("0", tk.END)

def show_category_analysis():
    """Display pie chart for the current user's expenses"""
    if not CURRENT_USER:
        messagebox.showerror("Error", "User ID is missing!")
        return

    try:
        with open(CSV_FILE, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = [row for row in reader if row['userid'] == CURRENT_USER]
    except FileNotFoundError:
        rows = []

    category_expenses = {}
    for row in rows:
        category = row['category']
        amount = float(row['amount'])
        category_expenses[category] = category_expenses.get(category, 0) + amount

    if not category_expenses:
        messagebox.showinfo("Info", "No data to display!")
        return

    categories = list(category_expenses.keys())
    amounts = list(category_expenses.values())

    # Create a new window for the analysis
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Category Analysis")
    analysis_window.geometry('750x550')

    # Create a figure for the pie chart
    fig = Figure(figsize=(6, 6), dpi=100)
    ax = fig.add_subplot(111)

    # Create the pie chart
    wedges, texts , autotexts= ax.pie(amounts, colors=plt.cm.tab20.colors[:len(categories)], startangle=90,autopct='%1.1f%%')
    ax.axis('equal')  # Equal aspect ratio ensures the pie is a circle
    ax.set_title('Expense Distribution by Category')

    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontsize(9)
        

    # Add a legend
    ax.legend(wedges, categories, title="Categories", loc="center left", bbox_to_anchor=(-0.14,0, 0, 1))

    # Add the pie chart to the tkinter window
    canvas = FigureCanvasTkAgg(fig, master=analysis_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


def logout():
    """Close the main window and reopen the login page."""
    root.destroy()
    subprocess.Popen(['python', 'Login.py'])

# Main UI
root = tk.Tk()
root.title("Expense Tracker")

# Load the background image
image_path = 'cg3.png'
image = Image.open(image_path)

# Resize the image if necessary to fit the window size
# Comment this section out if you want the image to retain its original size
window_width = 550
window_height = 450
image.thumbnail((window_width, window_height))  # Resize keeping aspect ratio
image = image.resize((window_width, window_height))  # Resize to exact fit (may distort image)

# Convert the image to a format tkinter can use
tk_image = ImageTk.PhotoImage(image)

# Create a Label with the image
background_label = tk.Label(root, image=tk_image)
background_label.image = tk_image  # Keep a reference to prevent garbage collection
background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Fill the window

# Input Frames
input_frame = tk.Frame(root,bg='#e2e9ec',width=500, height=300,bd=3, relief="raised")
input_frame.pack(padx=30, pady=30,fill=tk.Y)
input_frame.pack_propagate(False)  

tk.Label(input_frame, text="Category:",bg='#D3D3D3').grid(column=0, row=0,pady=8,padx=10)
category_var = tk.StringVar(input_frame)
category_var.set("Select Category")  
category_option = tk.OptionMenu(input_frame, category_var, "Food", "Transport", "Entertainment", "Other")
category_option.grid(column=1, row=0)

tk.Label(input_frame, text="Amount:",bg='#D3D3D3').grid(column=0, row=1,pady=12)
amount_entry = tk.Entry(input_frame)
amount_entry.grid(column=1, row=1,pady=12,padx=5)

tk.Label(input_frame, text="Date (YYYY-MM-DD):",bg='#D3D3D3').grid(column=0, row=2,padx= 10)
date_entry = tk.Entry(input_frame)
date_entry.grid(column=1, row=2)

tk.Label(input_frame, text="Note:",bg='#D3D3D3').grid(column=0, row=4,pady=1)
note_entry = tk.Text(input_frame, width=20, height=5)
note_entry.grid(column=1, row=4,pady=10,padx=10)

# Buttons
button_frame = tk.Frame(root,bg='#e2e9ec',bd=3, relief="raised")
button_frame.pack(padx=10, pady=10)

add_button = tk.Button(button_frame, text="Add Expense", command=add_expense,bd=3)
add_button.pack(side=tk.LEFT, padx=5)

view_button = tk.Button(button_frame, text="View Expenses", command=view_expenses,bd=3)
view_button.pack(side=tk.LEFT, padx=5)

total_button = tk.Button(button_frame, text="Edit Expense", command=edit_expense,bd=3)
total_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(button_frame, text="Delete Expense", command=delete_expense,bd=3)
clear_button.pack(side=tk.LEFT, padx=5)

analysis_button = tk.Button(button_frame, text="Category Analysis", command=show_category_analysis,bd=3)
analysis_button.pack(side=tk.LEFT, padx=5)

# Logout Button
tk.Button(root, text="Logout", command=logout, bg="#ffcccc", bd=3).pack(pady=10)

# Total Spend Label
total_label = tk.Label(root, text="Total Spend: ₹0.00",bg='#e2e9ec',bd=3, relief="raised")
total_label.pack(pady=10)

root.mainloop()