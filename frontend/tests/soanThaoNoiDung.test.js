import { test } from 'node:test'
import assert from 'node:assert/strict'
import { taoSlug } from '../src/utils/slug.js'
import { anhTuongDoi, anhTuyetDoi } from '../src/utils/anhNoiDung.js'
import { chuanHoaHtmlDan, htmlHoacRong, laAnhNgoai } from '../src/components/admin/soan-thao/noiDungHtml.js'

test('slug từ tiêu đề tiếng Việt (cùng quy tắc với backend)', () => {
  assert.equal(taoSlug('Đề án tuyển sinh 2026: Những điều cần biết!'), 'de-an-tuyen-sinh-2026-nhung-dieu-can-biet')
  assert.equal(taoSlug('  Hướng   nghiệp – THPT  '), 'huong-nghiep-thpt')
  assert.equal(taoSlug('Ứng dụng AI vào học tập'), 'ung-dung-ai-vao-hoc-tap')
  assert.equal(taoSlug('---'), '')
  assert.equal(taoSlug(null), '')
  assert.equal(taoSlug('a'.repeat(300)).length, 255)
})

test('HTML dán từ trang khác: h1 → h2, h5/h6 → h4, bỏ script/style/meta/comment', () => {
  const html =
    '<meta charset="utf-8"><!--StartFragment--><h1 class="t">Tiêu đề</h1><style>p{color:red}</style>' +
    '<p>Đoạn</p><script>alert(1)</script><h5>Nhỏ</h5><h6 id="x">Nhỏ hơn</h6><!--EndFragment-->'
  assert.equal(chuanHoaHtmlDan(html), '<h2 class="t">Tiêu đề</h2><p>Đoạn</p><h4>Nhỏ</h4><h4 id="x">Nhỏ hơn</h4>')
  assert.equal(chuanHoaHtmlDan('<header>giữ</header><hr>'), '<header>giữ</header><hr>')
})

test('nội dung rỗng của Tiptap lưu thành chuỗi rỗng', () => {
  assert.equal(htmlHoacRong('<p></p>'), '')
  assert.equal(htmlHoacRong(' <p>a</p> '), '<p>a</p>')
})

test('ảnh ngoài và đổi đường dẫn ảnh Thư viện', () => {
  const goc = 'https://api.vd.vn'
  assert.equal(laAnhNgoai('https://vnexpress.net/a.jpg', goc), true)
  assert.equal(laAnhNgoai('https://api.vd.vn/api/v1/thu-vien/tep/a.jpg', goc), false)
  assert.equal(laAnhNgoai('https://api.vd.vn.gia-mao.com/a.jpg', goc), true)
  assert.equal(laAnhNgoai('/api/v1/thu-vien/tep/a.jpg', goc), false)
  assert.equal(laAnhNgoai('data:image/png;base64,xx', goc), false)

  const luu = '<p>x</p><img src="/api/v1/thu-vien/tep/a.jpg" alt="a"><img src="https://khac.vn/b.png">'
  const hienThi = '<p>x</p><img src="https://api.vd.vn/api/v1/thu-vien/tep/a.jpg" alt="a"><img src="https://khac.vn/b.png">'
  assert.equal(anhTuyetDoi(luu, goc), hienThi)
  assert.equal(anhTuongDoi(hienThi, goc), luu)
  // Không có origin API (frontend gọi API cùng domain) thì giữ nguyên.
  assert.equal(anhTuyetDoi(luu, ''), luu)
  // URL bắt đầu bằng // (giao thức tương đối) không bị coi là đường dẫn Thư viện.
  assert.equal(anhTuyetDoi('<img src="//cdn.vn/c.png">', goc), '<img src="//cdn.vn/c.png">')
})
