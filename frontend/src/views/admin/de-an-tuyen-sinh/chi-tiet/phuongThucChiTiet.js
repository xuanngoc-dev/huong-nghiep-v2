const SECTION_ORDER = [
  ['quy_doi', 'Quy đổi điểm số'],
  ['thuong', 'Mức điểm thưởng cho chứng chỉ ngoại ngữ'],
  ['bang_diem', 'Bảng điểm'],
  ['cong_thuc', 'Quy định cách tính điểm'],
  ['khac', 'Quy định liên quan'],
]

const COLUMN_LABELS = {
  diem_thuong_thang_100: 'Điểm thưởng (thang 100)',
  diem_quy_doi_thang_10: 'Điểm quy đổi (thang 10)',
  ielts_academic: 'IELTS Academic',
  vstep: 'VSTEP',
  aptis_esol: 'Aptis ESOL',
  peic: 'PEIC',
  pte_academic: 'PTE Academic',
  linguaskill: 'Linguaskill',
  cambridge_assessment_english: 'Cambridge Assessment English',
  cambridge_english_tests: 'Cambridge English Tests',
  toeic_nghe: 'TOEIC Nghe',
  toeic_noi: 'TOEIC Nói',
  toeic_doc: 'TOEIC Đọc',
  toeic_viet: 'TOEIC Viết',
  toefl_ibt: 'TOEFL iBT',
  toefl_itp: 'TOEFL ITP',
  delf_dalf: 'DELF/DALF',
  tcf: 'TCF',
  testdaf: 'TestDaF',
  goethe_osd_telc_ecl: 'Goethe / ÖSD / telc / ECL',
  dsh: 'DSH',
  dsd: 'DSD',
  jlpt: 'JLPT',
  hsk: 'HSK',
  hskk: 'HSKK',
  topik: 'TOPIK',
}

const GROUP_LABELS = {
  HSG: 'Học sinh giỏi',
  KHKT: 'Khoa học kỹ thuật',
  OLYMPIA: 'Đường lên đỉnh Olympia',
  HE_CHUYEN: 'Hệ chuyên',
  NGOAI_NGU_IELTS_HOAC_TUONG_DUONG: 'Ngoại ngữ (IELTS hoặc tương đương)',
  VAN_THE_MY: 'Văn - thể - mỹ',
  HOAT_DONG_XA_HOI: 'Hoạt động xã hội',
}

const SCORE_LABELS = {
  nhat_quoc_gia_tro_len: 'Nhất quốc gia trở lên',
  nhi_quoc_gia: 'Nhì quốc gia',
  ba_quoc_gia: 'Ba quốc gia',
  khuyen_khich_quoc_gia: 'Khuyến khích quốc gia',
  tu_khuyen_khich_quoc_gia: 'Từ khuyến khích quốc gia',
  nhat_quoc_gia: 'Nhất quốc gia',
  giai_quoc_te: 'Giải quốc tế',
  nhat_tinh: 'Nhất tỉnh',
  nhi_tinh: 'Nhì tỉnh',
  ba_tinh: 'Ba tỉnh',
  khuyen_khich_tinh: 'Khuyến khích tỉnh',
  vong_nam: 'Vòng năm',
  vong_quy: 'Vòng quý',
  vong_thang: 'Vòng tháng',
  vong_tuan: 'Vòng tuần',
  hoc_chuyen_3_nam: 'Học chuyên 3 năm',
  IELTS_5_0: 'IELTS 5.0',
  'IELTS_5.0': 'IELTS 5.0',
  'IELTS_5.5': 'IELTS 5.5',
  'IELTS_6.0': 'IELTS 6.0',
  'IELTS_6.5': 'IELTS 6.5',
  IELTS_tu_7_0: 'IELTS từ 7.0',
  'IELTS_tu_7.0': 'IELTS từ 7.0',
  nhat_quoc_gia_hcv: 'Nhất quốc gia / HCV',
  nhi_quoc_gia_hcb: 'Nhì quốc gia / HCB',
  ba_quoc_gia_hcd: 'Ba quốc gia / HCĐ',
  nhat_tinh_hcv: 'Nhất tỉnh / HCV',
  nhi_tinh_hcb: 'Nhì tỉnh / HCB',
  ba_tinh_hcd: 'Ba tỉnh / HCĐ',
  bang_khen: 'Bằng khen',
  giay_khen: 'Giấy khen',
  giay_chung_nhan_hien_mau: 'Giấy chứng nhận hiến máu',
}

function text(value) {
  return String(value ?? '').trim()
}

