import tkinter as tk
from tkinter import ttk
import psutil
import threading
import time

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor Pro")
        self.root.geometry("400x350")
        self.root.attributes('-topmost', True)
        self.root.configure(bg="#1e1e1e") # Nền tối hiện đại
        
        # Style cho Progressbar
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TProgressbar", thickness=20)

        # --- Giao diện CPU ---
        self.cpu_label = tk.Label(root, text="CPU Usage: 0%", font=("Segoe UI", 12), bg="#1e1e1e", fg="#00d4ff")
        self.cpu_label.pack(pady=(20, 5))
        self.cpu_bar = ttk.Progressbar(root, length=300, mode='determinate')
        self.cpu_bar.pack(pady=5)

        # --- Giao diện RAM ---
        self.ram_label = tk.Label(root, text="RAM Usage: 0%", font=("Segoe UI", 12), bg="#1e1e1e", fg="#00ff00")
        self.ram_label.pack(pady=(20, 5))
        self.ram_bar = ttk.Progressbar(root, length=300, mode='determinate')
        self.ram_bar.pack(pady=5)

        # --- Thông tin bổ sung ---
        self.info_label = tk.Label(root, text="Đang tải dữ liệu...", font=("Segoe UI", 10), bg="#1e1e1e", fg="#aaaaaa", justify="left")
        self.info_label.pack(pady=20)

        # Khởi chạy luồng cập nhật dữ liệu
        self.update_stats()

    def update_stats(self):
        # Lấy thông tin CPU
        cpu_usage = psutil.cpu_percent()
        self.cpu_label.config(text=f"CPU Usage: {cpu_usage}%")
        self.cpu_bar['value'] = cpu_usage

        # Lấy thông tin RAM
        ram = psutil.virtual_memory()
        self.ram_label.config(text=f"RAM Usage: {ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)")
        self.ram_bar['value'] = ram.percent

        # Lấy thông tin chi tiết khác (Số nhân, Tốc độ...)
        boot_time = time.strftime("%H:%M:%S", time.localtime(psutil.boot_time()))
        extra_info = (
            f"Số nhân CPU: {psutil.cpu_count(logical=False)} | "
            f"Luồng: {psutil.cpu_count(logical=True)}\n"
            f"Thời gian hoạt động từ: {boot_time}"
        )
        self.info_label.config(text=extra_info)

        # Đệ quy gọi lại sau 1000ms (1 giây)
        self.root.after(1000, self.update_stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()