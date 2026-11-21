<template>
  <!-- Trang /demo-chat đã tạm bỏ: <div v-if="route.name !== 'demo-chat'" class="chatbot"> -->
  <div ref="rootEl" class="chatbot">
    <section v-if="chat.khungMo" id="chatbot-panel" ref="panelEl" class="chatbot__panel" aria-label="Trợ lý tuyển sinh">
      <header class="chatbot__header">
        <div class="chatbot__tieu-de">
          <strong>Trợ lý tuyển sinh</strong>
          <small>Bạn là: {{ tenDoiTuongHuongDen(chat.state.doiTuongHuongDen) }}</small>
        </div>
        <div class="chatbot__header-actions">
          <button
            type="button"
            class="chatbot__btn-icon"
            :class="{ 'is-active': caiDatMo }"
            aria-label="Cài đặt trợ lý"
            title="Cài đặt"
            aria-controls="chatbot-cai-dat"
            :aria-expanded="caiDatMo"
            @click="caiDatMo = !caiDatMo"
          >
            <el-icon :size="16"><Setting /></el-icon>
          </button>
          <!-- Trang /demo-chat đã tạm bỏ:
          <button type="button" class="chatbot__btn-icon" aria-label="Mở trang đầy đủ" title="Mở trang đầy đủ" @click="expand">
            <el-icon :size="16"><FullScreen /></el-icon>
          </button>
          -->
          <!-- Thành viên: mở hội thoại đang chat trong trang Danh sách hội thoại (khách không có danh sách này). -->
          <button
            v-if="auth.isAuthenticated"
            type="button"
            class="chatbot__btn-icon"
            aria-label="Mở trong Danh sách hội thoại"
            title="Mở trong Danh sách hội thoại"
            :disabled="chat.state.sending"
            @click="moDanhSachHoiThoai"
          >
            <el-icon :size="16"><FullScreen /></el-icon>
          </button>
          <button type="button" class="chatbot__close" aria-label="Đóng khung chat" @click="chat.khungMo = false">
            <el-icon :size="16"><Close /></el-icon>
          </button>
        </div>
        <!-- Cài đặt: đối tượng hướng đến. Đổi được tới khi gửi câu hỏi đầu (server chốt vào phiên). -->
        <div v-if="caiDatMo" id="chatbot-cai-dat" class="chatbot__cai-dat" role="dialog" aria-label="Cài đặt trợ lý">
          <div class="chatbot__cai-dat-dau">
            <strong>Bạn là</strong>
            <button type="button" class="chatbot__cai-dat-dong" aria-label="Đóng cài đặt" @click="caiDatMo = false">
              <el-icon :size="14"><Close /></el-icon>
            </button>
          </div>
          <p v-if="chat.daChotDoiTuong" class="chatbot__cai-dat-ghi-chu">
            Đã chốt cho cuộc hội thoại này. Bấm <b>Kết thúc</b> để bắt đầu hội thoại mới với đối tượng khác.
          </p>
          <p v-else class="chatbot__cai-dat-ghi-chu">Trợ lý trả lời theo hoàn cảnh của đối tượng bạn chọn.</p>
          <div class="chatbot__cai-dat-ds" role="group" aria-label="Chọn đối tượng người hỏi">
            <button
              v-for="item in DOI_TUONG_HUONG_DEN"
              :key="item.ma"
              type="button"
              :class="{ 'is-active': item.ma === chat.state.doiTuongHuongDen }"
              :aria-pressed="item.ma === chat.state.doiTuongHuongDen"
              :disabled="chat.daChotDoiTuong || chat.state.sending"
              @click="chonDoiTuong(item.ma)"
            >
              {{ item.label }}
            </button>
          </div>
          <!-- Khách: mời đăng nhập, nút ở góc phải bên dưới. -->
          <div v-if="!auth.isAuthenticated" class="chatbot__cai-dat-chan">
            <p class="chatbot__cai-dat-meo">
              <el-icon :size="14"><InfoFilled /></el-icon>
              <span>Mẹo: tạo tài khoản để lưu và xem lại lịch sử hội thoại, lưu kết quả trắc nghiệm, và để trợ lý dựa vào hồ sơ cá nhân (điểm, chứng chỉ, khu vực) tư vấn sát với bạn hơn.</span>
            </p>
            <button type="button" class="chatbot__dang-nhap" @click="dangNhap">Đăng nhập</button>
          </div>
        </div>
      </header>
      <ChatPanel compact />
    </section>
    <button type="button" class="guest-fab" aria-label="Mở chatbot" aria-controls="chatbot-panel" :aria-expanded="chat.khungMo" @click="chat.khungMo = !chat.khungMo">
      <el-icon :size="22"><ChatDotRound /></el-icon>
    </button>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DOI_TUONG_KEY } from '@/data/doiTuong'
