import tkinter as tk
from tkinter import messagebox
import requests

def check_login():
    username = entry_user.get()
    password = entry_pw.get()
    
    # Kiểm tra tài khoản admin, mật khẩu 1
    if username == "admin" and password == "1":
        messagebox.showinfo("Thành công", "Đăng nhập thành công!")
    else:
        messagebox.showerror("Thất bại", "Sai tài khoản hoặc mật khẩu!")

# 1. Khởi tạo cửa sổ chính
root = tk.Tk()
root.title("Đăng Nhập Hệ Thống")
root.geometry("400x450")
root.configure(bg="#2c3e50") # Nàu nền tối sang trọng
root.attributes('-topmost', True)

# 2. Frame trung tâm (Chứa nội dung form)
login_frame = tk.Frame(root, bg="#ffffff", padx=40, pady=40)
login_frame.place(relx=0.5, rely=0.5, anchor="center")

# 3. Tiêu đề
lbl_title = tk.Label(
    login_frame, 
    text="ĐĂNG NHẬP", 
    font=("Segoe UI", 18, "bold"), 
    bg="#ffffff", 
    fg="#2c3e50"
)
lbl_title.pack(pady=(0, 30))

# 4. Ô nhập Tài khoản
tk.Label(login_frame, text="Tài khoản", bg="#ffffff", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w")
entry_user = tk.Entry(
    login_frame, 
    font=("Segoe UI", 12), 
    width=25, 
    bd=0, 
    highlightthickness=1, 
    highlightbackground="#dcdde1"
)
entry_user.pack(pady=(5, 15), ipady=5)
entry_user.insert(0, "admin") # Gợi ý sẵn tài khoản theo yêu cầu

# 5. Ô nhập Mật khẩu
tk.Label(login_frame, text="Mật khẩu", bg="#ffffff", fg="#7f8c8d", font=("Segoe UI", 10)).pack(anchor="w")
entry_pw = tk.Entry(
    login_frame, 
    font=("Segoe UI", 12), 
    width=25, 
    bd=0, 
    highlightthickness=1, 
    highlightbackground="#dcdde1",
    show="●" # Ẩn mật khẩu
)
entry_pw.pack(pady=(5, 25), ipady=5)

# 6. Nút bấm Đăng nhập
def on_enter(e):
    btn_login.config(bg="#2980b9")

def on_leave(e):
    btn_login.config(bg="#3498db")

btn_login = tk.Button(
    login_frame, 
    text="ĐĂNG NHẬP", 
    font=("Segoe UI", 11, "bold"),
    bg="#3498db", 
    fg="white", 
    bd=0, 
    width=20, 
    cursor="hand2",
    command=check_login
)
btn_login.pack(ipady=8)

# Gán hiệu ứng hover cho nút
btn_login.bind("<Enter>", on_enter)
btn_login.bind("<Leave>", on_leave)

# 7. Chân trang
tk.Label(root, text="Quên mật khẩu?", bg="#2c3e50", fg="#bdc3c7", font=("Segoe UI", 9), cursor="hand2").pack(side="bottom", pady=20)

root.mainloop()