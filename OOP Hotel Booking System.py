# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import os
from datetime import datetime

# Setup data directory
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)

# File paths
users_file = os.path.join(data_dir, 'users.xlsx')
rooms_file = os.path.join(data_dir, 'rooms.xlsx')
bookings_file = os.path.join(data_dir, 'bookings.xlsx')

# Initialize files if not exist
if not os.path.exists(users_file):
    pd.DataFrame(columns=['Username', 'Password', 'Email', 'Role']).to_excel(users_file, index=False)
if not os.path.exists(rooms_file):
    pd.DataFrame(columns=['RoomID', 'Type', 'Price', 'Status']).to_excel(rooms_file, index=False)
if not os.path.exists(bookings_file):
    pd.DataFrame(columns=['Username', 'RoomID', 'Check-in', 'Check-out']).to_excel(bookings_file, index=False)


class Room:
    def __init__(self):
        self.df = pd.read_excel(rooms_file)

    def save(self):
        self.df.to_excel(rooms_file, index=False)

    def add(self):
        room_id = input("Enter Room ID: ")
        if room_id in self.df['RoomID'].astype(str).values:
            print("Room ID already exists.")
            return
        room_type = input("Enter Room Type (Single/Double/Suite): ")
        price = input("Enter Price: ")
        new_room = pd.DataFrame([[room_id, room_type, price, 'Available']], columns=self.df.columns)
        self.df = pd.concat([self.df, new_room], ignore_index=True)
        self.save()
        print("Room added successfully.")

    def remove(self):
        room_id = input("Enter Room ID to remove: ")
        if room_id in self.df['RoomID'].astype(str).values:
            self.df = self.df[self.df['RoomID'].astype(str) != room_id]
            self.save()
            print("Room removed successfully.")
        else:
            print("Room not found.")

    def modify(self):
        room_id = input("Enter Room ID to modify: ")
        if room_id in self.df['RoomID'].astype(str).values:
            new_type = input("Enter new room type: ")
            new_price = input("Enter new price: ")
            idx = self.df[self.df['RoomID'].astype(str) == room_id].index[0]
            self.df.at[idx, 'Type'] = new_type
            self.df.at[idx, 'Price'] = new_price
            self.save()
            print("Room updated successfully.")
        else:
            print("Room not found.")

    def view_available(self):
        available = self.df[self.df['Status'] == 'Available']
        if available.empty:
            print("No rooms available.")
        else:
            print("Available Rooms:")
            print(available[['RoomID', 'Type', 'Price']].to_string(index=False))

    def book(self, username):
        bookings_df = pd.read_excel(bookings_file)
        self.view_available()
        room_id = input("Enter Room ID to book: ")

        if room_id not in self.df['RoomID'].astype(str).values:
            print("Invalid Room ID.")
            return

        if self.df.loc[self.df['RoomID'].astype(str) == room_id, 'Status'].values[0] == 'Booked':
            print("Room is already booked.")
            return

        try:
            checkin = input("Enter check-in date (YYYY-MM-DD): ")
            checkout = input("Enter check-out date (YYYY-MM-DD): ")
            datetime.strptime(checkin, "%Y-%m-%d")
            datetime.strptime(checkout, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format.")
            return

        new_booking = pd.DataFrame([[username, room_id, checkin, checkout]], columns=bookings_df.columns)
        bookings_df = pd.concat([bookings_df, new_booking], ignore_index=True)
        bookings_df.to_excel(bookings_file, index=False)

        self.df.loc[self.df['RoomID'].astype(str) == room_id, 'Status'] = 'Booked'
        self.save()
        print("Room booked successfully!")

    def view_bookings(self):
        bookings_df = pd.read_excel(bookings_file)
        if bookings_df.empty:
            print("No bookings available.")
        else:
            print("All Bookings:")
            print(bookings_df.to_string(index=False))

class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

    @staticmethod
    def register():
        users_df = pd.read_excel(users_file)
        username = input("Enter new username: ")
        if username in users_df['Username'].values:
            print("Username already exists.")
            return None

        password = input("Enter password: ")
        email = input("Enter email: ")

        if users_df.empty:
            role = 'admin'
            print("First user registered as admin.")
        elif 'admin' not in users_df['Role'].values:
            role = 'admin' if input("No admin exists. Make this user admin? (y/n): ").lower() == 'y' else 'user'
        else:
            role = 'user'

        new_user = pd.DataFrame([[username, password, email, role]], columns=users_df.columns)
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_excel(users_file, index=False)
        print(f"User '{username}' registered as {role}.")
        return AdminUser(username, role) if role == 'admin' else RegularUser(username, role)

    @staticmethod
    def login():
        users_df = pd.read_excel(users_file)
        username = input("Enter username: ")
        password = input("Enter password: ")

        if ((users_df['Username'] == username) & (users_df['Password'] == password)).any():
            role = users_df.loc[users_df['Username'] == username, 'Role'].values[0]
            print(f"Login successful as {role}!")
            return AdminUser(username, role) if role == 'admin' else RegularUser(username, role)
        else:
            print("Invalid credentials.")
            return None

class AdminUser(User):
    def __init__(self, username, role):
        super().__init__(username, role)
    def menu(self):
        room = Room()
        while True:
            print("\n--- Admin Menu ---")
            print("1. Add Room")
            print("2. Remove Room")
            print("3. Modify Room")
            print("4. View Bookings")
            print("5. Logout")
            choice = input("Enter choice: ")
            if choice == '1':
                room.add()
            elif choice == '2':
                room.remove()
            elif choice == '3':
                room.modify()
            elif choice == '4':
                room.view_bookings()
            elif choice == '5':
                break
            else:
                print("Invalid choice.")

class RegularUser(User):
    def __init__(self, username, role):
        super().__init__(username, role)
    def menu(self):
        room = Room()
        while True:
            print("\n--- User Menu ---")
            print("1. View Available Rooms")
            print("2. Book Room")
            print("3. Logout")
            choice = input("Enter choice: ")
            if choice == '1':
                room.view_available()
            elif choice == '2':
                room.book(self.username)
            elif choice == '3':
                break
            else:
                print("Invalid choice.")

def main_menu():
    while True:
        print("\n=== Hotel Booking System ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            user = User.register()
            if user:
                user.menu()
        elif choice == '2':
            user = User.login()
            if user:
                user.menu()
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
