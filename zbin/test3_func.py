import math

# Giả lập mảng chứa lịch sử giá (ví dụ có 32 bước giá)
# Hàm này sử dụng cửa sổ trượt window_size = 5 để bạn dễ cộng trừ nhẩm
window_size = 5
lich_su_gia = [10, 11, 10, 12, 11, 15, 9] 
# Ta sẽ tính toán tại thời điểm bước giá thứ 6 (khi giá nhảy lên 15) và thứ 7 (khi giá sập về 9)

def giai_thich_tinh_toan_chi_so_toan_hoc(lich_su_gia, window_size):
    print(f"=== ĐẦU VÀO: Lịch sử giá hiện tại có {len(lich_su_gia)} phần tử ===")
    print(f"Toàn bộ mảng giá: {lich_su_gia}\n")

    # BƯỚC 1: Kiểm tra điều kiện đủ dữ liệu
    if len(lich_su_gia) < window_size:
        print("❌ Chưa đủ dữ liệu để tính toán!")
        return None, None
    
    # BƯỚC 2: Cắt lấy cửa sổ trượt (Rolling Window) - Chỉ lấy N phần tử cuối cùng
    # Trong code gốc: window_data = self.lich_su_gia[-self.window_size:]
    window_data = lich_su_gia[-window_size:]
    print(f"👉 Bước 1: Cắt lấy {window_size} phần tử gần nhất để tính toán:")
    print(f"   window_data = {window_data}")

    # BƯỚC 3: Tính Đường trung bình (MA - Mean)
    # Trong code gốc: ma = sum(window_data) / self.window_size
    tong = sum(window_data)
    ma = tong / window_size
    print(f"👉 Bước 2: Tính Đường trung bình (MA):")
    print(f"   ma = {tong} / {window_size} = {ma}")

    # BƯỚC 4: Tính Phương sai (Variance)
    # Đo khoảng cách bình phương từ mỗi điểm giá trong cửa sổ tới đường trung bình MA
    # Trong code gốc: variance = sum((x - ma) ** 2 for x in window_data) / self.window_size
    print(f"👉 Bước 3: Tính khoảng cách bình phương tới MA để tìm Phương sai:")
    tong_binh_phuong_khoang_cach = 0
    for x in window_data:
        khoang_cach_bp = (x - ma) ** 2
        tong_binh_phuong_khoang_cach += khoang_cach_bp
        print(f"   • Phần tử {x}: ({x} - {ma})^2 = {khoang_cach_bp:.2f}")
        
    variance = tong_binh_phuong_khoang_cach / window_size
    print(f"   => Phương sai (Variance) = {tong_binh_phuong_khoang_cach:.2f} / {window_size} = {variance:.2f}")

    # BƯỚC 5: Tính Độ lệch chuẩn (Standard Deviation - Căn bậc hai của Phương sai)
    # Trong code gốc: std_dev = math.sqrt(variance)
    std_dev = math.sqrt(variance)
    print(f"👉 Bước 4: Lấy căn bậc hai để tìm Độ lệch chuẩn (StdDev):")
    print(f"   std_dev = √{variance:.2f} = {std_dev:.2f}")
    
    # Ứng dụng để tính dải lọc nhiễu trong hệ thống:
    nguong_tren = ma + (2.5 * std_dev)
    nguong_duoi = ma - (2.5 * std_dev)
    print(f"\n🎯 KẾT LUẬN CHO HỆ THỐNG:")
    print(f"   • Vùng an toàn ngẫu nhiên: [{nguong_duoi:.2f}đ  đến  {nguong_tren:.2f}đ]")
    
    return ma, std_dev





giai_thich_tinh_toan_chi_so_toan_hoc(lich_su_gia[-6:], window_size)
