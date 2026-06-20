import random
import matplotlib.pyplot as plt

# ==========================================
# 1. ĐỊNH NGHĨA CÁC LỚP CHIẾN THUẬT
# ==========================================

class FixedFractional:
    def __init__(self, von_ban_dau, phan_tram_cuoc=0.05):
        self.ten = f"Fixed-Fractional ({phan_tram_cuoc*100}%)"
        self.von_ban_dau = float(von_ban_dau)
        self.tong_diem = float(von_ban_dau)
        self.phan_tram = phan_tram_cuoc
        self.chay_tai_khoan = False
        self.diem_du_doan = round(self.tong_diem * self.phan_tram, 2)

    def reset_phien(self):
        self.tong_diem = self.von_ban_dau
        self.diem_du_doan = round(self.tong_diem * self.phan_tram, 2)
        self.chay_tai_khoan = False

    def cap_nhat(self, doan_dung):
        # Mức cược tối thiểu để lệnh chạy được là 0.1đ
        if self.tong_diem < 0.1 or self.diem_du_doan < 0.1:
            self.chay_tai_khoan = True
            return

        if doan_dung:
            self.tong_diem = round(self.tong_diem + self.diem_du_doan, 2)
        else:
            self.tong_diem = round(self.tong_diem - self.diem_du_doan, 2)

        # Tính toán mức cược mới dựa trên số vốn mới (Lại kép / Giảm thiểu rủi ro)
        self.diem_du_doan = round(self.tong_diem * self.phan_tram, 2)


class AntiMartingale:
    def __init__(self, von_ban_dau, cuoc_co_so=2.0, chuoi_thang_muc_tieu=3):
        self.ten = f"Anti-Martingale (Chuỗi {chuoi_thang_muc_tieu})"
        self.von_ban_dau = float(von_ban_dau)
        self.tong_diem = float(von_ban_dau)
        self.cuoc_co_so = float(cuoc_co_so)
        self.diem_du_doan = self.cuoc_co_so
        self.chuoi_thang_muc_tieu = chuoi_thang_muc_tieu
        self.dem_chuoi_thang = 0
        self.chay_tai_khoan = False

    def reset_phien(self):
        self.tong_diem = self.von_ban_dau
        self.diem_du_doan = self.cuoc_co_so
        self.dem_chuoi_thang = 0
        self.chay_tai_khoan = False

    def cap_nhat(self, doan_dung):
        if self.tong_diem < self.diem_du_doan:
            self.chay_tai_khoan = True
            return

        if doan_dung:
            self.tong_diem = round(self.tong_diem + self.diem_du_doan, 2)
            self.dem_chuoi_thang += 1
            
            # Nếu đạt chuỗi thắng mục tiêu, chốt lời chuỗi ngắn và quay về mức cược cơ sở
            if self.dem_chuoi_thang >= self.chuoi_thang_muc_tieu:
                self.diem_du_doan = self.cuoc_co_so
                self.dem_chuoi_thang = 0
            else:
                self.diem_du_doan = round(self.diem_du_doan * 2.0, 2) # Gấp đôi khi THẮNG
        else:
            self.tong_diem = round(self.tong_diem - self.diem_du_doan, 2)
            self.diem_du_doan = self.cuoc_co_so # Thua thì quay về mức cược cơ sở ngay
            self.dem_chuoi_thang = 0


# ==========================================
# 2. HÀM CHẠY BACKTEST ĐỂ TÍNH KỲ VỌNG (EV)
# ==========================================

