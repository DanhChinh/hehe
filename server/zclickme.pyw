import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import psutil
import time

class SystemMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title(f"System Monitor Pro: {time.strftime('%H:%M:%S', time.localtime(psutil.boot_time()))}")
        self.root.geometry("500x333")
        self.root.attributes('-topmost', True)

        # Đọc ảnh gốc (giữ kích thước thật)
        self.original_image = Image.open("zcat.jpg")

        # Label chứa ảnh nền
        self.bg_label = tk.Label(root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        # ===== Các thông tin =====
        font_main = ("Segoe UI", 12, "bold")
        font_small = ("Segoe UI", 11)

        self.info_label = tk.Label(root, text="Đang tải dữ liệu...", font=font_main,
                                   bg="#000000", fg="#FFFFFF")
        self.info_label.place(x=20, y=20)

        self.cpu_label = tk.Label(root, text="CPU Usage: 0%", font=font_main,
                                  bg="#000000", fg="#00AE72")
        self.cpu_label.place(x=20, y=60)

        self.temp_label = tk.Label(root, text="CPU Temp: -- °C", font=font_main,
                                   bg="#000000", fg="#FF5555")
        self.temp_label.place(x=20, y=100)

        self.net_label = tk.Label(root, text="Network: ↑ 0.00 MB/s | ↓ 0.00 MB/s",
                                  font=font_main, bg="#000000", fg="#33FFFF")
        self.net_label.place(x=20, y=140)

        self.ram_label = tk.Label(root, text="RAM Usage: 0%", font=font_main,
                                  bg="#000000", fg="#00FF00")
        self.ram_label.place(x=20, y=180)

 


        # ===== Network baseline =====
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()

        # Bind sự kiện resize cửa sổ
        self.root.bind("<Configure>", self.resize_background)

        # Bắt đầu cập nhật
        self.update_stats()

    # ===== Hàm lấy nhiệt độ CPU =====
    def get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for entries in temps.values():
                    if entries:
                        return f"{entries[0].current:.1f} °C"
        except Exception:
            pass
        return "Không hỗ trợ"

    # ===== Hàm lấy top process =====
    def get_top_process(self):
        top_proc = None
        max_cpu = 0
        for proc in psutil.process_iter(['name', 'cpu_percent']):
            try:
                cpu = proc.info['cpu_percent']
                if cpu is not None and cpu > max_cpu:
                    max_cpu = cpu
                    top_proc = proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if top_proc:
            return f"Top CPU Process: {top_proc} ({max_cpu:.1f}%)"
        return "Top CPU Process: --"

    # ===== Cập nhật số liệu =====
    def update_stats(self):
        # CPU
        cpu = psutil.cpu_percent()
        self.cpu_label.config(text=f"CPU Usage: {cpu}%")
        self.temp_label.config(text=f"CPU Temp: {self.get_cpu_temp()}")

        # RAM
        ram = psutil.virtual_memory()
        self.ram_label.config(text=f"RAM Usage: {ram.used//(1024**2)} / {ram.total//(1024**2)} MB ({ram.percent}%)")

        # Network
        now = time.time()
        net = psutil.net_io_counters()
        interval = now - self.last_time
        up = (net.bytes_sent - self.last_net.bytes_sent) / interval / (1024**2)
        down = (net.bytes_recv - self.last_net.bytes_recv) / interval / (1024**2)
        self.net_label.config(text=f"Network: ↑ {up:.2f} MB/s | ↓ {down:.2f} MB/s")
        self.last_net = net
        self.last_time = now


        # Extra info
        extra_info = f"CPU: {psutil.cpu_count(logical=False)} nhân | {psutil.cpu_count(logical=True)} luồng"
        self.info_label.config(text=extra_info)

        # Gọi lại sau 1 giây
        self.root.after(1000, self.update_stats)

    # ===== Hàm resize nền =====
    def resize_background(self, event):
        width = event.width
        height = event.height
        # Resize ảnh gốc theo window
        image = self.original_image.resize((width, height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(image)
        self.bg_label.config(image=self.bg_image)

# ===== Run app =====
if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitor(root)
    root.mainloop()
