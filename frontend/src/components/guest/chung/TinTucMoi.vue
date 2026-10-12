<script>
const defaultItems = [
  {
    id: 'chon-huong-thcs',
    date: '2026-10-08',
    title: 'Ba câu hỏi trước khi chọn hướng lên THPT',
    summary: 'Đối chiếu sở thích, môn học thế mạnh và nhóm tính cách để chọn tổ hợp phù hợp.',
  },
  {
    id: 'holland-nganh-hoc',
    date: '2026-10-02',
    title: 'Nhóm Holland gắn với ngành học nào?',
    summary: 'Cách đọc kết quả R, I, A, S, E, C và đối chiếu với lĩnh vực đào tạo.',
  },
  {
    id: 'phu-huynh-dong-hanh',
    date: '2026-09-25',
    title: 'Phụ huynh cùng con chọn ngành',
    summary: 'Những điểm nên hỏi trước khi chốt trường, ngành và phương thức xét tuyển.',
  },
  {
    id: 'sinh-vien-doi-huong',
    date: '2026-09-18',
    title: 'Sinh viên muốn đổi hướng học',
    summary: 'Khi nào nên học tiếp ngành hiện tại và khi nào nên xem lại định hướng nghề.',
  },
  {
    id: 'nha-tuyen-dung',
    date: '2026-09-10',
    title: 'Nhà tuyển dụng nhìn nhóm tính cách ra sao',
    summary: 'Gợi ý cách dùng kết quả trắc nghiệm khi giới thiệu bản thân trong hồ sơ.',
  },
]
</script>

<script setup>
defineOptions({ name: 'TinTucMoi' })

defineProps({
  title: { type: String, default: 'Tin tức mới' },
  items: { type: Array, default: () => defaultItems },
})

function formatDate(value) {
  const [year, month, day] = String(value).split('-')
  if (!year || !month || !day) return value
  return `${day}/${month}/${year}`
}
</script>

<template>
  <aside class="news-panel" aria-labelledby="tin-tuc-moi-title">
    <h2 id="tin-tuc-moi-title" class="news-panel__title">{{ title }}</h2>
    <ul class="news-panel__list">
      <li v-for="item in items" :key="item.id">
        <article class="news-item">
          <time class="news-item__date" :datetime="item.date">{{ formatDate(item.date) }}</time>
          <h3 class="news-item__title">{{ item.title }}</h3>
          <p class="news-item__summary">{{ item.summary }}</p>
        </article>
      </li>
    </ul>
  </aside>
</template>
