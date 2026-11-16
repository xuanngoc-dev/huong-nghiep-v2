/**
 * Nội dung và nhận xét cho màn hình kết quả trắc nghiệm Holland (RIASEC).
 *
 * Nội dung mang tính định hướng: kết quả Holland phản ánh SỞ THÍCH tại thời điểm làm bài, không đo năng lực,
 * nên mọi câu chữ dùng "có thể", "thường", "nên cân nhắc" thay cho khẳng định.
 */

// Thứ tự trên lục giác Holland: hai nhóm cạnh nhau có nhiều điểm chung, đối diện nhau thì khác biệt nhất.
export const THU_TU_RIASEC = ['R', 'I', 'A', 'S', 'E', 'C']

export const NOI_DUNG_NHOM = {
  R: {
    ten: 'Kỹ thuật',
    dac_diem: ['Thực tế, thích làm việc bằng tay và công cụ', 'Thích kết quả cụ thể, nhìn thấy được', 'Kiên trì, ưa hành động hơn lý thuyết'],
    hoat_dong: ['Lắp ráp, sửa chữa đồ vật, máy móc', 'Làm mô hình, thí nghiệm thực hành', 'Hoạt động ngoài trời, thể thao, chăm sóc cây trồng vật nuôi'],
    moi_truong: 'Môi trường thực hành như xưởng, công trường, phòng thí nghiệm, ngoài trời; nhiệm vụ rõ ràng, có sản phẩm cụ thể.',
    ky_nang: ['Đọc bản vẽ, sử dụng thiết bị an toàn', 'Giải quyết sự cố kỹ thuật', 'Trình bày, phối hợp nhóm để bổ trợ phần giao tiếp'],
    can_nhac: 'Nhiều nghề kỹ thuật đòi hỏi sức khỏe, làm việc theo ca hoặc ngoài trời; nên tìm hiểu điều kiện làm việc thực tế.',
    trai_nghiem: ['Tham gia câu lạc bộ robotics, STEM hoặc sửa chữa', 'Tham quan nhà máy, xưởng sản xuất', 'Thử tự làm một sản phẩm nhỏ từ đầu đến cuối'],
    mo_ta_nghe: 'Công việc thực hành với máy móc, thiết bị, công trình hoặc sản phẩm cụ thể.',
  },
  I: {
    ten: 'Nghiên cứu',
    dac_diem: ['Tò mò, thích đặt câu hỏi "vì sao"', 'Thích phân tích, suy luận logic', 'Độc lập, tập trung sâu vào vấn đề'],
    hoat_dong: ['Giải bài toán, câu đố logic', 'Đọc sách khoa học, tìm hiểu công nghệ', 'Làm thí nghiệm, dự án nghiên cứu nhỏ'],
    moi_truong: 'Môi trường coi trọng tư duy và dữ liệu như phòng thí nghiệm, viện nghiên cứu, nhóm phân tích, công ty công nghệ.',
    ky_nang: ['Tư duy phản biện, phương pháp nghiên cứu', 'Toán, thống kê, tin học', 'Diễn đạt kết quả cho người khác hiểu'],
    can_nhac: 'Nhiều nghề nghiên cứu cần học lâu dài và kiên nhẫn với kết quả chậm; nên xem bạn có hứng thú với quá trình học sâu không.',
    trai_nghiem: ['Tham gia cuộc thi khoa học kỹ thuật, olympic', 'Làm một dự án nhỏ phân tích dữ liệu', 'Gặp gỡ giảng viên, nhà nghiên cứu để hỏi về công việc'],
    mo_ta_nghe: 'Công việc phân tích, nghiên cứu và giải quyết vấn đề bằng dữ liệu, lập luận.',
  },
  A: {
    ten: 'Nghệ thuật',
    dac_diem: ['Giàu trí tưởng tượng, nhạy cảm với cái đẹp', 'Thích thể hiện cá tính, ý tưởng riêng', 'Ưa tự do, linh hoạt'],
    hoat_dong: ['Vẽ, thiết kế, chụp ảnh, làm video', 'Viết, đọc sáng tác, biểu diễn âm nhạc, sân khấu', 'Trang trí, sáng tạo nội dung'],
    moi_truong: 'Môi trường mở, linh hoạt, khuyến khích sáng tạo như studio, agency, tòa soạn, nhà hát, dự án tự do.',
    ky_nang: ['Kỹ năng chuyên môn của loại hình nghệ thuật yêu thích', 'Xây dựng hồ sơ tác phẩm (portfolio)', 'Quản lý thời gian, nhận góp ý'],
    can_nhac: 'Thu nhập trong lĩnh vực sáng tạo có thể không ổn định lúc đầu; một số ngành cần thi năng khiếu nên chuẩn bị sớm.',
    trai_nghiem: ['Tham gia câu lạc bộ nghệ thuật, truyền thông của trường', 'Làm một sản phẩm cá nhân và chia sẻ để nhận góp ý', 'Theo một khóa học ngắn về thiết kế, nhiếp ảnh hoặc viết'],
    mo_ta_nghe: 'Công việc sáng tạo, thể hiện ý tưởng qua hình ảnh, ngôn ngữ, âm thanh hoặc biểu diễn.',
  },
  S: {
    ten: 'Xã hội',
    dac_diem: ['Quan tâm, thấu hiểu người khác', 'Thích hợp tác, giúp đỡ, chia sẻ', 'Giao tiếp tốt, kiên nhẫn'],
    hoat_dong: ['Hướng dẫn bạn bè học bài', 'Tham gia hoạt động tình nguyện, cộng đồng', 'Lắng nghe, tư vấn, tổ chức sinh hoạt tập thể'],
    moi_truong: 'Môi trường làm việc với con người như trường học, bệnh viện, tổ chức xã hội, bộ phận nhân sự, chăm sóc khách hàng.',
    ky_nang: ['Lắng nghe, giao tiếp, thấu cảm', 'Giải quyết mâu thuẫn', 'Giữ cân bằng cảm xúc khi hỗ trợ người khác'],
    can_nhac: 'Công việc hỗ trợ con người có thể nhiều áp lực cảm xúc; nên cân nhắc khả năng chịu áp lực và cách tự cân bằng.',
    trai_nghiem: ['Tham gia tình nguyện, gia sư, hỗ trợ học tập', 'Làm trợ giảng, ban cán sự lớp', 'Tìm hiểu một ngày làm việc của giáo viên, điều dưỡng, tư vấn viên'],
    mo_ta_nghe: 'Công việc giảng dạy, chăm sóc, tư vấn và hỗ trợ con người.',
  },
  E: {
    ten: 'Quản lý',
    dac_diem: ['Năng động, tự tin, thích dẫn dắt', 'Thích thuyết phục, thương lượng', 'Định hướng mục tiêu, dám chấp nhận thử thách'],
    hoat_dong: ['Tổ chức sự kiện, dẫn dắt nhóm', 'Kinh doanh nhỏ, bán hàng, gây quỹ', 'Tranh biện, thuyết trình'],
    moi_truong: 'Môi trường năng động, cạnh tranh, gắn với mục tiêu và kết quả như doanh nghiệp, khởi nghiệp, kinh doanh, truyền thông.',
    ky_nang: ['Lập kế hoạch, quản lý thời gian', 'Thuyết trình, đàm phán', 'Hiểu biết tài chính, kinh doanh cơ bản'],
    can_nhac: 'Các vị trí quản lý thường đến sau một thời gian làm chuyên môn; nên chọn ngành có nền tảng kiến thức vững để phát triển lâu dài.',
    trai_nghiem: ['Làm trưởng nhóm một dự án, sự kiện của trường', 'Thử một dự án kinh doanh nhỏ', 'Tham gia câu lạc bộ khởi nghiệp, tranh biện'],
    mo_ta_nghe: 'Công việc lãnh đạo, kinh doanh, thuyết phục và điều hành để đạt mục tiêu.',
  },
  C: {
    ten: 'Nghiệp vụ',
    dac_diem: ['Cẩn thận, chính xác, ngăn nắp', 'Thích quy trình rõ ràng', 'Đáng tin cậy, có trách nhiệm'],
    hoat_dong: ['Sắp xếp, quản lý tài liệu, số liệu', 'Lập bảng tính, kế hoạch chi tiêu', 'Làm thủ quỹ, thư ký cho lớp, câu lạc bộ'],
    moi_truong: 'Môi trường ổn định, có quy định và quy trình như văn phòng, ngân hàng, cơ quan hành chính, bộ phận kế toán.',
    ky_nang: ['Tin học văn phòng, bảng tính', 'Xử lý số liệu chính xác', 'Thích nghi với thay đổi và công cụ số mới'],
    can_nhac: 'Nhiều công việc nghiệp vụ đang được tự động hóa; nên chú trọng kỹ năng phân tích và công nghệ đi kèm.',
    trai_nghiem: ['Quản lý quỹ lớp hoặc sổ sách câu lạc bộ', 'Học thành thạo một công cụ bảng tính', 'Tìm hiểu công việc kế toán, hành chính qua người thân'],
    mo_ta_nghe: 'Công việc có quy trình rõ ràng, xử lý dữ liệu, số liệu và hồ sơ chính xác.',
  },
}

