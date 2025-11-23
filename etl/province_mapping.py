# etl/province_mapping.py

from typing import Optional

# Mapping mẫu. Bạn cần bổ sung đầy đủ mã tỉnh theo quy ước SBD của Bộ GD và ĐT.
MA_TINH_TO_TEN = {
    "01": "Hà Nội",
    "02": "Thành phố Hồ Chí Minh",
    "03": "Hải Phòng",
    "04": "Đà Nẵng",
    "05": "Hà Giang",
    "06": "Cao Bằng",
    "07": "Lai Châu",
    "08": "Lào Cai",
    "09": "Tuyên Quang",
    "10": "Lạng Sơn",
    "11": "Bắc Kạn",
    "12": "Thái Nguyên",
    "13": "Yên Bái",
    "14": "Sơn La",
    "15": "Phú Thọ",
    "16": "Vĩnh Phúc",
    "17": "Quảng Ninh",
    "18": "Bắc Giang",
    "19": "Bắc Ninh",
    # "20": hiện tại không dùng trong bảng mã Sở GDĐT
    "21": "Hải Dương",
    "22": "Hưng Yên",
    "23": "Hòa Bình",
    "24": "Hà Nam",
    "25": "Nam Định",
    "26": "Thái Bình",
    "27": "Ninh Bình",
    "28": "Thanh Hóa",
    "29": "Nghệ An",
    "30": "Hà Tĩnh",
    "31": "Quảng Bình",
    "32": "Quảng Trị",
    "33": "Thừa Thiên Huế",
    "34": "Quảng Nam",
    "35": "Quảng Ngãi",
    "36": "Kon Tum",
    "37": "Bình Định",
    "38": "Gia Lai",
    "39": "Phú Yên",
    "40": "Đắk Lắk",
    "41": "Khánh Hòa",
    "42": "Lâm Đồng",
    "43": "Bình Phước",
    "44": "Bình Dương",
    "45": "Ninh Thuận",
    "46": "Tây Ninh",
    "47": "Bình Thuận",
    "48": "Đồng Nai",
    "49": "Long An",
    "50": "Đồng Tháp",
    "51": "An Giang",
    "52": "Bà Rịa - Vũng Tàu",
    "53": "Tiền Giang",
    "54": "Kiên Giang",
    "55": "Cần Thơ",
    "56": "Bến Tre",
    "57": "Vĩnh Long",
    "58": "Trà Vinh",
    "59": "Sóc Trăng",
    "60": "Bạc Liêu",
    "61": "Cà Mau",
    "62": "Điện Biên",
    "63": "Đắk Nông",
    "64": "Hậu Giang",
    "65": "Cục Nhà trường - Bộ Quốc phòng",
}


def extract_ma_tinh_from_sbd(sbd: str) -> Optional[str]:
    if sbd is None:
        return None
    sbd = str(sbd).strip()
    if len(sbd) < 2:
        return None

    prefix2 = sbd[:2]
    if prefix2 in MA_TINH_TO_TEN:
        return prefix2

    prefix3 = sbd[:3]
    if prefix3 in MA_TINH_TO_TEN:
        return prefix3

    return None


def get_tinh_thanh_from_sbd(sbd: str) -> Optional[str]:
    ma_tinh = extract_ma_tinh_from_sbd(sbd)
    if ma_tinh is None:
        return None
    return MA_TINH_TO_TEN.get(ma_tinh)