function asData(value) {
  if (value && typeof value === 'object') return value
  if (typeof value !== 'string') return null
  const raw = value.trim()
  if (!raw.startsWith('{') && !raw.startsWith('[')) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

function columnLabel(key) {
  return COLUMN_LABELS[key] || key.replaceAll('_', ' ')
}

function scoreLabel(value) {
  const raw = text(value)
  if (!raw) return '—'
  return SCORE_LABELS[raw] || raw.replaceAll('_', ' ')
}

function walkCodes(value, known, found, queue) {
  if (typeof value === 'string') {
    const code = value.trim()
    if (known.has(code) && !found.has(code)) {
      found.add(code)
      queue.push(code)
    }
    return
  }
  if (Array.isArray(value)) {
    value.forEach((item) => walkCodes(item, known, found, queue))
    return
  }
  if (value && typeof value === 'object') {
    Object.values(value).forEach((item) => walkCodes(item, known, found, queue))
  }
}

function referencedCriteria(methods, criteria) {
  const known = new Map()
  for (const item of criteria) {
    const code = text(item?.ma_tieu_chi)
    if (code && !known.has(code)) known.set(code, item)
  }
  const found = new Set()
  const queue = []
  for (const method of methods) {
    walkCodes(asData(method?.dieu_kien_can) || method?.dieu_kien_can, known, found, queue)
  }
  while (queue.length) {
    const item = known.get(queue.shift())
    walkCodes(asData(item?.gia_tri_tieu_chi) || item?.gia_tri_tieu_chi, known, found, queue)
  }
  return [...found]
    .map((code) => known.get(code))
    .sort((a, b) => (a.thu_tu_ap_dung ?? 999) - (b.thu_tu_ap_dung ?? 999) || text(a.ten_tieu_chi).localeCompare(text(b.ten_tieu_chi), 'vi'))
}

function sectionKey(criterion) {
  const value = asData(criterion.gia_tri_tieu_chi) || {}
  if (value.bang_quy_doi_tuong_duong) return 'quy_doi'
  if (value.moc_ielts_hoac_tuong_duong) return 'thuong'
  if (value.bang_diem || criterion.loai_tieu_chi === 'bang_diem') return 'bang_diem'
  if (value.cong_thuc_hien_thi || criterion.loai_tieu_chi === 'cong_thuc' || value.cong_thuc) return 'cong_thuc'
  return 'khac'
}

function conversionBlock(criterion) {
  const value = asData(criterion.gia_tri_tieu_chi) || {}
  const source = value.bang_quy_doi_tuong_duong
  if (!Array.isArray(source) || !source.length) return null
  const keys = []
  for (const row of source) {
    if (!row || typeof row !== 'object') continue
    for (const key of Object.keys(row)) {
      if (!keys.includes(key)) keys.push(key)
    }
  }
  const preferred = ['diem_thuong_thang_100', 'diem_quy_doi_thang_10']
  const ordered = [
    ...preferred.filter((key) => keys.includes(key)),
    ...keys.filter((key) => !preferred.includes(key)),
  ]
  const notes = []
  if (value.quy_tac_toeic) notes.push(value.quy_tac_toeic)
  return {
    kind: 'table',
    title: criterion.ten_tieu_chi || '',
    notes,
    columns: ordered.map((key) => ({
      key,
      label: columnLabel(key),
      minWidth: preferred.includes(key) ? 150 : key.startsWith('cambridge') ? 220 : 140,
    })),
    rows: source.map((row) => ({ ...row })),
  }
}

function bonusBlock(criterion) {
  const value = asData(criterion.gia_tri_tieu_chi) || {}
  const levels = value.moc_ielts_hoac_tuong_duong
  if (!Array.isArray(levels) || !levels.length) return null
  const certs = []
  for (const level of levels) {
    const scores = level?.diem_thuong_theo_chung_chi
    if (!scores || typeof scores !== 'object') continue
    for (const key of Object.keys(scores)) {
      if (!certs.includes(key)) certs.push(key)
    }
  }
  const notes = [value.quy_tac_ap_dung, value.don_vi_diem_thuong].filter(Boolean)
  return {
    kind: 'table',
    title: criterion.ten_tieu_chi || '',
    notes,
    columns: [
      { key: 'muc', label: 'Mức IELTS hoặc tương đương', minWidth: 180 },
      { key: 'thuong_100', label: 'Điểm thưởng (thang 100)', minWidth: 160 },
      ...certs.map((key) => ({ key, label: key, minWidth: 100 })),
    ],
    rows: levels.map((level) => {
      const row = {
        muc: level.muc_ielts_hoac_tuong_duong ?? null,
        thuong_100: level.diem_thuong_thang_100 ?? null,
      }
      for (const cert of certs) row[cert] = level.diem_thuong_theo_chung_chi?.[cert] ?? null
      return row
    }),
  }
}

function formulaBlock(criterion) {
  const value = asData(criterion.gia_tri_tieu_chi) || {}
  const rule = value.quy_tac_lay_diem_chung_chi || {}
  const notes = []
  if (rule.cach_lay_diem) notes.push(rule.cach_lay_diem)
  if (Array.isArray(rule.mon_bat_buoc) && rule.mon_bat_buoc.length) {
    notes.push(`Môn bắt buộc: ${rule.mon_bat_buoc.join(', ')}.`)
  }
  if (Array.isArray(rule.mon_tu_chon_hai_mon_diem_cao_nhat) && rule.mon_tu_chon_hai_mon_diem_cao_nhat.length) {
    notes.push(`Hai môn có điểm cao nhất trong: ${rule.mon_tu_chon_hai_mon_diem_cao_nhat.join(', ')}.`)
  }
  if (value.diem_tu_duy?.bieu_thuc) notes.push(`Điểm tư duy: ${value.diem_tu_duy.bieu_thuc}.`)
  if (value.diem_thanh_tich?.bieu_thuc) notes.push(`Điểm thành tích: ${value.diem_thanh_tich.bieu_thuc}.`)
  if (value.diem_thuong?.bieu_thuc) notes.push(`Điểm thưởng: ${value.diem_thuong.bieu_thuc}.`)
  if (value.phong_van) {
    const interview = value.phong_van
    const pass = interview.diem_phong_van_dat_toi_thieu
    const scale = interview.thang_diem_phong_van
    if (pass != null) {
      notes.push(
        `Phỏng vấn đạt từ ${pass}${scale != null ? `/${scale}` : ''} điểm và không cộng vào điểm xét tuyển.`,
      )
    }
  }
  const letters = rule.bang_quy_doi_diem_chu
  const letterText = letters && typeof letters === 'object'
    ? Object.entries(letters).map(([letter, score]) => `${letter} = ${score}`).join(', ')
    : ''
  if (letterText) notes.push(`Quy đổi điểm chữ: ${letterText}.`)
  const formula = value.cong_thuc_hien_thi || criterion.noi_dung_tieu_chi || value.cong_thuc || ''
  if (!formula && !notes.length) return null
  return {
    kind: 'formula',
    title: value.ma_chung_chi || criterion.ten_tieu_chi || '',
    formula,
    notes,
  }
}

function scoreGroups(criterion) {
  const value = asData(criterion.gia_tri_tieu_chi) || {}
  const table = value.bang_diem
  if (!table || typeof table !== 'object' || Array.isArray(table)) return null
  const groups = Object.entries(table)
    .filter(([, rows]) => Array.isArray(rows) && rows.length)
    .map(([key, rows]) => ({
      title: GROUP_LABELS[key] || key.replaceAll('_', ' '),
      rows: rows.map((row) => ({
        loai: scoreLabel(row?.loai),
        diem: row?.diem ?? null,
      })),
    }))
  if (!groups.length) return null
  const notes = [criterion.noi_dung_tieu_chi, value.quy_tac_dieu_kien, value.quy_tac_chong_trung].filter(Boolean)
  return {
    kind: 'groups',
    title: criterion.ten_tieu_chi || '',
    notes,
    groups,
  }
}

function textBlock(criterion) {
  const content = text(criterion.noi_dung_tieu_chi)
  if (!content) return null
  return {
    kind: 'text',
    title: criterion.ten_tieu_chi || '',
    text: content,
    notes: [],
  }
}

function blockFor(section, criterion) {
  if (section === 'quy_doi') return conversionBlock(criterion)
  if (section === 'thuong') return bonusBlock(criterion)
  if (section === 'cong_thuc') return formulaBlock(criterion)
  if (section === 'bang_diem') return scoreGroups(criterion)
  return textBlock(criterion)
}

function methodFormulas(methods) {
  const seen = new Set()
  const blocks = []
  for (const method of methods) {
    const formula = text(method?.cong_thuc_tinh_diem)
    if (!formula || seen.has(formula)) continue
    seen.add(formula)
    blocks.push({ kind: 'text', title: '', text: formula, notes: [] })
  }
  return blocks
}

export function buildMethodDetail({ label, subtitle, methods, criteria }) {
  const items = referencedCriteria(methods || [], criteria || [])
  const grouped = new Map(SECTION_ORDER.map(([key]) => [key, []]))
  for (const item of items) {
    const key = sectionKey(item)
    const block = blockFor(key, item)
    if (block) grouped.get(key).push(block)
  }
  const formulas = grouped.get('cong_thuc')
  if (!formulas.some((block) => block.kind === 'formula')) {
    formulas.unshift(...methodFormulas(methods || []))
  }

  const sections = SECTION_ORDER
    .map(([key, title]) => ({ key, title, blocks: grouped.get(key) }))
    .filter((section) => section.blocks.length)

  return {
    title: label || 'Phương thức tuyển sinh',
    subtitle: text(subtitle),
    sections,
  }
}