import { DOI_TUONG_HUONG_DEN, doiTuongTheoTrang, tenDoiTuongHuongDen } from '@/constants/doiTuongHuongDen'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import ChatPanel from './ChatPanel.vue'

defineOptions({ name: 'Chatbot' })
// Trạng thái mở khung nằm trong store để các nút "Hỏi trợ lý AI" ở trang khác mở được khung này.
const chat = useChatStore()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const caiDatMo = ref(false)
function chonDoiTuong(ma) {
  chat.chonDoiTuong(ma)
  caiDatMo.value = false
}
function dangNhap() {
  caiDatMo.value = false
  chat.khungMo = false
  router.push({ name: 'login', query: { redirect: route.fullPath } })
}
// Đối tượng hướng đến mặc định của hội thoại mới theo trang đang xem (hoặc đối tượng đã chọn ở trang chủ).
watch(() => route.meta, (meta) => {
  let daChon = ''
  try {
    daChon = sessionStorage.getItem(DOI_TUONG_KEY) || ''
  } catch {
    daChon = ''
  }
  chat.datDoiTuongTrang(doiTuongTheoTrang(meta, daChon))
}, { immediate: true })
// Mobile toàn màn hình: khung bám theo vùng đang nhìn thấy (visualViewport) để khi bàn phím bật lên,
// trình duyệt cuộn trang không đẩy tiêu đề ra khỏi màn hình. Chỉ dùng trong media query mobile.
const panelEl = ref(null)
// Bấm ra ngoài khung chat (và nút mở) thì đóng khung. Dùng pointerdown thay cho click để nút "Hỏi trợ lý AI"
// ở nơi khác (mở khung bằng click) không bị đóng lại ngay trong cùng cú bấm. Bỏ qua hộp xác nhận / popup
// của Element Plus vì chúng được teleport ra body nhưng vẫn thuộc khung chat (vd. xác nhận Kết thúc).
const rootEl = ref(null)
function dongKhiBamRaNgoai(event) {
  if (!chat.khungMo || rootEl.value?.contains(event.target)) return
  if (event.target.closest?.('.el-overlay, .el-popper, .el-message')) return
  caiDatMo.value = false
  chat.khungMo = false
}
function capNhatKhungNhin() {
  const vv = window.visualViewport
  if (!vv || !panelEl.value) return
  panelEl.value.style.setProperty('--khung-nhin-cao', `${vv.height}px`)
  panelEl.value.style.setProperty('--khung-nhin-tren', `${vv.offsetTop}px`)
}
watch(panelEl, capNhatKhungNhin)
onMounted(() => {
  document.addEventListener('pointerdown', dongKhiBamRaNgoai)
  window.visualViewport?.addEventListener('resize', capNhatKhungNhin)
  window.visualViewport?.addEventListener('scroll', capNhatKhungNhin)
})
onUnmounted(() => {
  document.removeEventListener('pointerdown', dongKhiBamRaNgoai)
  window.visualViewport?.removeEventListener('resize', capNhatKhungNhin)
  window.visualViewport?.removeEventListener('scroll', capNhatKhungNhin)
})
// Hội thoại đã có câu hỏi (đã lưu, có mã phiên) mở đúng hội thoại đó; chưa hỏi gì thì mở hội thoại mới.
function moDanhSachHoiThoai() {
  chat.khungMo = false
  router.push(chat.state.maPhien ? { name: 'danh-sach-hoi-thoai', query: { phien: chat.state.maPhien } } : { name: 'hoi-thoai-moi' })
}
// Trang /demo-chat đã tạm bỏ:
// function expand() {
//   chat.khungMo = false
//   router.push('/demo-chat')
// }
</script>

