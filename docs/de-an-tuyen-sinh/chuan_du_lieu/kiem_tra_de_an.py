"""Kiểm tra một file đề án theo cấu trúc chuẩn trước khi nạp vào hệ thống.

Cách dùng:
    python kiem_tra_de_an.py mau_NTH_2026.json [file_khac.json ...]

Kiểm tra 3 lớp:
  1. Đúng cấu trúc theo de_an_xet_tuyen.schema.json (cần `pip install jsonschema`).
  2. Tham chiếu nội bộ: mã công thức, mã bảng quy đổi, mã cơ sở, mã trùng lặp...
  3. Mã danh mục (môn, tổ hợp, bài thi, chứng chỉ, thành tích, phương thức, tỉnh, trường, ngành)
     theo danh_muc_ma.json nếu file này nằm cùng thư mục.
LỖI làm file không nạp được. CẢNH BÁO là chỗ nên xem lại nhưng vẫn nạp được.
Mã thoát: 0 nếu không có lỗi, 1 nếu có lỗi.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHI_SO_CAN_KHOA = {
    'MON_CHUYEN': 'mon_hoc', 'DIEM_THI_THPT': 'mon_hoc', 'DIEM_HOC_BA_TB': 'mon_hoc',
    'DIEM_BAI_THI': 'bai_thi', 'DIEM_CHUNG_CHI': 'chung_chi', 'CO_CHUNG_CHI': 'chung_chi',
    'THANH_TICH': 'thanh_tich', 'TBC_LOP': 'lop', 'HOC_LUC_LOP': 'lop', 'REN_LUYEN_LOP': 'lop',
}


def tai_danh_muc():
    path = os.path.join(HERE, 'danh_muc_ma.json')
    if not os.path.exists(path):
        return None
    dm = json.load(open(path, encoding='utf-8'))
    ma = {k: {x['ma'] for x in v} for k, v in dm.items() if isinstance(v, list)}
    ma['lop'] = {'10', '11', '12'}
    ma['_to_hop'] = {x['ma']: x['vi_tri'] for x in dm['to_hop']}
    ma['_nhom_mon'] = {x['ma']: x['nhom'] for x in dm['mon_hoc']}
    return ma


def kiem_tra(doc, dm):
    loi, canh_bao = [], []

    def trung(ds, khoa, ten):
        seen = set()
        for x in ds:
            v = x.get(khoa)
            if v in seen:
                loi.append(f'{ten}: mã "{v}" bị trùng')
            seen.add(v)
        return seen

    def co_ma(loai, ma, vi_tri):
        if dm is not None and ma is not None and ma not in dm[loai]:
            loi.append(f'{vi_tri}: mã "{ma}" không có trong danh mục {loai}')

    co_so = trung(doc.get('co_so', []), 'ma_co_so', 'co_so')
    bang = {b['ma_bang']: b for b in doc.get('bang_quy_doi', [])}
    trung(doc.get('bang_quy_doi', []), 'ma_bang', 'bang_quy_doi')
    cong_thuc = {c['ma_cong_thuc']: c for c in doc['cong_thuc']}
    trung(doc['cong_thuc'], 'ma_cong_thuc', 'cong_thuc')
    trung(doc['chuong_trinh'], 'ma_chuong_trinh', 'chuong_trinh')
    to_hop_rieng = {t['ma_to_hop']: t['vi_tri'] for t in doc.get('to_hop_rieng', [])}

    co_ma('truong', doc['ma_truong'], 'ma_truong')
    for c in doc.get('co_so', []):
        co_ma('tinh_thanh', c['ma_tinh'], f'co_so {c["ma_co_so"]}')
    for ma, vt in to_hop_rieng.items():
        for pos in vt:
            for m in pos:
                co_ma('mon_hoc', m, f'to_hop_rieng {ma}')

    def vi_tri_to_hop(ma):
        if ma in to_hop_rieng:
            return to_hop_rieng[ma]
        if dm is None:
            return None
        return dm['_to_hop'].get(ma)

    def kiem_nhom(n, vi_tri, cho_phep_ct=False):
        if n.get('ma_cong_thuc') is not None:
            if not cho_phep_ct:
                loi.append(f'{vi_tri}: nhóm {n["ma_nhom"]} không được khai ma_cong_thuc ở vị trí này')
            elif n['ma_cong_thuc'] not in cong_thuc:
                loi.append(f'{vi_tri}: nhóm {n["ma_nhom"]} tham chiếu công thức không tồn tại "{n["ma_cong_thuc"]}"')
        for d in n['mot_trong']:
            kiem_chi_so(d, f'{vi_tri} / nhóm {n["ma_nhom"]}')

    def kiem_chi_so(d, vi_tri):
        loai = CHI_SO_CAN_KHOA.get(d['ma_chi_so'])
        khoa = d.get('khoa', '')
        if loai and not khoa:
            loi.append(f'{vi_tri}: chỉ số {d["ma_chi_so"]} phải có khoa')
        elif not loai and khoa:
            loi.append(f'{vi_tri}: chỉ số {d["ma_chi_so"]} không dùng khoa (đang là "{khoa}")')
        elif loai:
            co_ma(loai, khoa, f'{vi_tri} / {d["ma_chi_so"]}')

    # bảng quy đổi
    for b in doc.get('bang_quy_doi', []):
        for i, m in enumerate(b['muc'], 1):
            vt = f'bang_quy_doi {b["ma_bang"]} mức {i}'
            co_ma('chung_chi', m.get('ma_chung_chi'), vt)
            co_ma('bai_thi', m.get('ma_bai_thi'), vt)
            co_ma('mon_hoc', m.get('ma_mon_thay_the'), vt)
            tu, den = m.get('diem_tu'), m.get('diem_den')
            if tu is not None and den is not None and tu > den:
                loi.append(f'{vt}: diem_tu lớn hơn diem_den')
            if m.get('he_so_noi_suy') and tu is None:
                loi.append(f'{vt}: có he_so_noi_suy thì phải có diem_tu')
            if tu is None and den is None and not m.get('cap_do'):
                canh_bao.append(f'{vt}: không có khoảng điểm và không có cấp độ, mọi kết quả đều khớp')

    # công thức
    for ma, c in cong_thuc.items():
        vt = f'cong_thuc {ma}'
        co_ma('phuong_thuc_cua_bo', c.get('ma_phuong_thuc_cua_bo') or '500', vt)
        b = c.get('ma_bang_quy_doi_ngoai_ngu')
        if b is not None and b not in bang:
            loi.append(f'{vt}: bảng quy đổi ngoại ngữ "{b}" không tồn tại')
        elif b is not None and not any(m.get('ma_mon_thay_the') for m in bang[b]['muc']):
            loi.append(f'{vt}: bảng "{b}" không có mức nào khai ma_mon_thay_the nên không thay được điểm môn ngoại ngữ')
        if c['kieu_tinh'] != 'TO_HOP_MON' and c.get('he_so_mon'):
            canh_bao.append(f'{vt}: he_so_mon chỉ có tác dụng với TO_HOP_MON')
        if c['kieu_tinh'] != 'THANH_PHAN' and c.get('thanh_phan'):
            canh_bao.append(f'{vt}: thanh_phan chỉ có tác dụng với THANH_PHAN')
        for h in c.get('he_so_mon') or []:
            co_ma('mon_hoc', h.get('ma_mon'), vt + ' / he_so_mon')
        for t in c.get('thanh_phan') or []:
            co_ma('bai_thi', t.get('ma_bai_thi'), vt + ' / thanh_phan')
            co_ma('mon_hoc', t.get('ma_mon'), vt + ' / thanh_phan')
            tb = t.get('ma_bang_quy_doi')
            if tb is not None and tb not in bang:
                loi.append(f'{vt}: thành phần vị trí {t["vi_tri"]} dùng bảng quy đổi không tồn tại "{tb}"')
        if c['kieu_tinh'] == 'THANH_PHAN':
            # điểm tối đa lý thuyết phải bằng thang điểm
            theo_vt = {}
            for t in c.get('thanh_phan') or []:
                tb = t.get('ma_bang_quy_doi')
                toi_da = bang[tb]['thang_diem_dich'] if tb in bang else None
                if toi_da is None:
                    theo_vt = None
                    break
                theo_vt[t['vi_tri']] = max(theo_vt.get(t['vi_tri'], 0), toi_da * t.get('he_so', 1))
            if theo_vt:
                tong = sum(theo_vt.values()) * (c.get('he_so_nhan') or 1)
                if abs(tong - c['thang_diem']) > 0.01:
                    canh_bao.append(f'{vt}: điểm tối đa theo các thành phần là {tong:.2f}, khác thang_diem {c["thang_diem"]}')
        for n in c.get('dieu_kien') or []:
            kiem_nhom(n, vt)

    for n in doc.get('dieu_kien_chung', []):
        kiem_nhom(n, 'dieu_kien_chung')

    # điểm cộng
    for i, d in enumerate(doc.get('diem_cong', []), 1):
        vt = f'diem_cong dòng {i}'
        if d.get('ma_cong_thuc') is not None and d['ma_cong_thuc'] not in cong_thuc:
            loi.append(f'{vt}: công thức "{d["ma_cong_thuc"]}" không tồn tại')
        kiem_chi_so(d, vt)

    # chương trình
    da_dung = set()
    da_bao_thang = set()
    for c in doc['chuong_trinh']:
        vt = f'chuong_trinh {c["ma_chuong_trinh"]}'
        if c.get('ma_co_so') is not None and c['ma_co_so'] not in co_so:
            loi.append(f'{vt}: cơ sở "{c["ma_co_so"]}" không tồn tại')
        co_ma('nganh', c.get('ma_nganh'), vt)
        if c.get('ma_nganh') is None:
            canh_bao.append(f'{vt}: chưa có ma_nganh')
        hp = c.get('hoc_phi')
        if hp and hp.get('hoc_phi_den') is not None and hp['hoc_phi_den'] < hp['hoc_phi_tu']:
            loi.append(f'{vt}: hoc_phi_den nhỏ hơn hoc_phi_tu')
        seen = set()
        for p in c['phuong_an']:
            ma = p['ma_cong_thuc']
            if ma not in cong_thuc:
                loi.append(f'{vt}: công thức "{ma}" không tồn tại')
                continue
            if ma in seen:
                loi.append(f'{vt}: công thức "{ma}" khai hai lần, hãy gộp tổ hợp vào một dòng')
            seen.add(ma)
            da_dung.add(ma)
            ct = cong_thuc[ma]
            if ct['kieu_tinh'] == 'TO_HOP_MON':
                if not p.get('to_hop'):
                    loi.append(f'{vt}: công thức "{ma}" kiểu TO_HOP_MON phải có to_hop')
                he_so = {h.get('ma_mon'): h['he_so'] for h in ct.get('he_so_mon') or [] if h.get('ma_mon')}
                he_so_nhom = {h['nhom_mon']: h['he_so'] for h in ct.get('he_so_mon') or [] if h.get('nhom_mon')}
                for th in p.get('to_hop', []):
                    vi_tri = vi_tri_to_hop(th)
                    if dm is not None and th not in to_hop_rieng and th not in dm['to_hop']:
                        loi.append(f'{vt}: tổ hợp "{th}" không có trong danh mục và không khai ở to_hop_rieng')
                        continue
                    if vi_tri is None:
                        if dm is not None:
                            loi.append(f'{vt}: tổ hợp "{th}" chưa có cấu trúc vị trí môn, hãy khai ở to_hop_rieng')
                        continue
                    nhom = dm['_nhom_mon'] if dm else {}
                    w = lambda m: he_so.get(m, he_so_nhom.get(nhom.get(m), 1))
                    if ct.get('thay_ngoai_ngu') == 'BAT_BUOC' and dm and not any(nhom.get(m) == 'Ngoại ngữ' for pos in vi_tri for m in pos):
                        loi.append(f'{vt}: công thức "{ma}" bắt buộc dùng chứng chỉ nhưng tổ hợp "{th}" không có môn ngoại ngữ')
                    for pos in vi_tri:
                        if len({w(m) for m in pos}) > 1:
                            loi.append(f'{vt}: tổ hợp "{th}" có các môn thay thế nhau nhưng khác hệ số trong công thức "{ma}"')
                    tong = sum(max(w(m) for m in pos) for pos in vi_tri) * 10 * (ct.get('he_so_nhan') or 1)
                    if abs(tong - ct['thang_diem']) > 0.01 and (ma, th) not in da_bao_thang:
                        da_bao_thang.add((ma, th))
                        canh_bao.append(f'cong_thuc {ma} với tổ hợp {th}: điểm tối đa theo hệ số là {tong:.2f}, khác thang_diem {ct["thang_diem"]}')
            elif p.get('to_hop'):
                canh_bao.append(f'{vt}: công thức "{ma}" không theo tổ hợp, to_hop sẽ bị bỏ qua')
        for n in c.get('dieu_kien_rieng') or []:
            kiem_nhom(n, vt, cho_phep_ct=True)

    for ma in cong_thuc:
        if ma not in da_dung:
            canh_bao.append(f'cong_thuc {ma}: không có chương trình nào dùng')

    # điểm chuẩn
    ma_xt = {c['ma_xet_tuyen'] for c in doc['chuong_trinh']}
    for i, d in enumerate(doc.get('diem_chuan', []), 1):
        vt = f'diem_chuan dòng {i}'
        co_ma('phuong_thuc_cua_bo', d.get('ma_phuong_thuc_cua_bo'), vt)
        if d['diem_chuan'] > d['thang_diem']:
            loi.append(f'{vt}: diem_chuan lớn hơn thang_diem')
        if d['nam_tuyen_sinh'] > doc['nam_tuyen_sinh']:
            loi.append(f'{vt}: năm điểm chuẩn lớn hơn năm của đề án')
        if d['ma_xet_tuyen'] not in ma_xt:
            canh_bao.append(f'{vt}: mã xét tuyển "{d["ma_xet_tuyen"]}" không có trong đề án năm nay nên sẽ không được dùng')
    if not doc.get('diem_chuan'):
        canh_bao.append('diem_chuan: chưa có điểm chuẩn năm trước, hệ thống sẽ không chấm được điểm phù hợp cho trường này')
    thieu_dc = sorted(ma_xt - {d['ma_xet_tuyen'] for d in doc.get('diem_chuan', [])})
    if doc.get('diem_chuan') and thieu_dc:
        canh_bao.append(f'diem_chuan: {len(thieu_dc)} mã xét tuyển chưa có điểm chuẩn: {", ".join(thieu_dc[:10])}{"..." if len(thieu_dc) > 10 else ""}')
    return loi, canh_bao


def main(files):
    schema = json.load(open(os.path.join(HERE, 'de_an_xet_tuyen.schema.json'), encoding='utf-8'))
    try:
        import jsonschema
        validator = jsonschema.Draft7Validator(schema)
    except ImportError:
        validator = None
        print('CHÚ Ý: chưa cài jsonschema nên bỏ qua bước kiểm tra cấu trúc (pip install jsonschema).')
    dm = tai_danh_muc()
    if dm is None:
        print('CHÚ Ý: không thấy danh_muc_ma.json nên bỏ qua bước kiểm tra mã danh mục.')
    co_loi = False
    for f in files:
        print(f'\n=== {f}')
        try:
            doc = json.load(open(f, encoding='utf-8'))
        except (OSError, ValueError) as e:
            print(f'LỖI: không đọc được file: {e}')
            co_loi = True
            continue
        loi_cau_truc = []
        if validator is not None:
            for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path)):
                loi_cau_truc.append('/'.join(str(p) for p in e.absolute_path) + ': ' + e.message[:200])
        if loi_cau_truc:
            co_loi = True
            print(f'{len(loi_cau_truc)} LỖI cấu trúc (sửa xong mới kiểm tra tiếp được):')
            for x in loi_cau_truc[:50]:
                print('  LỖI:', x)
            continue
        loi, canh_bao = kiem_tra(doc, dm)
        gom = {}
        for x in canh_bao:
            khoa = x.split(': ', 1)[-1] if x.startswith('chuong_trinh ') else x
            gom.setdefault(khoa, []).append(x)
        for x in loi:
            print('  LỖI:', x)
        for khoa, ds in gom.items():
            print('  CẢNH BÁO:', ds[0] if len(ds) == 1 else f'{len(ds)} chương trình: {khoa}')
        so_pa = sum(len(p.get('to_hop') or [1]) for c in doc['chuong_trinh'] for p in c['phuong_an'])
        print(f'Kết quả: {len(loi)} lỗi, {len(gom)} loại cảnh báo | {len(doc["cong_thuc"])} công thức, '
              f'{len(doc["chuong_trinh"])} chương trình, {so_pa} phương án')
        co_loi = co_loi or bool(loi)
    return 1 if co_loi else 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