/** Nhóm có điểm, xếp giảm dần theo điểm (bằng điểm thì theo thứ tự RIASEC). */
export function xepHang(nhom) {
  return [...(nhom || [])]
    .filter((item) => Number(item.diem) > 0)
    .sort((a, b) => b.diem - a.diem || THU_TU_RIASEC.indexOf(a.ma_nhom) - THU_TU_RIASEC.indexOf(b.ma_nhom))
}

/** 6 nhóm theo thứ tự RIASEC (cho biểu đồ), nhóm thiếu điểm = 0. */
export function theoThuTuRiasec(nhom) {
  const theoMa = new Map((nhom || []).map((item) => [item.ma_nhom, item]))
  return THU_TU_RIASEC.map(
    (ma) => theoMa.get(ma) || { ma_nhom: ma, ten_nhom: NOI_DUNG_NHOM[ma].ten, diem: 0 },
  )
}

/** Khoảng cách trên lục giác: 1 = cạnh nhau, 2 = cách một nhóm, 3 = đối diện. */
export function khoangCach(ma1, ma2) {
  const d = Math.abs(THU_TU_RIASEC.indexOf(ma1) - THU_TU_RIASEC.indexOf(ma2))
  return Math.min(d, 6 - d)
}

/** Các đoạn nhận xét tổng quan, mang tính định hướng. */
export function nhanXetTongQuan(nhom) {
  const top = xepHang(nhom)
  if (!top.length) return ['Chưa đủ câu trả lời để nhận xét. Hãy hoàn thành bài trắc nghiệm để xem xu hướng sở thích.']
  const doan = []
  const ten = (item) => `${item.ten_nhom} (${item.ma_nhom})`
  const ba = top.slice(0, 3)
  doan.push(
    ba.length > 1
      ? `Sở thích của bạn nghiêng nhiều nhất về ${ten(ba[0])}, tiếp theo là ${ba.slice(1).map(ten).join(' và ')}.`
      : `Sở thích của bạn nghiêng rõ về nhóm ${ten(ba[0])}.`,
  )

  const diem = theoThuTuRiasec(nhom).map((item) => Number(item.diem) || 0)
  const cao = Math.max(...diem)
  const thap = Math.min(...diem)
  if (cao > 0 && (cao - thap) / cao <= 0.25) {
    doan.push(
      'Điểm giữa các nhóm khá đồng đều: bạn có thể quan tâm đến nhiều lĩnh vực cùng lúc. Trải nghiệm thực tế sẽ giúp bạn thu hẹp lựa chọn.',
    )
  } else if (top[1] && top[0].diem - top[1].diem >= Math.max(2, cao * 0.15)) {
    doan.push(`Nhóm ${ten(top[0])} nổi bật hơn hẳn các nhóm còn lại, đây là hướng nên ưu tiên tìm hiểu trước.`)
  }

  if (top[1]) {
    const d = khoangCach(top[0].ma_nhom, top[1].ma_nhom)
    if (d === 1) {
      doan.push('Hai nhóm đứng đầu có nhiều điểm chung, các xu hướng sở thích của bạn khá nhất quán và bổ trợ cho nhau.')
    } else if (d === 3) {
      doan.push(
        'Hai nhóm đứng đầu khá khác nhau. Bạn có thể tìm những nghề kết hợp được cả hai, hoặc trải nghiệm thêm để biết mình ưu tiên hướng nào.',
      )
    }
  }
  doan.push(
    'Kết quả phản ánh sở thích tại thời điểm làm bài, không phải thước đo năng lực. Hãy kết hợp với kết quả học tập, sức khỏe, điều kiện gia đình và trải nghiệm thực tế khi chọn nghề.',
  )
  return doan
}

