"""Tách file .sql thành từng câu lệnh để chạy qua SQLAlchemy/Alembic (op.execute).

Trình điều khiển MySQL của Python không hiểu lệnh DELIMITER và không chạy được nhiều
câu lệnh trong một lần gọi, nên các file trong thư mục này phải được tách trước.

Dùng trong migration:
    from chay_sql import doc_cau_lenh
    for cau in doc_cau_lenh('01_schema.sql'):
        op.execute(sa.text(cau).execution_options(no_parameters=True))   # hoặc op.get_bind().exec_driver_sql(cau)

Kiểm tra nhanh không cần CSDL:
    python chay_sql.py 01_schema.sql 02_thu_tuc.sql
"""
import re
import sys

BACKSLASH = chr(92)


def tach_cau_lenh(sql):
    """Tách theo dấu ; nằm ngoài chuỗi, ngoài tên trong dấu ` và ngoài chú thích."""
    out, buf, i, n, quote = [], [], 0, len(sql), None
    while i < n:
        ch = sql[i]
        if quote:
            buf.append(ch)
            if ch == BACKSLASH and i + 1 < n:
                buf.append(sql[i + 1])
                i += 1
            elif ch == quote:
                quote = None
        elif ch in ("'", '"', '`'):
            quote = ch
            buf.append(ch)
        elif sql.startswith('--', i) and (i + 2 >= n or sql[i + 2] in ' \t\r\n'):
            while i < n and sql[i] != '\n':
                i += 1
            continue
        elif sql.startswith('/*', i):
            i = sql.index('*/', i) + 2
            continue
        elif ch == ';':
            cau = ''.join(buf).strip()
            if cau:
                out.append(cau)
            buf = []
        else:
            buf.append(ch)
        i += 1
    cau = ''.join(buf).strip()
    if cau:
        out.append(cau)
    return out


def tach_script(sql):
    """Hỗ trợ cả file có DELIMITER $$ (hàm, thủ tục)."""
    if not re.search(r'(?mi)^\s*DELIMITER\s', sql):
        return tach_cau_lenh(sql)
    out, delim = [], ';'
    for dong_delim, phan in _theo_delimiter(sql):
        delim = dong_delim or delim
        if delim == ';':
            out.extend(tach_cau_lenh(phan))
        else:
            for khoi in phan.split(delim):
                # bỏ các dòng chú thích đứng trước câu lệnh
                khoi = re.sub(r'(?m)^\s*--.*$', '', khoi).strip() if not re.search(r'(?i)\bBEGIN\b', khoi) else khoi.strip()
                if khoi:
                    out.append(khoi)
    return out


def _theo_delimiter(sql):
    """Sinh (delimiter mới hoặc None, đoạn SQL theo sau)."""
    vi_tri, delim = 0, None
    for m in re.finditer(r'(?mi)^\s*DELIMITER\s+(\S+)\s*$', sql):
        yield delim, sql[vi_tri:m.start()]
        delim, vi_tri = m.group(1), m.end()
    yield delim, sql[vi_tri:]


def doc_cau_lenh(duong_dan):
    with open(duong_dan, encoding='utf-8') as f:
        return tach_script(f.read())


if __name__ == '__main__':
    for ten in sys.argv[1:]:
        ds = doc_cau_lenh(ten)
        dem = {}
        for cau in ds:
            dau = re.sub(r'(?m)^\s*--.*$', '', cau).split()
            khoa = ' '.join(dau[:2]).upper() if dau and dau[0].upper() in ('CREATE', 'DROP', 'ALTER') else (dau[0].upper() if dau else '?')
            dem[khoa] = dem.get(khoa, 0) + 1
        print(f'{ten}: {len(ds)} câu lệnh', dem)
