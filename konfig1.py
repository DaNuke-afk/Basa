import os
import logging
import tkinter as tk
from tkinter import scrolledtext, filedialog
from pathlib import Path
import zipfile
import configparser

# Set up logging
logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(message)s')

def log_action(action):
    logging.info(action)

def list_directory(path=None):
    try:
        path = path or os.getcwd()
        entries = os.listdir(path)
        output = "\n".join(entries)
        return output
    except FileNotFoundError:
        return "Directory not found."
    except OSError as e:
        return f"Error accessing directory: {e}"


def change_directory(path):
    try:
        new_path = os.path.join(os.getcwd(), path)  #Correct path joining
        os.chdir(new_path)
        return f"Changed directory to: {os.getcwd()}"
    except FileNotFoundError:
        return "Directory not found."
    except OSError as e:
        return f"Error changing directory: {e}"


def echo_command(text):
    return text


def tree_command(path=None):
    try:
        path = path or os.getcwd()
        output = ""
        for root, dirs, files in os.walk(path):
            level = root.replace(path, '').count(os.sep)
            indent = ' ' * 4 * level
            output += f"{indent}{os.path.basename(root)}/\n"
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                output += f"{subindent}{f}\n"
        return output
    except FileNotFoundError:
        return "Directory not found."
    except OSError as e:
        return f"Error traversing directory: {e}"


def process_command(command):
    log_action(command)
    parts = command.split()
    command_name = parts[0]

    try:
        if command_name == "exit":
            app.quit()
        elif command_name == "ls":
            if len(parts) > 1:
                return list_directory(parts[1]) #Handles ls <directory>
            else:
                return list_directory()
        elif command_name == "cd":
            if len(parts) > 1:
                return change_directory(parts[1])
            else:
                return "cd requires a directory argument."
        elif command_name == "echo":
            return echo_command(" ".join(parts[1:]))
        elif command_name == "tree":
            if len(parts) > 1:
                return tree_command(parts[1])
            else:
                return tree_command()
        else:
            return "Command not recognized."
    except Exception as e:
                return f"An error occurred: {e}"


def on_enter(event):
    command = entry.get()
    entry.delete(0, tk.END)
    result = process_command(command)
    output_box.configure(state='normal')
    output_box.insert(tk.END, f"{Path.cwd()}/:> {command}\n{result}\n")
    output_box.configure(state='disabled')
    output_box.see(tk.END)


def load_vfs():
    config['DEFAULT']['vfs_path'] = filedialog.askopenfilename(filetypes=[("Zip files", "*.zip")])
    if config['DEFAULT']['vfs_path']:
        try:
            with zipfile.ZipFile(config['DEFAULT']['vfs_path'], 'r') as zip_ref:
                zip_ref.extractall("./vfs")
                os.chdir("./vfs") #change dir to the extracted vfs
                print(f"Virtual filesystem loaded from: {config['DEFAULT']['vfs_path']}")

        except FileNotFoundError:
            print("Error: Zip file not found.")
        except zipfile.BadZipFile:
            print("Error: Invalid zip file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


# --- GUI setup ---
app = tk.Tk()
app.title("Linux Console Emulator")
app.geometry("800x600")


# Config file handling
config = configparser.ConfigParser()
config.read('config.ini')

#If no config file, create it with defaults
if not config.has_section('DEFAULT'):
    config['DEFAULT'] = {'computer_name': 'MyVirtualMachine', 'vfs_path': '', 'log_file': 'log.txt'}
    with open('config.ini', 'w') as configfile:
        config.write(configfile)

# Menu
menubar = tk.Menu(app)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Load VFS", command=load_vfs)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=app.quit)
menubar.add_cascade(label="File", menu=filemenu)
app.config(menu=menubar)

# Output box
output_box = scrolledtext.ScrolledText(app, state='disabled', wrap=tk.WORD, height=20)
output_box.pack(fill=tk.BOTH, expand=True)

# Input field
entry = tk.Entry(app)
entry.pack(fill=tk.X)
entry.bind("<Return>", on_enter)

# Start the GUI
app.mainloop()