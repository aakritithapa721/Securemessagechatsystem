import tkinter as tk
from datetime import datetime

class ChatUI:
    def __init__(self, root, username, send_callback):
        self.root = root
        self.username = username
        self.send_callback = send_callback
        self.current_chat = None
        self.chats = {}

        self.root.title(f"Secure Message Chat - {username}")
        self.root.geometry("900x550")
        self.root.configure(bg="#121212")  # dark background

        # LEFT: users
        left = tk.Frame(root, bg="#1f1f1f", width=250)
        left.pack(side="left", fill="y")

        tk.Label(left, text="Chats", bg="#1f1f1f",
                 fg="white", font=("Arial", 14, "bold")).pack(pady=10)

        self.user_list = tk.Listbox(left, font=("Arial", 12), bg="#2a2a2a", fg="white", selectbackground="#25D366")
        self.user_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.user_list.bind("<<ListboxSelect>>", self.open_chat)

        # RIGHT: messages
        right = tk.Frame(root, bg="#121212")
        right.pack(side="right", fill="both", expand=True)

        self.header = tk.Label(right, text="Select a chat",
                               bg="#075E54", fg="white",
                               font=("Arial", 14, "bold"), pady=10)
        self.header.pack(fill="x")

        # Chat area with canvas + scrollbar
        self.chat_canvas = tk.Canvas(right, bg="#121212", highlightthickness=0)
        self.chat_scrollbar = tk.Scrollbar(right, orient="vertical", command=self.chat_canvas.yview)
        self.chat_scrollbar.pack(side="right", fill="y")
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.chat_canvas.configure(yscrollcommand=self.chat_scrollbar.set)

        self.chat_frame = tk.Frame(self.chat_canvas, bg="#121212")
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))

        # Bottom input
        bottom = tk.Frame(right, bg="#121212")
        bottom.pack(fill="x", padx=10, pady=10)

        self.entry = tk.Entry(bottom, font=("Arial", 12), bg="#1f1f1f", fg="white", insertbackground="white")
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", self.send_message)

        tk.Button(bottom, text="Send", bg="#25D366",
                  fg="white", command=self.send_message).pack(side="right")

    # ---------- UI FUNCTIONS ----------
    def load_users(self, users):
        self.user_list.delete(0, tk.END)
        for u in users:
            if u != self.username:
                self.user_list.insert(tk.END, u)
                self.chats.setdefault(u, [])

    def open_chat(self, event):
        if not self.user_list.curselection():
            return
        self.current_chat = self.user_list.get(self.user_list.curselection())
        self.header.config(text=f"Chatting with {self.current_chat}")
        self.refresh_chat()

    def refresh_chat(self):
        for widget in self.chat_frame.winfo_children():
            widget.destroy()

        for sender, message in self.chats.get(self.current_chat, []):
            self.add_message_bubble(sender, message, from_refresh=True)

        self.chat_canvas.yview_moveto(1.0)

    def add_message(self, sender, message):
        self.chats.setdefault(sender, []).append((sender, message))
        if self.current_chat == sender or sender == self.username:
            self.add_message_bubble(sender, message)

    def add_message_bubble(self, sender, message, from_refresh=False):
        """Display a single message bubble in the chat frame"""
        timestamp = datetime.now().strftime("%H:%M")
        frame = tk.Frame(self.chat_frame, bg="#121212")
        bubble_color = "#056162" if sender == self.username else "#2a2a2a"
        text_color = "white"

        bubble = tk.Label(frame, text=f"{message}\n{timestamp}", bg=bubble_color, fg=text_color,
                          font=("Arial", 12), wraplength=400, justify="left", padx=10, pady=5)
        if sender == self.username:
            bubble.pack(anchor="e", padx=10, pady=2)
        else:
            bubble.pack(anchor="w", padx=10, pady=2)
        frame.pack(fill="both", expand=True)

        if not from_refresh:
            self.chat_canvas.update_idletasks()
            self.chat_canvas.yview_moveto(1.0)

    def send_message(self, event=None):
        if not self.current_chat:
            return
        msg = self.entry.get().strip()
        if not msg:
            return

        self.add_message(self.username, msg)
        self.send_callback(self.current_chat, msg)
        self.entry.delete(0, tk.END) 