def chay_backtest_he_thong(chien_thuat, so_phien=1000, rvr_ratio=1.0, winrate_lenh_le=0.5, ti_le_an_lenh_le=1.0):
    muc_tieu_thang = chien_thuat.von_ban_dau * rvr_ratio
    diem_muc_tieu = chien_thuat.von_ban_dau + muc_tieu_thang
    
    so_phien_thang = 0
    lich_su_loi_nhuan = []

    for _ in range(so_phien):
        chien_thuat.reset_phien()
        
        vong = 0
        max_vong = 2000 # Giới hạn số vòng mỗi phiên để tránh loop vô hạn khi ko cháy
        while chien_thuat.tong_diem < diem_muc_tieu and not chien_thuat.chay_tai_khoan and vong < max_vong:
            kq = random.random() < winrate_lenh_le
            
            # Tùy biến tỷ lệ ăn lẻ nếu cần (ở bài toán này đang mặc định đặt 1 ăn 1)
            if kq and ti_le_an_lenh_le != 1.0:
                # Nếu cấu hình đặt biệt cho tỷ lệ ăn
                original_bet = chien_thuat.diem_du_doan
                chien_thuat.diem_du_doan = round(original_bet * ti_le_an_lenh_le, 2)
                chien_thuat.cap_nhat(True)
                chien_thuat.diem_du_doan = original_bet
            else:
                chien_thuat.cap_nhat(kq)
                
            vong += 1
            
        loi_nhuan_phien = chien_thuat.tong_diem - chien_thuat.von_ban_dau
        lich_su_loi_nhuan.append(loi_nhuan_phien)
        
        if chien_thuat.tong_diem >= diem_muc_tieu:
            so_phien_thang += 1

    # Thống kê toán học
    winrate_phien = so_phien_thang / so_phien
    cac_khoan_thang = [r for r in lich_su_loi_nhuan if r > 0]
    cac_khoan_thua = [r for r in lich_su_loi_nhuan if r <= 0]
    
    avg_win = sum(cac_khoan_thang) / len(cac_khoan_thang) if cac_khoan_thang else 0
    avg_loss = sum(cac_khoan_thua) / len(cac_khoan_thua) if cac_khoan_thua else -chien_thuat.von_ban_dau
    
    ev = (winrate_phien * avg_win) + ((1 - winrate_phien) * avg_loss)
    
    return {
        "ten": chien_thuat.ten,
        "winrate": winrate_phien,
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "ev": round(ev, 2),
        "lich_su": lich_su_loi_nhuan
    }

def in_ket_qua(kq):
    print(f"=== CHIẾN THUẬT: {kq['ten'].upper()} ===")
    print(f"• Tỷ lệ thắng phiên (WinRate): {kq['winrate']*100:.1f}%")
    print(f"• Thắng mục tiêu trung bình nhận được: +{kq['avg_win']}đ")
    print(f"• Thua/Dừng phiên trung bình mất đi: {kq['avg_loss']}đ")
    print(f"• GIÁ TRỊ KỲ VỌNG (EV): {kq['ev']}đ")
    if kq['ev'] > 0:
        print("=> Đánh giá: KỲ VỌNG DƯƠNG 🟢")
    elif abs(kq['ev']) <= 0.5:
        print("=> Đánh giá: KỲ VỌNG HOÀ VỐN (Hệ thống cân bằng) ⚪")
    else:
        print("=> Đánh giá: KỲ VỌNG ÂM 🔴")
    print("-" * 50)

# ==========================================
# 3. CHẠY CẤU HÌNH THỬ NGHIỆM
# ==========================================
SO_PHIEN = 1000
VON_BAN_DAU = 127.0
RVR_TARGET = 1.0         # Kiếm thêm 100% vốn (127đ) thì dừng phiên
WINRATE_LENH_LE = 0.5   # Tỷ lệ đoán trúng lệnh lẻ là 50/50

# Khởi tạo chiến thuật
st_fixed = FixedFractional(VON_BAN_DAU, phan_tram_cuoc=0.04) # Cược 4% tài khoản mỗi lệnh
st_anti = AntiMartingale(VON_BAN_DAU, cuoc_co_so=4.0, chuoi_thang_muc_tieu=3) # Cược gốc 4đ, ăn chuỗi 3 thì reset

# Chạy backtest
kq_fixed = chay_backtest_he_thong(st_fixed, SO_PHIEN, RVR_TARGET, WINRATE_LENH_LE)
kq_anti = chay_backtest_he_thong(st_anti, SO_PHIEN, RVR_TARGET, WINRATE_LENH_LE)

# In báo cáo
in_ket_qua(kq_fixed)
in_ket_qua(kq_anti)

# Vẽ đồ thị đường cong vốn
plt.figure(figsize=(12, 6))
plt.plot(kq_fixed['lich_su'], label=f"{kq_fixed['ten']} (EV: {kq_fixed['ev']}đ)", color='purple', alpha=0.6)
plt.plot(kq_anti['lich_su'], label=f"{kq_anti['ten']} (EV: {kq_anti['ev']}đ)", color='orange', alpha=0.6)
plt.axhline(0, color='red', linestyle='--', label='Vạch Hòa Vốn')
plt.title(f'BACKTEST {SO_PHIEN} PHIÊN - CHIẾN THUẬT QUẢN LÝ VỐN MỚI (Mục tiêu RvR = 1:{RVR_TARGET})')
plt.xlabel('Phiên chơi')
plt.ylabel('Lợi nhuận thu về mỗi phiên (đ)')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)
plt.show()