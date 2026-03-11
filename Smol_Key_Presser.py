import ctypes
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

COUNTDOWN_SECONDS = 5

# Windows virtual-key codes for F13-F24
VK_CODES = {
    "F13": 0x7C,
    "F14": 0x7D,
    "F15": 0x7E,
    "F16": 0x7F,
    "F17": 0x80,
    "F18": 0x81,
    "F19": 0x82,
    "F20": 0x83,
    "F21": 0x84,
    "F22": 0x85,
    "F23": 0x86,
    "F24": 0x87,
}

user32 = ctypes.windll.user32
KEYEVENTF_KEYUP = 0x0002


def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def send_virtual_key(vk_code: int) -> None:
 # If you see this, know that these next two lines are literally the whole point, the rest is BUTTONS AAAHHH
    user32.keybd_event(vk_code, 0, 0, 0)  # key down
    user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)  # key up


class CountdownWindow(tk.Toplevel):
    def __init__(self, parent: tk.Tk, fn_key: str) -> None:
        super().__init__(parent)
        self.parent = parent
        self.fn_key = fn_key
        self.remaining = COUNTDOWN_SECONDS

        self.title("Smol Key Presser")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.iconbitmap(resource_path("VS_FN_Logo.ico"))
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.columnconfigure(0, weight=1)

        ttk.Label(
            self,
            text="Start listening for a keypress in your app!",
            anchor="center",
            font=("Comic Sans MS", 11, "bold"),
        ).grid(row=0, column=0, padx=20, pady=(15, 8), sticky="ew")

        self.message_label = ttk.Label(
            self,
            text="",
            anchor="center",
            font=("Comic Sans MS", 10),
        )
        self.message_label.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.progress = ttk.Progressbar(
            self,
            mode="determinate",
            maximum=COUNTDOWN_SECONDS,
            length=320,
        )
        self.progress.grid(row=2, column=0, padx=20, pady=(0, 15))

        self.center_window()
        self.update_countdown()

    def center_window(self) -> None:
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def update_countdown(self) -> None:
        if self.remaining > 0:
            self.message_label.config(
                text=f"Sending {self.fn_key} in {self.remaining} second(s)..."
            )
            self.progress["value"] = COUNTDOWN_SECONDS - self.remaining
            self.remaining -= 1
            self.after(1000, self.update_countdown)
            return

        self.message_label.config(text=f"Sending {self.fn_key} now...")
        self.progress["value"] = COUNTDOWN_SECONDS
        self.after(500, self.send_key)

    def send_key(self) -> None:
        try:
            vk_code = VK_CODES[self.fn_key]
            send_virtual_key(vk_code)
            self.message_label.config(text=f"{self.fn_key} sent.")
            self.after(1200, self.finish)
        except Exception as exc:
            messagebox.showerror("Error", f"Failed to send {self.fn_key}.\n\n{exc}")
            self.finish()

    def cancel(self) -> None:
        self.finish()

    def finish(self) -> None:
        self.destroy()
        self.parent.deiconify()
        self.parent.lift()
        self.parent.attributes("-topmost", True)
        self.parent.after(200, lambda: self.parent.attributes("-topmost", True))


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("Smol Key Presser Selection Menu")
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.iconbitmap(resource_path("VS_FN_Logo.ico"))

        container = ttk.Frame(self, padding=16)
        container.grid(row=0, column=0, sticky="nsew")

        ttk.Label(
            container,
            text="Pick your key! It will be pressed after 5 seconds.",
            anchor="center",
            font=("Comic Sans MS", 10),
        ).grid(row=0, column=0, columnspan=4, pady=(0, 12))

        keys = list(VK_CODES.keys())

        for index, key_name in enumerate(keys):
            row = (index // 4) + 1
            col = index % 4
            btn = ttk.Button(
                container,
                text=key_name,
                command=lambda k=key_name: self.start_countdown(k),
                width=10,
            )
            btn.grid(row=row, column=col, padx=6, pady=6)

        ttk.Button(
            container,
            text="Exit",
            command=self.destroy,
            width=10,
        ).grid(row=4, column=0, columnspan=4, pady=(12, 0))

        self.center_window()

    def center_window(self) -> None:
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def start_countdown(self, fn_key: str) -> None:
        self.withdraw()
        CountdownWindow(self, fn_key)


if __name__ == "__main__":
    app = App()
    app.mainloop()