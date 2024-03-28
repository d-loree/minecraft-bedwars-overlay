from tkinter import *
from tkinter import ttk
import requests
from PIL import Image, ImageTk
from dotenv import load_dotenv
import os
import time
from threading import Thread
import re
import glob

load_dotenv()
API_KEY = os.getenv('HYPIXEL_API_KEY')
LOG_FILE_PATH = os.path.join(os.environ['APPDATA'], '.minecraft', 'logs', 'latest.log')
WINDOW_WIDTH = '800'
WINDOW_HEIGHT = '500'

current_usernames = set()

# Regex patterns
add_user_pattern = r"\[CHAT\] (\w+) (has joined|reconnected)"
remove_user_pattern = r"\[CHAT\] (\w+) (has quit|disconnected)"
remove_user_pattern_final_kill = r"\[CHAT\] (\w+) .*? FINAL KILL!"
clear_all_pattern_lobby = r"\[CHAT\] .*?joined the lobby!"
clear_all_pattern_sending = r"\[CHAT\] (Sending you to)"


def set_log_path(client):
    global LOG_FILE_PATH
    if client == "badlion":
        LOG_FILE_PATH = os.path.join(os.environ['APPDATA'], '.minecraft', 'logs', 'blclient', 'minecraft', 'latest.log')
    elif client == "lunar":
        logs_dir = os.path.join(os.environ['USERPROFILE'], '.lunarclient', 'logs', 'game')
        search_pattern = os.path.join(logs_dir, "*-master.log")
        log_files = glob.glob(search_pattern)
        LOG_FILE_PATH = log_files[0]
    else:
        LOG_FILE_PATH = os.path.join(os.environ['APPDATA'], '.minecraft', 'logs', 'latest.log')

def on_button_click_client(client):
    set_log_path(client)
    splash.destroy()
    display_window()

def display_choose_client():
    global splash
    splash = Tk()
    splash.title("Choose Client")
    splash.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')

    # Set bed icon for window GUI
    ico = Image.open('images/bed.png')
    photo = ImageTk.PhotoImage(ico)
    splash.wm_iconphoto(False, photo)

    # Create a main frame that will use grid for all its children
    main_frame = Frame(splash)
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    # Load and resize images for the buttons
    vanilla_img = ImageTk.PhotoImage(Image.open('images/vanilla.png').resize((150, 150)))
    badlion_img = ImageTk.PhotoImage(Image.open('images/badlion.png').resize((150, 150)))
    lunar_img = ImageTk.PhotoImage(Image.open('images/lunar.png').resize((150, 150)))

    # Title Label using grid within main frame
    titleLabel = Label(main_frame, text="Select your client", font=('Helvetica', 14, 'bold'))
    titleLabel.grid(row=0, column=0, columnspan=3, pady=(20, 10))  # Centered above the buttons

    button_style = ttk.Style()
    button_style.configure("CustomButton.TButton", font=('Helvetica', 14, 'bold'), background='black', foreground='black')

    # Buttons using grid within main frame
    ttk.Button(main_frame, image=vanilla_img, style="CustomButton.TButton",command=lambda: on_button_click_client(""), compound="top", text="Vanilla/Forge").grid(row=1, column=0, padx=10, pady=20)
    ttk.Button(main_frame, image=badlion_img, style="CustomButton.TButton", command=lambda: on_button_click_client("badlion"), compound="top", text="Badlion").grid(row=1, column=1, padx=10, pady=20)
    ttk.Button(main_frame, image=lunar_img, style="CustomButton.TButton", command=lambda: on_button_click_client("lunar"), compound="top", text="Lunar").grid(row=1, column=2, padx=10, pady=20)

    splash.mainloop()

def display_window():
    global window
    window = Tk()

    # Set bed icon for window GUI
    ico = Image.open('images/bed.png')
    photo = ImageTk.PhotoImage(ico)
    window.wm_iconphoto(False, photo)

    window.title("Bedwars Stats")
    window.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}')
    window.configure(bg="black")
    window.attributes('-topmost',True)

    # Initialize Treeview widget
    global table
    table = ttk.Treeview(window, columns=('Username', 'Level', 'FKDR', 'Winstreak', 'WLR'), show='headings')

    # Define headings and column configurations
    headings = ('Username', 'Level', 'FKDR', 'Winstreak', 'WLR')
    for heading in headings:
        table.heading(heading, text=heading, anchor='center')
        table.column(heading, anchor='center', width=100)

    # Create a dummy style with the same theme and apply it -> fix for tags not working
    style = ttk.Style(window)
    current_theme = style.theme_use()
    style.theme_create("dummy", parent=current_theme)
    style.theme_use("dummy")

    # Configure the Treeview colors
    style.configure("Treeview",
                    background="#121211",
                    foreground="white",
                    rowheight=28,  # Adjust the row height
                    fieldbackground="#D3D3D3")

    # Configure the Treeview heading colors and font
    style.configure("Treeview.Heading",
                    foreground="black",
                    font=('Helvetica', 10, 'bold'),
                    anchor="center")  # Center align the heading text

    style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])

    # Configure tags for row colors
    table.tag_configure('white_text', foreground='white')
    table.tag_configure('row_bg', background='#333333')
    table.tag_configure('danger_1', foreground='#42f557')
    table.tag_configure('danger_2', foreground='#f5ec42')
    table.tag_configure('danger_3', foreground='#ff1f1f')
    table.tag_configure('danger_4', foreground='#ff33f5')
    table.tag_configure('danger_5', foreground='#8e07e8')

    table.pack(fill='both', expand=True)

    # Monitor thread start
    monitor_thread = Thread(target=monitor_logs)
    monitor_thread.daemon = True
    monitor_thread.start()

    window.mainloop()

