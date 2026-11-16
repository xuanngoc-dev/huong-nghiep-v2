<template>
  <div class="kq-lo-trinh">
    <div class="row g-3">
      <div class="col-12 col-lg-7">
        <article class="kq-card">
          <h3 class="kq-card__title">Các bước tiếp theo</h3>
          <ol class="kq-steps">
            <li>
              <strong>Tìm hiểu sâu 3–5 nghề và ngành</strong>
              <span>Đọc mô tả công việc, môn học, mức lương và cơ hội việc làm của các ngành phù hợp; đánh dấu "Quan tâm".</span>
              <button type="button" class="kq-link" @click="emit('chuyen-tab', 'nghe-nghiep')">Xem nghề nghiệp và ngành</button>
            </li>
            <li>
              <strong>Đối chiếu với năng lực thực tế</strong>
              <span>So sở thích với kết quả học tập, môn mạnh, sức khỏe và điều kiện gia đình; sở thích chưa phải là năng lực.</span>
              <RouterLink v-if="daDangNhap" class="kq-link" :to="{ name: 'ho-so' }">Cập nhật hồ sơ năng lực</RouterLink>
            </li>
            <li>
              <strong>Trải nghiệm trước khi quyết định</strong>
              <span>Thử các hoạt động gợi ý bên cạnh để kiểm chứng mình có thật sự hứng thú.</span>
            </li>
            <li>
              <strong>Chọn trường và phương thức xét tuyển</strong>
              <span>Xem trường đào tạo ngành quan tâm, điểm chuẩn và khả năng trúng tuyển theo điểm của bạn.</span>
              <RouterLink v-if="maNganhTimTruong" class="kq-link" :to="lienKetTimTruong">Tìm trường phù hợp</RouterLink>
            </li>
            <li>
              <strong>Trao đổi trước khi chốt nguyện vọng</strong>
              <span>Chia sẻ kết quả với gia đình, thầy cô hoặc hỏi trợ lý AI để có thêm góc nhìn.</span>
            </li>
          </ol>
        </article>
      </div>
      <div class="col-12 col-lg-5">
        <article class="kq-card">
          <h3 class="kq-card__title">Gợi ý trải nghiệm nghề nghiệp</h3>
          <ul v-if="traiNghiem.length" class="kq-list">
            <li v-for="(x, i) in traiNghiem" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
          </ul>
          <p v-else class="kq-muted">Hoàn thành trắc nghiệm để nhận gợi ý trải nghiệm.</p>
        </article>
      </div>
    </div>

    <article class="kq-card">
      <header class="kq-section-head kq-section-head--row">
        <h3 class="kq-card__title">Danh sách quan tâm</h3>
        <span class="kq-muted">Lưu trên trình duyệt này cho lần làm bài hiện tại.</span>
      </header>
      <p v-if="!quanTam.nganh.length && !quanTam.truong.length" class="kq-muted">
        Chưa có lựa chọn nào. Bấm "Quan tâm" ở ngành hoặc trường trong tab Nghề nghiệp &amp; đào tạo.
      </p>
      <div v-else class="row g-3">
        <div class="col-12 col-md-6">
          <h4 class="kq-y__title">Ngành ({{ quanTam.nganh.length }})</h4>
          <ul class="kq-chips">
            <li v-for="item in quanTam.nganh" :key="item.ma_nganh" class="kq-chip">
              <RouterLink :to="{ name: 'thpt-thi-dai-hoc-chi-tiet-nganh', params: { ssid, maNganh: item.ma_nganh }, query: routeQuery }">
                {{ item.ma_nganh }} — {{ item.ten_nganh }}
              </RouterLink>
              <button type="button" class="kq-chip__remove" :aria-label="`Bỏ quan tâm ${item.ten_nganh}`" @click="emit('doi-quan-tam', 'nganh', item)">
                ×
              </button>
            </li>
          </ul>
        </div>
        <div class="col-12 col-md-6">
          <h4 class="kq-y__title">Trường ({{ quanTam.truong.length }})</h4>
          <ul class="kq-chips">
            <li v-for="item in quanTam.truong" :key="item.ma_truong" class="kq-chip">
              <RouterLink
                :to="{ name: 'thpt-thi-dai-hoc-chi-tiet-truong', params: { ssid, maTruong: item.ma_truong }, query: { ...routeQuery, ma_nganh: item.ma_nganh } }"
              >
                {{ item.ten_truong }}
              </RouterLink>
              <button type="button" class="kq-chip__remove" :aria-label="`Bỏ quan tâm ${item.ten_truong}`" @click="emit('doi-quan-tam', 'truong', item)">
                ×
              </button>
            </li>
          </ul>
        </div>
      </div>
    </article>

    <div class="row g-3">
      <div class="col-12 col-md-6 col-xl-4">
        <article class="kq-card kq-action">
          <h4 class="kq-y__title">Tìm trường phù hợp</h4>
          <p class="kq-muted">
            {{ maNganhTimTruong ? `Theo ngành ${tenNganhTimTruong}, dựa trên điểm và nguyện vọng của bạn.` : 'Chọn một ngành quan tâm để tìm trường.' }}
          </p>
          <RouterLink v-if="maNganhTimTruong" class="btn btn-success" :to="lienKetTimTruong">Tìm trường</RouterLink>
        </article>
      </div>
      <div class="col-12 col-md-6 col-xl-4">
        <article class="kq-card kq-action">
          <h4 class="kq-y__title">Tư vấn với trợ lý AI</h4>
          <p class="kq-muted">Hỏi thêm về ngành, nghề phù hợp với mã {{ maNoiBat || 'Holland' }} của bạn.</p>
          <button type="button" class="btn btn-success" :disabled="!top.length" @click="tuVanAi">Hỏi trợ lý AI</button>
        </article>
      </div>
      <div class="col-12 col-xl-4">
        <article class="kq-card kq-action">
          <h4 class="kq-y__title">Lưu kết quả</h4>
          <p v-if="daDangNhap" class="kq-muted">Các lần làm trắc nghiệm khi đã đăng nhập được lưu trong lịch sử trắc nghiệm.</p>
          <p v-else class="kq-muted">
            Bạn chưa đăng nhập: hãy lưu đường dẫn để mở lại kết quả. Đăng nhập trước khi làm bài để kết quả được lưu vào tài khoản.
          </p>
          <div class="kq-actions">
            <RouterLink v-if="daDangNhap" class="btn btn-success" :to="{ name: 'lich-su-trac-nghiem' }">Xem lịch sử</RouterLink>
            <button type="button" class="btn btn-outline-success" @click="saoChepLienKet">Sao chép đường dẫn</button>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { cauHoiTuVan, gopNoiDung } from '@/utils/ketQuaHolland'

