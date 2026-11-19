<template>
  <div class="kq-tab">
    <div class="row g-3">
      <div class="col-12 col-md-6">
        <article class="kq-card kq-buoc">
          <span class="kq-buoc__so">1</span>
          <h3 class="kq-card__title">Chọn ngành</h3>
          <p class="kq-muted">Tìm hiểu sâu 3–5 ngành phù hợp: môn học, cơ hội việc làm, mức lương tham khảo.</p>
          <div class="kq-actions">
            <button type="button" class="kq-link" @click="emit('chuyen-tab', 'phu-hop')">Xem ngành gợi ý</button>
            <RouterLink class="kq-link" :to="{ name: tenRoute('thpt-thi-dai-hoc-nganh-phu-hop'), params: { ssid }, query: routeQuery }">
              So sánh ngành
            </RouterLink>
          </div>
        </article>
      </div>
      <div class="col-12 col-md-6">
        <article class="kq-card kq-buoc">
          <span class="kq-buoc__so">2</span>
          <h3 class="kq-card__title">Chọn trường</h3>
          <p class="kq-muted">
            Từ danh sách ngành phù hợp, xem trường đào tạo từng ngành, phương thức xét tuyển, điểm chuẩn và khả năng
            trúng tuyển theo điểm của bạn.
          </p>
          <div class="kq-actions">
            <RouterLink
              class="btn btn-sm btn-success"
              :to="{ name: tenRoute('thpt-thi-dai-hoc-nganh-phu-hop'), params: { ssid }, query: routeQuery }"
            >
              Bắt đầu
            </RouterLink>
            <RouterLink v-if="daDangNhap" class="btn btn-sm btn-outline-success" :to="{ name: trangLichSu.timTruong }">
              Xem lịch sử tìm trường
            </RouterLink>
          </div>
        </article>
      </div>
      <div class="col-12 col-md-6">
        <article class="kq-card kq-buoc">
          <span class="kq-buoc__so">3</span>
          <h3 class="kq-card__title">Trải nghiệm nghề</h3>
          <ul v-if="traiNghiem.length" class="kq-list">
            <li v-for="(x, i) in traiNghiem" :key="i"><span class="kq-tag">{{ x.ma_nhom }}</span>{{ x.noi_dung }}</li>
          </ul>
          <p v-else class="kq-muted">Hoàn thành trắc nghiệm để nhận gợi ý trải nghiệm.</p>
        </article>
      </div>
      <div class="col-12 col-md-6">
        <article class="kq-card kq-buoc">
          <span class="kq-buoc__so">4</span>
          <h3 class="kq-card__title">Lập kế hoạch phát triển</h3>
          <ul class="kq-list">
            <li>Đặt mục tiêu điểm cho các môn của tổ hợp xét tuyển dự định.</li>
            <li>Rèn các kỹ năng gợi ý ở tab "Tôi cần cải thiện điều gì?".</li>
            <li>Trao đổi với gia đình, thầy cô trước khi chốt nguyện vọng.</li>
          </ul>
          <div class="kq-actions">
            <button type="button" class="btn btn-sm btn-outline-success" :disabled="!top.length" @click="tuVanAi">
              Hỏi trợ lý AI
            </button>
            <RouterLink v-if="daDangNhap" class="btn btn-sm btn-outline-success" :to="{ name: trangLichSu.tracNghiem }">
              Lịch sử trắc nghiệm
            </RouterLink>
            <button type="button" class="btn btn-sm btn-light" @click="saoChepLienKet">Sao chép đường dẫn kết quả</button>
          </div>
        </article>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
// import { useRouter } from 'vue-router' // chỉ dùng cho /demo-chat (đã tạm bỏ)
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { cauHoiTuVan, gopNoiDung } from '@/utils/ketQuaHolland'
import { useTenRouteThpt } from '../../../useTenRouteThpt'

const { tenRoute } = useTenRouteThpt()

const props = defineProps({
  ssid: { type: String, required: true },
  top: { type: Array, default: () => [] },
  routeQuery: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['chuyen-tab'])

// const router = useRouter()
const auth = useAuthStore()
const chat = useChatStore()

const daDangNhap = computed(() => auth.isAuthenticated)
// Quản trị viên xem lịch sử của mọi người ở trang quản trị; thành viên xem lịch sử của mình.
const trangLichSu = computed(() =>
  auth.isAdmin
    ? { tracNghiem: 'admin-lich-su-trac-nghiem', timTruong: 'admin-lich-su-tim-truong' }
    : { tracNghiem: 'lich-su-trac-nghiem', timTruong: 'lich-su-tim-truong' },
)
const traiNghiem = computed(() => gopNoiDung(props.top, 'trai_nghiem'))

// Mở khung chat nổi với câu hỏi tư vấn điền sẵn (trang /demo-chat đã tạm bỏ).
function tuVanAi() {
  chat.moKhungChat(cauHoiTuVan(props.top))
  // chat.state.draft = cauHoiTuVan(props.top)
  // router.push({ name: 'demo-chat' })
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
