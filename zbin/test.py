import random
import matplotlib.pyplot as plt

class ChienThuatMartingale:
    def __init__(self, ten, tong_diem_ban_dau=127.0, diem_du_doan_ban_dau=1.0, kieu_thang="co_dinh"):
        self.ten = ten
        self.von_ban_dau = float(tong_diem_ban_dau)
        self.tong_diem = float(tong_diem_ban_dau)
        self.diem_du_doan = float(diem_du_doan_ban_dau)
        self.kieu_thang = kieu_thang 
        self.chay_tai_khoan = False
        
    def reset_phien(self):
        """Khởi động lại thông số cho phiên mới"""
        self.tong_diem = self.von_ban_dau
        self.diem_du_doan = 1.0 if self.kieu_thang == "co_dinh" else round(self.von_ban_dau / 31.0, 2)
        self.chay_tai_khoan = False

    def cap_nhat(self, doan_dung):
        if self.tong_diem < self.diem_du_doan:
            self.chay_tai_khoan = True
            return

        if doan_dung:
            self.tong_diem = round(self.tong_diem + self.diem_du_doan * 0.97, 2)
            if self.kieu_thang == "co_dinh":
                self.diem_du_doan = 1.0
            elif self.kieu_thang == "tang_dan":
                self.diem_du_doan = round(self.tong_diem / 31.0, 2)
        else:
            self.tong_diem = round(self.tong_diem - self.diem_du_doan, 2)
            self.diem_du_doan = round(self.diem_du_doan * 2.0, 2)

        if self.diem_du_doan < 0.01:
            self.diem_du_doan = 0.01

def mo_phong_he_thong(chien_thuat, so_phien=100, rvr_ratio=0.5, win_rate_tung_lenh=0.5):
    """
    Hàm mô phỏng chạy nhiều phiên để tính toán thống kê
    rvr_ratio = 0.5 nghĩa là Mục tiêu thắng = 50% số vốn ban đầu (Risk 1 : Reward 0.5)
    """
    muc_tieu_thang = chien_thuat.von_ban_dau * rvr_ratio
    diem_muc_tieu = chien_thuat.von_ban_dau + muc_tieu_thang
    
    so_phien_thang = 0
    so_phien_thua = 0
    lich_su_loi_nhuan = []

    for _ in range(so_phien):
        chien_thuat.reset_phien()
        
        # Chạy 1 phiên cho đến khi đạt điều kiện dừng (Thắng mục tiêu hoặc Cháy)
        max_vong_an_toan = 1000  # Tránh vòng lặp vô hạn
        vong = 0
        while chien_thuat.tong_diem < diem_muc_tieu and not chien_thuat.chay_tai_khoan and vong < max_vong_an_toan:
            # Mô phỏng lệnh đoán dựa trên tỷ lệ WinRate cấu hình
            kq = random.random() < win_rate_tung_lenh
            chien_thuat.cap_nhat(kq)
            vong += 1
            
        # Kết thúc 1 phiên -> Ghi nhận kết quả
        loi_nhuan_phien = chien_thuat.tong_diem - chien_thuat.von_ban_dau
        lich_su_loi_nhuan.append(loi_nhuan_phien)
        
        if chien_thuat.tong_diem >= diem_muc_tieu:
            so_phien_thang += 1
        else:
            so_phien_thua += 1

    # --- TÍNH TOÁN THỐNG KÊ ---
    winrate_phien = so_phien_thang / so_phien
    
    # Lọc phần trăm lợi nhuận trung bình khi thắng/thua
    cac_khoan_thang = [r for r in lich_su_loi_nhuan if r > 0]
    cac_khoan_thua = [r for r in lich_su_loi_nhuan if r <= 0]
    
    avg_win = sum(cac_khoan_thang) / len(cac_khoan_thang) if cac_khoan_thang else 0
    avg_loss = sum(cac_khoan_thua) / len(cac_khoan_thua) if cac_khoan_thua else -chien_thuat.von_ban_dau
    
    # Công thức Giá trị kỳ vọng: E(X) = (P_win * Avg_Win) + (P_loss * Avg_Loss)
    gia_tri_ky_vong = (winrate_phien * avg_win) + ((1 - winrate_phien) * avg_loss)
    
    return {
        "ten": chien_thuat.ten,
        "winrate": winrate_phien,
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "ev": round(gia_tri_ky_vong, 2),
        "lich_su": lich_su_loi_nhuan
    }


