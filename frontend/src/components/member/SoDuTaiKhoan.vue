<template>
  <CustomDropdown
    :trigger="moBangCham ? 'click' : 'hover'"
    placement="bottom-end"
    popper-class="so-du-menu"
    @visible-change="onVisibleChange"
    @command="onCommand"
  >
    <button type="button" class="so-du-chip" :aria-label="`Số dư: ${hienSo(soDu?.edu_coin)} Edu coin`">
      <CustomIcon class="so-du-chip__icon"><Coin /></CustomIcon>
      <strong>{{ soDu ? hienSo(soDu.edu_coin) : '—' }}</strong>
      <span class="so-du-chip__don-vi">Edu coin</span>
    </button>
    <template #dropdown>
      <el-dropdown-menu>
        <li class="so-du-menu__dau" aria-hidden="true">Số dư tài khoản</li>
        <li v-if="loi" class="so-du-menu__loi">{{ loi }}</li>
        <li v-for="item in SO_DU" :key="item.truong" class="so-du-menu__dong">
          <span class="so-du-menu__nhan">
            <CustomIcon><component :is="item.icon" /></CustomIcon>
            {{ item.nhan }}
          </span>
          <!-- Cùng hàng: lượt miễn phí còn lại hôm nay (nhỏ) rồi số dư thực (lớn). -->
          <span class="so-du-menu__gia-tri">
            <small
              v-if="mienPhi[item.truong]"
              class="so-du-menu__mien-phi"
              :title="`Còn ${mienPhi[item.truong].conLai}/${mienPhi[item.truong].tong} lượt miễn phí hôm nay`"
            >
              Miễn phí {{ mienPhi[item.truong].conLai }}/{{ mienPhi[item.truong].tong }}
            </small>
            <strong class="so-du-menu__so-du">{{ soDu ? hienSo(soDu[item.truong]) : '—' }}</strong>
          </span>
        </li>
        <el-dropdown-item divided command="nap-tien" :icon="Wallet">Nạp tiền</el-dropdown-item>
        <el-dropdown-item command="lich-su-nap-tien" :icon="Tickets">Lịch sử nạp tiền</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </CustomDropdown>
</template>

<script setup>
/**
 * Chip số dư Edu coin trên header cho thành viên; rê chuột (desktop) hoặc chạm (mobile) để xem các số dư lượt.
 * Tải số dư khi gắn và mỗi lần mở menu (số dư có thể vừa được cộng qua nạp tiền).
 */
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChatDotRound, Coin, EditPen, Search, Tickets, Wallet } from '@element-plus/icons-vue'
import { fetchHoSo } from '@/api/hoSo'
import { fetchLuotTimTruong } from '@/api/timTruongPhuHop'
import { useIsMobile } from '@/composables/useResponsiveSize'
import { hienSo } from '@/data/napTien'

// truong: cột số dư trong hồ sơ (GET /tai-khoan/ho-so).
const SO_DU = [
  { truong: 'edu_coin', nhan: 'Edu coin', icon: Coin },
  { truong: 'luot_tra_cuu', nhan: 'Lượt tra cứu', icon: Search },
  { truong: 'luot_hoi_dap', nhan: 'Lượt hỏi đáp', icon: ChatDotRound },
  { truong: 'luot_khao_sat', nhan: 'Lượt khảo sát', icon: EditPen },
]

const router = useRouter()
const moBangCham = useIsMobile('(max-width: 991.98px), (hover: none)')
const soDu = ref(null)
const luotMienPhi = ref(null)
const loi = ref('')
let dangTai = false

// Lượt miễn phí theo cột số dư; hiện chỉ tra cứu có hạn mức miễn phí theo ngày (GET /tim-truong-phu-hop/luot).
const mienPhi = computed(() => {
  const ketQua = {}
  if (luotMienPhi.value) {
    ketQua.luot_tra_cuu = { conLai: luotMienPhi.value.con_lai ?? 0, tong: luotMienPhi.value.so_luot_ngay ?? 0 }
  }
  return ketQua
})

async function taiSoDu() {
  if (dangTai) return
  dangTai = true
  try {
    const [hoSo, mienPhi] = await Promise.allSettled([fetchHoSo({ skipLoading: true }), fetchLuotTimTruong()])
    if (hoSo.status === 'fulfilled') {
      soDu.value = hoSo.value
      loi.value = ''
    } else {
      loi.value = 'Không tải được số dư.'
    }
    luotMienPhi.value = mienPhi.status === 'fulfilled' ? mienPhi.value : null
  } finally {
    dangTai = false
  }
}

function onVisibleChange(open) {
  if (open) taiSoDu()
}

function onCommand(command) {
  router.push({ name: command })
}

onMounted(taiSoDu)
</script>

<style scoped>
.so-du-chip {
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  gap: 6px;
  min-height: 36px;
  padding: 4px 12px;
  border: 1px solid var(--el-color-warning-light-5);
  border-radius: 999px;
  background: var(--el-color-warning-light-9);
  color: var(--el-text-color-primary);
  font-size: 14px;
  line-height: 1;
  white-space: nowrap;
  cursor: pointer;
}

.so-du-chip:hover,
.so-du-chip:focus-visible {
  border-color: var(--el-color-warning);
}

.so-du-chip__icon {
  color: var(--el-color-warning-dark-2);
  font-size: 16px;
}

.so-du-chip__don-vi {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

@media (max-width: 575.98px) {
  .so-du-chip__don-vi {
    display: none;
  }
}
</style>

<!-- Menu teleport ra body nên không dùng scoped. -->
<style>
.so-du-menu .el-dropdown-menu {
  min-width: 280px;
}

.so-du-menu__dau {
  padding: 6px 16px 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
  list-style: none;
}

.so-du-menu__loi {
  padding: 0 16px 6px;
  color: var(--el-color-danger);
  font-size: 12px;
  list-style: none;
}

.so-du-menu__dong {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 6px 16px;
  font-size: 14px;
  list-style: none;
}

.so-du-menu__nhan {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-regular);
}

.so-du-menu__gia-tri {
  display: inline-flex;
  align-items: baseline;
  gap: 8px;
  white-space: nowrap;
}

.so-du-menu__mien-phi {
  padding: 1px 6px;
  border-radius: 999px;
  background: var(--el-color-success-light-9);
  color: var(--el-color-success-dark-2);
  font-size: 11px;
}

.so-du-menu__so-du {
  color: var(--el-text-color-primary);
  font-size: 16px;
}
</style>
