// Đối tượng áp dụng của loại câu hỏi. Khớp backend/app/constants/doi_tuong_ap_dung.py.
// `ma` trùng `code` hướng đi trong components/guest/doi-tuong/HocSinhThpt/dinhHuong.js.
// Chỉ thêm giá trị mới, không đổi/xóa số đã dùng vì dữ liệu đã lưu theo số.
export const DOI_TUONG_AP_DUNG = [
  { value: 1, ma: 'thi-dai-hoc', label: 'Học sinh THPT thi đại học & cao đẳng', nhanNgan: 'Thi ĐH & CĐ' },
  { value: 2, ma: 'di-lam', label: 'Học sinh THPT đi làm ngay sau tốt nghiệp', nhanNgan: 'Đi làm ngay' },
  { value: 3, ma: 'du-hoc-nghe', label: 'Học sinh THPT du học nghề', nhanNgan: 'Du học nghề' },
  { value: 4, ma: 'du-hoc', label: 'Học sinh THPT du học', nhanNgan: 'Du học' },
  { value: 5, ma: 'khoi-nghiep', label: 'Học sinh THPT khởi nghiệp', nhanNgan: 'Khởi nghiệp' },
  { value: 6, ma: 'xuat-khau-lao-dong', label: 'Học sinh THPT xuất khẩu lao động', nhanNgan: 'Xuất khẩu lao động' },
]

export function timDoiTuongApDung(value) {
  return DOI_TUONG_AP_DUNG.find((item) => item.value === value)
}