<style scoped>
.chatbot__panel { height: min(680px, calc(100dvh - 110px)) !important; width: min(440px, calc(100vw - 24px)) !important; }
.chatbot__tieu-de { display: flex; flex-direction: column; min-width: 0; line-height: 1.25; }
.chatbot__tieu-de small { overflow: hidden; color: rgba(255, 255, 255, 0.85); font-size: 11px; text-overflow: ellipsis; white-space: nowrap; }
.chatbot__btn-icon.is-active { background: rgba(255, 255, 255, 0.2); }
.chatbot__header { position: relative; }
/* Khung cài đặt phủ lên phần đầu khung chat, ngay dưới tiêu đề. */
.chatbot__cai-dat {
  position: absolute;
  z-index: 10;
  top: calc(100% + 6px);
  right: 8px;
  left: 8px;
  max-height: min(420px, 60dvh);
  overflow-y: auto;
  padding: 12px 14px;
  border: 1px solid #d3e3d9;
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 10px 24px rgba(31, 122, 77, 0.18);
}
.chatbot__cai-dat-dau { display: flex; align-items: center; justify-content: space-between; color: #1c2b23; }
.chatbot__cai-dat-dong { display: inline-grid; place-items: center; width: 24px; height: 24px; padding: 0; border: 0; border-radius: 6px; background: transparent; color: #607169; cursor: pointer; }
.chatbot__cai-dat-dong:hover { background: #edf5f0; }
.chatbot__cai-dat-ghi-chu { margin: 6px 0 8px; color: #607169; font-size: 12px; }
.chatbot__cai-dat-ds { display: flex; flex-wrap: wrap; gap: 6px; }
.chatbot__cai-dat-ds button {
  padding: 5px 10px;
  border: 1px solid #c9ddd1;
  border-radius: 999px;
  background: #fff;
  color: #215b3d;
  font: inherit;
  font-size: 12px;
  text-align: left;
  cursor: pointer;
}
.chatbot__cai-dat-ds button:hover:not(:disabled) { border-color: #237b51; }
.chatbot__cai-dat-ds button.is-active { border-color: #237b51; background: #237b51; color: #fff; }
.chatbot__cai-dat-ds button:disabled { cursor: not-allowed; opacity: 0.55; }
.chatbot__cai-dat-ds button.is-active:disabled { opacity: 0.85; }
.chatbot__cai-dat-chan { display: flex; align-items: flex-end; gap: 10px; margin-top: 12px; padding-top: 10px; border-top: 1px solid #e2ece5; }
.chatbot__cai-dat-meo { display: flex; flex: 1; gap: 6px; min-width: 0; margin: 0; color: #755622; font-size: 12px; line-height: 1.45; }
.chatbot__cai-dat-meo .el-icon { flex-shrink: 0; margin-top: 2px; }
.chatbot__dang-nhap {
  flex-shrink: 0;
  padding: 6px 14px;
  border: 0;
  border-radius: 8px;
  background: #237b51;
  color: #fff;
  font: inherit;
  font-size: 13px;
  cursor: pointer;
}
.chatbot__dang-nhap:hover { background: #1c6542; }
.chatbot__cai-dat-ds button:focus-visible,
.chatbot__dang-nhap:focus-visible { outline: 2px solid #237b51; outline-offset: 2px; }
/* Mobile: khung chat phủ toàn màn hình (ẩn nút nổi, khóa cuộn trang nằm ở guest.scss). */
@media (max-width: 767px) {
  .chatbot__panel {
    position: fixed;
    /* Bề rộng theo left/right (vùng hiển thị thực), không dùng 100vw vì vw tính cả thanh cuộn nên rộng hơn màn hình.
       Chiều cao và mép trên theo visualViewport (biến đặt trong script) để tiêu đề luôn ở đầu khi bàn phím mở. */
    top: var(--khung-nhin-tren, 0);
    right: 0;
    bottom: auto;
    left: 0;
    width: auto !important;
    max-width: 100%;
    height: var(--khung-nhin-cao, 100dvh) !important;
    border: 0;
    border-radius: 0;
    box-shadow: none;
    padding-bottom: env(safe-area-inset-bottom);
  }

  /* Tiêu đề không bị co khi nội dung dài; chỉ vùng tin nhắn cuộn. */
  .chatbot__header {
    flex-shrink: 0;
    padding-top: max(10px, env(safe-area-inset-top));
  }

  /* iOS Safari tự phóng to trang khi chạm vào ô nhập có chữ nhỏ hơn 16px. */
  .chatbot__panel :deep(textarea),
  .chatbot__panel :deep(input),
  .chatbot__panel :deep(select) {
    font-size: 16px;
  }
}
</style>