# Get player UUID from Mojang API (Because we need to lookup via UUID not username)
def get_uuid(username):
    response = requests.get(f'https://api.mojang.com/users/profiles/minecraft/{username}')
    if response.status_code == 200:
        return response.json().get('id')
    
# Fetch Bedwars stats for the given Player (Based on their UUID).
def get_bedwars_stats(uuid):
    response = requests.get(f'https://api.hypixel.net/player?key={API_KEY}&uuid={uuid}')
    if response.status_code == 200:
        player_data = response.json().get('player')
        if player_data and 'stats' in player_data and 'Bedwars' in player_data['stats']:

            player_final_kills = player_data['stats']['Bedwars'].get('final_kills_bedwars', 0)
            player_final_deaths = player_data['stats']['Bedwars'].get('final_deaths_bedwars', 1)
            player_fkdr = format(player_final_kills / player_final_deaths, '.2f')


            player_wins = player_data['stats']['Bedwars'].get('wins_bedwars', 0)
            player_losses = player_data['stats']['Bedwars'].get('losses_bedwars', 1)
            player_wlr = format(player_wins / player_losses, '.2f')

            
            player_winstreak = player_data['stats']['Bedwars'].get('winstreak', 0)
            if player_winstreak is None:
                player_winstreak = '?'
  
            player_level = player_data['achievements'].get('bedwars_level', 0)
            return player_level, player_fkdr, player_winstreak, player_wlr
    return '0', '0.00', '?', '0.00'

# Monitor Log File 
def monitor_logs():
    # Open log file to monitor for updates to add/remove users
    with open(LOG_FILE_PATH, 'r', encoding='utf-8', errors="ignore") as file:

        # Move to end of file for new logs
        file.seek(0, 2)

        while True:
                # Read next line
                line = file.readline()
                
                # Check if line is not empty
                if line:
                    # Check for clearing the table
                    match = re.search(clear_all_pattern_lobby, line)
                    match2 = re.search(clear_all_pattern_sending, line)
                    if match or match2:
                        clear_gui()

                    # Check if user types /who to reload all players
                    elif '[CHAT] ONLINE:' in line:
                        split_line = line.split('ONLINE:')
                        usernames_string = split_line[1]
                        usernames = [username.strip() for username in usernames_string.split(',')]
                        add_all_usernames(usernames)

                    # Conditions for adding a player
                    match = re.search(add_user_pattern, line)
                    if match:
                        username = match.group(1)
                        add_single_username(username)

                    # Conditions for removing a player
                    match = re.search(remove_user_pattern, line)
                    match2 = re.search(remove_user_pattern_final_kill, line)
                    if match:
                        username = match.group(1)
                        remove_single_username(username)
                    elif match2:
                        username = match2.group(1)
                        remove_single_username(username)
                else:
                    # If no new line, wait for a short time before checking again
                    time.sleep(1)

# Clear all table items
def clear_gui():
    for row in table.get_children():
        table.delete(row)
    current_usernames.clear()

# Remove user from table
def remove_single_username(username):
    for row in table.get_children():
        if username in table.item(row, 'values'):
            current_usernames.remove(username)
            table.delete(row)

# Add all usernames in list to table
def add_all_usernames(usernames):
    for username in usernames:
        insert_username_stats(username)

# Add user to table
def add_single_username(username):
    if username not in current_usernames:
        insert_username_stats(username)

# Logic for inserting a user into table
def insert_username_stats(username):
    if username not in current_usernames:
        current_usernames.add(username)
        uuid = get_uuid(username)
        player_level, player_fkdr, player_winstreak, player_wlr = get_bedwars_stats(uuid)

        table_values = (username, player_level, player_fkdr, player_winstreak, player_wlr)

        tags = ('row_bg',)

        # Color the rows text based on on high the users FKDR is
        if float(player_fkdr) >= 20:
            tags = tags + ('danger_5',)
        elif float(player_fkdr) >= 12:
            tags = tags + ('danger_4',)
        elif float(player_fkdr) >= 8:
            tags = tags + ('danger_3',)
        elif float(player_fkdr) >= 5:
            tags = tags + ('danger_2',)
        elif float(player_fkdr) >= 3:
            tags = tags + ('danger_1',)
        else:
            tags = tags + ('white_text',)

        # Sort by FKDR
        position = 'end'
        for index, item_id in enumerate(table.get_children()):
            item_values = table.item(item_id, 'values')
            current_fkdr = float(item_values[2])
            if float(player_fkdr) > current_fkdr:
                position = index
                break 

        # If no position found, then insert at end
        if position == 'end':
            table.insert('', 'end', values=table_values, tags=tags)
        else:
            table.insert('', position, values=table_values, tags=tags)

# Display the GUI
display_choose_client()