/** Gộp một loại nội dung (dac_diem, hoat_dong, ky_nang, trai_nghiem) của các nhóm nổi bật, ghi kèm mã nhóm. */
export function gopNoiDung(top, khoa) {
  return (top || []).flatMap((item) =>
    (NOI_DUNG_NHOM[item.ma_nhom]?.[khoa] || []).map((noiDung) => ({ ma_nhom: item.ma_nhom, noi_dung: noiDung })),
  )
}

/** Nghề gợi ý từ vi_du_nghe_nghiep của danh mục nhóm Holland, mỗi nhóm nổi bật tối đa `moiNhom` nghề, không lặp. */
export function ngheGoiY(top, danhMucNhom, moiNhom = 4) {
  const theoMa = new Map((danhMucNhom || []).map((item) => [item.ma_nhom, item]))
  const daCo = new Set()
  const ketQua = []
  for (const item of top || []) {
    const ds = String(theoMa.get(item.ma_nhom)?.vi_du_nghe_nghiep || '')
      .split(/[,;\n]/)
      .map((ten) => ten.trim())
      .filter(Boolean)
    let them = 0
    for (const ten of ds) {
      const khoa = ten.toLowerCase()
      if (daCo.has(khoa) || them >= moiNhom) continue
      daCo.add(khoa)
      them += 1
      ketQua.push({
        ten: ten.charAt(0).toUpperCase() + ten.slice(1),
        ma_nhom: item.ma_nhom,
        ten_nhom: item.ten_nhom,
        mo_ta: NOI_DUNG_NHOM[item.ma_nhom]?.mo_ta_nghe || '',
      })
    }
  }
  return ketQua
}

/** Câu hỏi điền sẵn cho trợ lý AI. */
export function cauHoiTuVan(top) {
  const ma = top.map((item) => item.ma_nhom).join('')
  const ten = top.map((item) => `${item.ten_nhom} (${item.ma_nhom})`).join(', ')
  return `Kết quả trắc nghiệm Holland của tôi là ${ma}: nổi bật các nhóm ${ten}. Hãy gợi ý giúp tôi các ngành học, nghề nghiệp phù hợp và tôi nên chuẩn bị gì trong thời gian tới.`
}

/** Danh sách quan tâm (ngành, trường) lưu trong trình duyệt theo phiên khảo sát; lỗi bộ nhớ thì bỏ qua. */
export function docQuanTam(storage, ssid) {
  try {
    const data = JSON.parse(storage?.getItem(`holland-quan-tam:${ssid}`) || '{}')
    return { nganh: Array.isArray(data.nganh) ? data.nganh : [], truong: Array.isArray(data.truong) ? data.truong : [] }
  } catch {
    return { nganh: [], truong: [] }
  }
}

export function ghiQuanTam(storage, ssid, data) {
  try {
    storage?.setItem(`holland-quan-tam:${ssid}`, JSON.stringify(data))
    return true
  } catch {
    return false
  }
}
