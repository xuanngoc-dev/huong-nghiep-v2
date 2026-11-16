<template>
  <section class="so-du-tong-quan" aria-label="Số dư tài khoản">
    <article v-for="item in THE" :key="item.truong" class="so-du-the" :class="`so-du-the--${item.loai}`">
      <span class="so-du-the__icon" aria-hidden="true">
        <CustomIcon><component :is="item.icon" /></CustomIcon>
      </span>
      <div class="so-du-the__than">
        <span class="so-du-the__nhan">{{ item.nhan }}</span>
        <strong class="so-du-the__so">{{ soDu ? hienSo(soDu[item.truong]) : '—' }}</strong>
        <span v-if="item.truong === 'luot_tra_cuu' && luotMienPhi" class="so-du-the__phu">
          Miễn phí hôm nay: {{ luotMienPhi.con_lai ?? 0 }}/{{ luotMienPhi.so_luot_ngay }}
        </span>
        <span v-else class="so-du-the__phu">{{ item.donVi }}</span>
      </div>
      <CustomTooltip :content="`Nạp thêm ${item.nhan.toLowerCase()}`" placement="top">
        <CustomButton
          link
          type="primary"
          class="so-du-the__nap"
          :aria-label="`Nạp thêm ${item.nhan.toLowerCase()}`"
          @click="router.push({ name: 'nap-tien', query: { loai: item.loai } })"
        >
          <CustomIcon><Plus /></CustomIcon>
        </CustomButton>
      </CustomTooltip>
    </article>
  </section>
</template>

<script setup>
/**
 * Hàng thẻ số dư trên trang tổng quan thành viên: Edu coin, lượt tra cứu (kèm lượt miễn phí hôm nay), hỏi đáp,
 * khảo sát. Nút "+" mở trang nạp tiền đúng tab.
 */
import { useRouter } from 'vue-router'
import { ChatDotRound, Coin, EditPen, Plus, Search } from '@element-plus/icons-vue'
import { hienSo } from '@/data/napTien'

defineProps({
  // Hồ sơ (GET /tai-khoan/ho-so) chứa các cột số dư.
  soDu: { type: Object, default: null },
  // Lượt tìm trường miễn phí hôm nay (GET /tim-truong-phu-hop/luot).
  luotMienPhi: { type: Object, default: null },
})

// loai khớp ?loai= của trang nạp tiền.
const THE = [
  { truong: 'edu_coin', loai: 'edu_coin', nhan: 'Edu coin', donVi: 'Edu coin', icon: Coin },
  { truong: 'luot_tra_cuu', loai: 'tra_cuu', nhan: 'Lượt tra cứu', donVi: 'lượt', icon: Search },
  { truong: 'luot_hoi_dap', loai: 'hoi_dap', nhan: 'Lượt hỏi đáp', donVi: 'lượt', icon: ChatDotRound },
  { truong: 'luot_khao_sat', loai: 'khao_sat', nhan: 'Lượt khảo sát', donVi: 'lượt', icon: EditPen },
]

const router = useRouter()
</script>

<style scoped>
.so-du-tong-quan {
  container-type: inline-size;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.so-du-the {
  --the-mau: #0c5c34;
  --the-nen: #eef6f1;
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 12px;
  background: var(--el-bg-color);
}

.so-du-the--edu_coin {
  --the-mau: #a15c07;
  --the-nen: #fff4e0;
}

.so-du-the--hoi_dap {
  --the-mau: #1f5fa8;
  --the-nen: #eaf2fc;
}

.so-du-the--khao_sat {
  --the-mau: #7a3fb0;
  --the-nen: #f4ecfb;
}

.so-du-the__icon {
  display: grid;
  flex-shrink: 0;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--the-nen);
  color: var(--the-mau);
  font-size: 20px;
}

.so-du-the__than {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.so-du-the__nhan,
.so-du-the__phu {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.4;
}

.so-du-the__phu {
  font-size: 12px;
}

.so-du-the__so {
  color: var(--el-text-color-primary);
  font-size: 24px;
  line-height: 1.3;
}

.so-du-the__nap {
  position: absolute;
  top: 8px;
  right: 8px;
}

@container (max-width: 860px) {
  .so-du-tong-quan {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@container (max-width: 420px) {
  .so-du-the {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    padding: 12px;
  }
}
</style>