const props = defineProps({
  ssid: { type: String, required: true },
  top: { type: Array, default: () => [] },
  maNoiBat: { type: String, default: '' },
  nganh: { type: Array, default: () => [] },
  quanTam: { type: Object, required: true },
  routeQuery: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['doi-quan-tam', 'chuyen-tab'])

const router = useRouter()
const auth = useAuthStore()
const chat = useChatStore()

const daDangNhap = computed(() => auth.isAuthenticated)
const traiNghiem = computed(() => gopNoiDung(props.top, 'trai_nghiem'))
// Ngành để tìm trường: ngành quan tâm đầu tiên, không có thì ngành phù hợp nhất.
const nganhTimTruong = computed(() => props.quanTam.nganh[0] || props.nganh[0] || null)
const maNganhTimTruong = computed(() => nganhTimTruong.value?.ma_nganh || '')
const tenNganhTimTruong = computed(() => nganhTimTruong.value?.ten_nganh || maNganhTimTruong.value)
const lienKetTimTruong = computed(() => ({
  name: 'thpt-thi-dai-hoc-truong-phu-hop',
  params: { maNganh: maNganhTimTruong.value },
}))

function tuVanAi() {
  chat.state.draft = cauHoiTuVan(props.top)
  router.push({ name: 'demo-chat' })
}

async function saoChepLienKet() {
  try {
    await navigator.clipboard.writeText(window.location.href)
    ElMessage.success('Đã sao chép đường dẫn kết quả')
  } catch {
    ElMessage.error('Không sao chép được, hãy sao chép đường dẫn trên thanh địa chỉ')
  }
}
</script>

<style scoped src="./ket-qua.css"></style>
