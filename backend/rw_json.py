import json
from datetime import datetime




CAU_TRUC_MAC_DINH = {"money": [], "tong_so": 0, "ngay_tao": ""}


def ghi_file_json(data=None, file_path="data.json"):
    """Hàm ghi dữ liệu vào file JSON.

    Nếu data trống hoặc None, sẽ dùng cấu trúc mặc định.
    """
    # Nếu không có dữ liệu hoặc dữ liệu rỗng, dùng cấu trúc mặc định
    if not data:
        data = CAU_TRUC_MAC_DINH
        print("⚠️ Không có dữ liệu, tiến hành ghi cấu trúc mặc định.")

    try:
        CAU_TRUC_MAC_DINH.ngay_tao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f" Ghi file thành công vào: {file_path}")
    except Exception as e:
        print(f"❌ Lỗi khi ghi file: {e}")


def doc_file_json(file_path="data.json"):
    """Hàm đọc dữ liệu từ file JSON.

    Nếu không tìm thấy file, trả về cấu trúc mặc định.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(
            f"⚠️ Không tìm thấy file '{file_path}'. Trả về cấu trúc mặc định."
        )
        return CAU_TRUC_MAC_DINH
    except Exception as e:
        print(f"❌ Lỗi khi đọc file: {e}")
        return CAU_TRUC_MAC_DINH