def in_bao_cao(kq):
    print(f"=== BÁO CÁO: {kq['ten'].upper()} ===")
    print(f"• Tỷ lệ thắng phiên (WinRate): {kq['winrate']*100:.1f}%")
    print(f"• Số tiền trung bình nhận được khi THẮNG mục tiêu: +{kq['avg_win']}đ")
    print(f"• Số tiền trung bình mất đi khi THUA (Cháy): {kq['avg_loss']}đ")
    print(f"• GIÁ TRỊ KỲ VỌNG (Expected Value): {kq['ev']}đ")
    if kq['ev'] > 0:
        print("=> Đánh giá: Chiến thuật có kỳ vọng DƯƠNG (Có lãi về dài hạn) 🟢")
    else:
        print("=> Đánh giá: Chiến thuật có kỳ vọng ÂM (Chắc chắn lỗ về dài hạn) 🔴")
    print("-" * 50)


# --- CẤU HÌNH THỬ NGHIỆM ---
for target in [0.5, 1, 2]:
    SO_PHIEN = 1000
    VON_BAN_DAU = 127.0
    RVR_TARGET = target        # Muốn ăn 50% vốn (kiếm thêm ~63.5đ mỗi phiên)
    WINRATE_MESS = 0.5       # Xác suất đoán đúng của từng lệnh lẻ (Ví dụ: Tung đồng xu 50/50)

    print("\nSO_PHIEN, VON_BAN_DAU, RVR_TARGET, WINRATE_MESS")
    print(SO_PHIEN, VON_BAN_DAU, RVR_TARGET, WINRATE_MESS)

    # Khởi tạo chiến thuật
    c1 = ChienThuatMartingale("Cách 1: Cược cố định", VON_BAN_DAU, kieu_thang="co_dinh")
    c2 = ChienThuatMartingale("Cách 2: Cược tăng dần", VON_BAN_DAU, kieu_thang="tang_dan")

    # Chạy mô phỏng hệ thống
    kq_c1 = mo_phong_he_thong(c1, so_phien=SO_PHIEN, rvr_ratio=RVR_TARGET, win_rate_tung_lenh=WINRATE_MESS)
    kq_c2 = mo_phong_he_thong(c2, so_phien=SO_PHIEN, rvr_ratio=RVR_TARGET, win_rate_tung_lenh=WINRATE_MESS)

    # --- IN BÁO CÁO TOÁN HỌC ---

    in_bao_cao(kq_c1)
    in_bao_cao(kq_c2)

# --- VẼ BIỂU ĐỒ TRỰC QUAN HÓA TÀI KHOẢN ---de
# plt.figure(figsize=(12, 6))
# plt.plot(kq_c1['lich_su'], label=f"{kq_c1['ten']} (EV: {kq_c1['ev']}đ)", color='blue', alpha=0.7)
# plt.plot(kq_c2['lich_su'], label=f"{kq_c2['ten']} (EV: {kq_c2['ev']}đ)", color='green', alpha=0.7)
# plt.axhline(0, color='red', linestyle='--', label='Vạch Hòa Vốn')
# plt.title(f'BIỂU ĐỒ KẾT QUẢ ĐẦU TƯ CỦA {SO_PHIEN} PHIÊN (RvR Vốn : Mục tiêu = 1 : {RVR_TARGET})')
# plt.xlabel('Phiên chơi thứ')
# plt.ylabel('Lợi nhuận ròng thu về mỗi phiên (đ)')
# plt.legend()
# plt.grid(True, linestyle=':', alpha=0.6)
# plt.show()