import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter import PhotoImage
import datetime

class FileManager:
    def __init__(self, root):
        self.root = root
        self.root.title("VILE: File Manager")
        self.root.geometry("1000x600")
        self.current_directory = os.getcwd()

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat", background="#444", foreground="white", font=("Helvetica", 10))
        self.style.map("TButton", background=[('active', '#555')])
        self.style.configure("TEntry", padding=6, font=("Helvetica", 10))
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))

        self.create_widgets()
        self.update_file_list()

    def create_widgets(self):
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        self.dir_entry = ttk.Entry(top_frame, width=100)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dir_entry.insert(0, self.current_directory)

        self.refresh_button = ttk.Button(top_frame, text="Refresh", command=self.update_file_list, style="TButton")
        self.refresh_button.pack(side=tk.LEFT, padx=5)

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame, padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.tree = ttk.Treeview(left_frame, show='tree')
        self.tree.pack(fill=tk.Y, expand=True)
        self.populate_tree()

        self.tree.bind('<<TreeviewSelect>>', self.change_directory)

        right_frame = ttk.Frame(main_frame, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        columns = ('Name', 'Date Modified', 'Type', 'Size')
        self.file_listbox = ttk.Treeview(right_frame, columns=columns, show='headings', style="Treeview")

        for col in columns:
            self.file_listbox.heading(col, text=col)
            if col == 'Size':
                self.file_listbox.column(col, width=70)
            else:
                self.file_listbox.column(col, width=150, anchor=tk.W)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=(5, 0))

        self.scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(5, 0))
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)

        self.file_listbox.bind('<Double-1>', self.open_item)

        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.new_file_button = ttk.Button(bottom_frame, text="New File", command=self.create_file, style="TButton")
        self.new_file_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(bottom_frame, text="Delete", command=self.delete_item, style="TButton")
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.new_dir_button = ttk.Button(bottom_frame, text="New Directory", command=self.create_directory, style="TButton")
        self.new_dir_button.pack(side=tk.LEFT, padx=5)

        self.rename_button = ttk.Button(bottom_frame, text="Rename", command=self.rename_item, style="TButton")
        self.rename_button.pack(side=tk.LEFT, padx=5)

    def populate_tree(self):
        self.tree.insert('', 'end', 'computer', text='Computer')
        home = os.path.expanduser("~")
        self.tree.insert('computer', 'end', 'Desktop', text='Desktop')
        self.tree.insert('computer', 'end', 'Documents', text='Documents')
        self.tree.insert('computer', 'end', 'Downloads', text='Downloads')
        self.tree.insert('computer', 'end', 'Music', text='Music')
        self.tree.insert('computer', 'end', 'Pictures', text='Pictures')
        self.tree.insert('computer', 'end', 'Videos', text='Videos')

    def change_directory(self, event):
        selected_item = self.tree.selection()[0]
        if selected_item == 'computer':
            return
        new_dir = self.tree.item(selected_item, 'text')
        home = os.path.expanduser("~")
        self.current_directory = os.path.join(home, new_dir)
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, self.current_directory)
        self.update_file_list()

    def update_file_list(self):
        for item in self.file_listbox.get_children():
            self.file_listbox.delete(item)
        self.current_directory = self.dir_entry.get()
        try:
            files_and_dirs = os.listdir(self.current_directory)
            files_and_dirs.sort(key=lambda x: os.path.getmtime(os.path.join(self.current_directory, x)), reverse=True)
            for item in files_and_dirs:
                item_path = os.path.join(self.current_directory, item)
                item_info = os.stat(item_path)
                item_type = "Folder" if os.path.isdir(item_path) else "File"
                item_size = self.format_size(item_info.st_size) if item_type == "File" else ""
                item_date = self.format_date(item_info.st_mtime)
                self.file_listbox.insert('', 'end', values=(item, item_date, item_type, item_size))
        except Exception as e:
            messagebox.showerror("Error", f"Unable to access directory: {e}")

    def format_date(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    def open_item(self, event):
        selected_item = self.file_listbox.item(self.file_listbox.selection()[0], 'values')[0]
        full_path = os.path.join(self.current_directory, selected_item)
        if os.path.isdir(full_path):
            self.current_directory = full_path
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, self.current_directory)
            self.update_file_list()
        else:
            os.startfile(full_path)

    def create_file(self):
        self.input_window = tk.Toplevel(self.root)
        self.input_window.title("New File")
        self.input_window.geometry("300x150")

        input_label = ttk.Label(self.input_window, text="Enter file name:", font=("Helvetica", 12))
        input_label.pack(pady=10)

        self.file_name_entry = ttk.Entry(self.input_window, width=30)
        self.file_name_entry.pack(pady=10)

        create_button = ttk.Button(self.input_window, text="Create", command=self.create_file_action, style="TButton")
        create_button.pack(pady=10)

    def create_file_action(self):
        file_name = self.file_name_entry.get()
        if file_name:
            new_file_path = os.path.join(self.current_directory, file_name)
            with open(new_file_path, 'w') as file:
                file.write('')
            self.update_file_list()
        self.input_window.destroy()

    def delete_item(self):
        selected_item = self.file_listbox.item(self.file_listbox.selection()[0], 'values')[0]
        full_path = os.path.join(self.current_directory, selected_item)
        if os.path.isdir(full_path):
            if os.listdir(full_path):
                if not messagebox.askyesno("Confirm Delete", f"Folder '{selected_item}' contains files. Do you want to delete it?"):
                    return
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete folder '{selected_item}'?"):
                try:
                    os.rmdir(full_path)
                except OSError as e:
                    messagebox.showerror("Error", f"Failed to delete directory: {e}")
        else:
            if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete file '{selected_item}'?"):
                os.remove(full_path)
        self.update_file_list()

    def create_directory(self):
        dir_name = simpledialog.askstring("New Directory", "Enter directory name:", parent=self.root)
        if dir_name:
            new_dir_path = os.path.join(self.current_directory, dir_name)
            os.mkdir(new_dir_path)
            self.update_file_list()

    def rename_item(self):
        selected_item = self.file_listbox.item(self.file_listbox.selection()[0], 'values')[0]
        new_name = simpledialog.askstring("Rename", "Enter new name:", parent=self.root)
        if new_name:
            full_path = os.path.join(self.current_directory, selected_item)
            new_path = os.path.join(self.current_directory, new_name)
            os.rename(full_path, new_path)
            self.update_file_list()

if __name__ == "__main__":
    root = tk.Tk()
    file_manager = FileManager(root)
    root.mainloop()