import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from ttkthemes import ThemedStyle

# Database creation
conn = sqlite3.connect("atm.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_number TEXT,
                    pin TEXT,
                    balance REAL,
                    name TEXT,
                    contact TEXT,
                    address TEXT,
                    account_type TEXT
                )''')

# Customer Account Record
dummy_data = [
    ("123456", "1234", 1000.0, "Haroon Mahmood", "123-456-7890", "123 Main St, Sambrial", "Savings"),
    ("112233", "1122", 500.0, "Laiba Arshad", "987-654-3210", "37-D Bungalow Block-2, DHA Lhr", "Current"),
    ("100601", "2001", 1200.0, "Shahzeb Ali", "117-253-5417", "House 64/B Street 02, Gulberg-III Lhr", "Current")
]

for data in dummy_data:
    cursor.execute("INSERT INTO accounts (account_number, pin, balance, name, contact, address, account_type) VALUES (?, ?, ?, ?, ?, ?, ?)", data)

conn.commit()

class ATM:
    def __init__(self, root):
        self.root = root
        self.root.title("ATM Machine")
        self.root.geometry("400x300")

        # Create a themed style
        self.style = ThemedStyle(self.root)
        self.style.set_theme("vista")

        # Create and pack themed widgets
        self.label = ttk.Label(root, text="Enter Account Number:")
        self.label.pack(pady=10)

        self.account_entry = ttk.Entry(root)
        self.account_entry.pack(pady=10)

        self.pin_label = ttk.Label(root, text="Enter PIN:")
        self.pin_label.pack(pady=10)

        self.pin_entry = ttk.Entry(root, show="*")
        self.pin_entry.pack(pady=10)

        self.login_button = ttk.Button(root, text="Login", command=self.login)
        self.login_button.pack(pady=15)

    def login(self):
        account_number = self.account_entry.get()
        pin = self.pin_entry.get()

        # Check if the account exists
        cursor.execute("SELECT * FROM accounts WHERE account_number=? AND pin=?", (account_number, pin))
        account = cursor.fetchone()

        if account:
            self.show_menu(account)
        else:
            messagebox.showerror("Error", "Invalid account number or PIN")

    def show_menu(self, account):
        if hasattr(self, 'root') and self.root:
            self.root.destroy()  # Close the login window

        # window for the ATM menu
        menu_window = tk.Tk()
        menu_window.title("ATM Menu")
        menu_window.geometry("400x300")

        # style for the menu window
        menu_style = ThemedStyle(menu_window)
        menu_style.set_theme("vista")

        # Display account information
        account_label = ttk.Label(menu_window, text=f"Account Number: {account[1]}\nBalance: ${account[3]:.2f}")
        account_label.pack(pady=15)

        # Menu options
        check_balance_button = ttk.Button(menu_window, text="Check Balance", command=lambda: self.check_balance(account))
        check_balance_button.pack(pady=10)

        withdraw_button = ttk.Button(menu_window, text="Withdraw Money", command=lambda: self.withdraw_money(account))
        withdraw_button.pack(pady=10)

        transfer_button = ttk.Button(menu_window, text="Transfer Money", command=lambda: self.transfer_money(account))
        transfer_button.pack(pady=10)

        account_info_button = ttk.Button(menu_window, text="Account Information", command=lambda: self.show_account_info(account))
        account_info_button.pack(pady=10)

        logout_button = ttk.Button(menu_window, text="Logout", command=menu_window.destroy)
        logout_button.pack(pady=10)

        menu_window.mainloop()

    def check_balance(self, account):
        messagebox.showinfo("Balance", f"Your balance is: ${account[3]:.2f}")

    def withdraw_money(self, account):
        withdrawal_amount = simpledialog.askfloat("Withdrawal", "Enter the withdrawal amount:")
        if withdrawal_amount is not None:
            if withdrawal_amount > 0 and withdrawal_amount <= account[3]:
                new_balance = account[3] - withdrawal_amount
                cursor.execute("UPDATE accounts SET balance=? WHERE id=?", (new_balance, account[0]))
                conn.commit()
                messagebox.showinfo("Withdrawal", f"Withdrawal successful. New balance: ${new_balance:.2f}")
                self.show_menu((account[0], account[1], account[2], new_balance))
            else:
                messagebox.showerror("Error", "Invalid withdrawal amount or insufficient funds")

    def transfer_money(self, source_account):
        target_account_number = simpledialog.askstring("Transfer", "Enter the target account number:")
        if target_account_number is not None:
            # Check if the target account exists
            cursor.execute("SELECT * FROM accounts WHERE account_number=?", (target_account_number,))
            target_account = cursor.fetchone()

            if target_account:
                transfer_amount = simpledialog.askfloat("Transfer", "Enter the transfer amount:")
                if transfer_amount is not None:
                    if transfer_amount > 0 and transfer_amount <= source_account[3]:
                        # Perform the transfer
                        source_new_balance = source_account[3] - transfer_amount
                        target_new_balance = target_account[3] + transfer_amount

                        cursor.execute("UPDATE accounts SET balance=? WHERE id=?", (source_new_balance, source_account[0]))
                        cursor.execute("UPDATE accounts SET balance=? WHERE id=?", (target_new_balance, target_account[0]))

                        conn.commit()

                        messagebox.showinfo("Transfer", f"Transfer successful. New balance: ${source_new_balance:.2f}")
                        self.show_menu((source_account[0], source_account[1], source_account[2], source_new_balance))
                    else:
                        messagebox.showerror("Error", "Invalid transfer amount or insufficient funds")
            else:
                messagebox.showerror("Error", "Target account not found")

    def show_account_info(self, account):
        messagebox.showinfo("Account Information",
                            f"Account Number: {account[1]}\n"
                            f"Name: {account[4]}\n"
                            f"Contact: {account[5]}\n"
                            f"Address: {account[6]}\n"
                            f"Account Type: {account[7]}")

if __name__ == "__main__":
    root = tk.Tk()
    atm = ATM(root)
    root.mainloop()
