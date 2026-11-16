// Chạy bộ tính JS gốc trong test_xet_tuyen.html, xuất kết quả để đối chiếu với bản Python.
import { readFileSync, writeFileSync } from 'node:fs'
const html = readFileSync(process.argv[2], 'utf8')
const lay = (dau, cuoi) => html.slice(html.indexOf(dau), html.indexOf(cuoi) + cuoi.length)
const dong = html.split('\n')
const ma = [dong[160], lay('//<ENGINE>', '//</ENGINE>'), lay('//<PRESETS>', '//</PRESETS>'),
  'return { DATA, XT, PRESETS }'].join('\n')
const { DATA, XT, PRESETS } = new Function(ma)()
const I = XT.index(DATA)
const opt = { nam: 2026, homNay: '2026-07-01', diemChuan: DATA.diemChuanDemo }
const cfg = { trongSo: DATA.trongSo }
const out = { tuy_chon: opt, ho_so: {} }
for (const ten of Object.keys(PRESETS)) {
  const hs = PRESETS[ten]
  const kq = XT.tinhPhuongAn(I, hs, opt)
  const rows = XT.xepHang(I, hs, kq, cfg, null)
  out.ho_so[ten] = {
    ho_so: hs,
    muc_uu_tien: kq.mucUt,
    phuong_an: kq.phuongAn.map(p => ({ paId: p.paId, ctr: p.ctr, ct: p.ct, toHop: p.toHop, kieu: p.kieu, goc: p.goc,
      tb: p.tb, thpt: p.thpt, cong: p.cong, ut: p.ut, xet: p.xet, datNguong: p.datNguong, du: p.du, lyDo: p.lyDo,
      soNhom: p.soNhom, soDat: p.soDat, dc: p.dc, namDc: p.namDc, chenh: p.chenh, chiTiet: p.chiTiet })),
    xep_hang: rows.map(r => ({ hang: r.hang, ctr: r.ctr, paId: r.pa.paId, xetThang: r.xetThang, kn: r.kn, nhanKn: r.nhanKn,
      hp: r.hp, vt: r.vt, ph: r.ph, loai: r.loai })),
    theo_truong: XT.theoTruong(rows).map(t => ({ truong: t.truong, so: t.so, daCham: t.daCham, phuHop: t.phuHop,
      caoNhat: t.caoNhat, diem: t.diem, hangTot: t.hangTot })),
  }
  console.log(ten, 'phương án', kq.phuongAn.length, 'chương trình xếp hạng', rows.length)
}
writeFileSync(process.argv[3], JSON.stringify(out))
writeFileSync(process.argv[4], JSON.stringify(DATA))
