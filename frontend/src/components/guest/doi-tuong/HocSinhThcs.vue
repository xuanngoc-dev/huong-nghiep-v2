<template>
  <section class="thcs py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <div class="intro-card mb-3">
            <h1 class="thcs__title">Học sinh THCS: chọn hướng đi sau lớp 9</h1>
            <p class="thcs__lead mb-0">
              Hết lớp 9 bạn có nhiều con đường: học THPT, học nghề hay vừa học vừa làm. Hãy xem từng hướng đi, ưu nhược
              điểm và chi phí, hoặc trả lời vài câu hỏi ngắn để biết hướng nào hợp với bạn nhất.
            </p>
          </div>

          <RouterLink class="goi-y-card mb-3" :to="{ name: 'hs-thcs-tu-danh-gia' }">
            <span class="goi-y-card__icon" aria-hidden="true">
              <el-icon><Compass /></el-icon>
            </span>
            <span class="goi-y-card__body">
              <span class="goi-y-card__ten">Chưa biết chọn hướng nào?</span>
              <span class="goi-y-card__mo-ta">
                Tự đánh giá học lực, sở thích, hoàn cảnh gia đình để nhận gợi ý hướng đi phù hợp.
              </span>
            </span>
            <span class="goi-y-card__nut">Tìm hướng đi phù hợp →</span>
          </RouterLink>

          <div class="directions-card">
            <h2 class="directions-heading">Là học sinh THCS, bạn định hướng gì sau khi học xong lớp 9</h2>

            <div v-if="dangTai" class="thcs__trang-thai" role="status">Đang tải các hướng đi…</div>
            <div v-else-if="loi" class="thcs__trang-thai">
              {{ loi }}
              <button type="button" class="thcs__thu-lai" @click="taiHuongDi">Thử lại</button>
            </div>
            <div v-else-if="!dsHuong.length" class="thcs__trang-thai">Chưa có dữ liệu hướng đi sau THCS.</div>

            <div v-else class="row g-3">
              <div v-for="huong in dsHuong" :key="huong.id" class="col-12 col-sm-6 col-xl-4">
                <RouterLink
                  class="huong-card h-100"
                  :to="{ name: 'hs-thcs-huong-di', params: { maHuong: huong.ma_huong } }"
                >
                  <span class="huong-card__ten">{{ huong.ten_huong }}</span>
                  <span class="huong-card__mo-ta">{{ huong.mo_ta_tong_quan }}</span>
                  <ul v-if="uuNhuocCua(huong.id).length" class="uu-nhuoc">
                    <li
                      v-for="item in uuNhuocCua(huong.id)"
                      :key="item.id"
                      class="uu-nhuoc__muc"
                      :class="`uu-nhuoc__muc--${item.loai}`"
                    >
                      <span class="uu-nhuoc__dau" aria-hidden="true">{{ item.loai === 'uu_diem' ? '+' : '−' }}</span>
                      <span class="visually-hidden">{{ item.loai === 'uu_diem' ? 'Ưu điểm:' : 'Nhược điểm:' }}</span>
                      {{ item.tieu_de }}
                    </li>
                  </ul>
                  <span v-if="chiPhi(huong)" class="huong-card__chi-phi">{{ chiPhi(huong) }}</span>
                  <span class="huong-card__xem">Xem chi tiết →</span>
                </RouterLink>
              </div>
            </div>
          </div>

          <div class="d-flex flex-column gap-3 mt-3">
            <HoTroDinhHuong />
            <CauHoiThuongGap />
          </div>
        </div>

        <div class="col-lg-3">
          <div class="audiences-card">
            <h2 id="chon-lai-doi-tuong" class="h4 mb-3">Chọn lại đối tượng</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-lai-doi-tuong">
              <button
                v-for="item in audiences"
                :key="item.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': selectedCode === item.code, 'is-locked': !item.moTruyCap }"
                :disabled="!item.moTruyCap"
                @click="chonDoiTuong(item)"
              >
                <img class="switch-card__image" :src="item.image" :alt="item.name" />
                <span class="switch-card__body">
                  <span class="switch-card__name">
                    {{ item.name }}
                    <span v-if="!item.moTruyCap" class="sap-ra-mat sap-ra-mat--inline">Sắp ra mắt</span>
                  </span>
                  <span class="switch-card__text">{{ item.description }}</span>
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { Compass } from '@element-plus/icons-vue'
import { useDoiTuongAudiences } from '@/composables/useDoiTuongAudiences'
import { uuNhuocDiemApi } from '@/api/thcsHuongDi'
import { loadAll } from '@/composables/useThcsHuongDi'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { chiPhi, useDsHuongDiThcs } from './HocSinhThcs/thcs'

defineOptions({ name: 'HocSinhThcs' })

defineProps({
  audience: { type: Object, required: true },
})

const { audiences, selectedCode, chonDoiTuong } = useDoiTuongAudiences()
const { dsHuong, dangTai, loi, taiHuongDi } = useDsHuongDiThcs()

// Số ưu điểm, nhược điểm tối đa hiện trên mỗi thẻ; xem đủ ở trang chi tiết.
const SO_MUC_MOI_LOAI = 2
// { huongDiId: [ưu điểm..., nhược điểm...] }, API đã xếp ưu điểm trước và theo thứ tự hiển thị.
const uuNhuocTheoHuong = ref({})

function uuNhuocCua(huongId) {
  return uuNhuocTheoHuong.value[huongId] || []
}

// Lỗi tải ưu/nhược điểm không chặn trang: thẻ chỉ ẩn phần này.
async function taiUuNhuoc() {
  try {
    const theoHuong = {}
    for (const item of await loadAll(uuNhuocDiemApi.fetch)) {
      const ds = (theoHuong[item.thcs_huong_di_id] ??= [])
      if (ds.filter((x) => x.loai === item.loai).length < SO_MUC_MOI_LOAI) ds.push(item)
    }
    uuNhuocTheoHuong.value = theoHuong
  } catch {
    uuNhuocTheoHuong.value = {}
  }
}

onMounted(() => {
  taiHuongDi()
  taiUuNhuoc()
})
</script>

<style scoped>
.thcs__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
}

.thcs__lead {
  color: #3a4742;
  line-height: 1.6;
}

.thcs__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.thcs__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.goi-y-card {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  padding: 16px 20px;
  border: 1px solid rgba(var(--guest-primary-rgb), 0.3);
  border-radius: var(--guest-radius);
  background: linear-gradient(120deg, rgba(var(--guest-primary-rgb), 0.1), #fff 70%);
  color: inherit;
  text-decoration: none;
  transition: box-shadow 0.3s ease;
}

.goi-y-card:hover {
  box-shadow: 0 12px 24px rgba(31, 122, 77, 0.12);
}

.goi-y-card__icon {
  display: inline-flex;
  flex: 0 0 44px;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--guest-primary);
  color: #fff;
  font-size: 1.4rem;
}

.goi-y-card__body {
  display: flex;
  flex: 1 1 240px;
  flex-direction: column;
  gap: 2px;
}

.goi-y-card__ten {
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 700;
}

.goi-y-card__mo-ta {
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
}

.goi-y-card__nut {
  border-radius: 999px;
  padding: 8px 16px;
  background: var(--guest-primary);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
}

.huong-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  width: 100%;
  padding: 14px;
  border: 1px solid #d7eadf;
  border-top: 4px solid var(--guest-primary);
  border-radius: var(--guest-radius);
  background: #fff;
  color: inherit;
  text-decoration: none;
  transition: box-shadow 0.3s ease;
}

.huong-card:hover {
  box-shadow: 0 12px 24px rgba(31, 122, 77, 0.12);
}

.huong-card__ten {
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 700;
  line-height: 1.35;
}

.huong-card__mo-ta {
  display: -webkit-box;
  overflow: hidden;
  color: #3a4742;
  font-size: 0.9rem;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.uu-nhuoc {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 2px 0 0;
  padding: 0;
  list-style: none;
}

.uu-nhuoc__muc {
  --mau: var(--guest-primary);
  display: flex;
  align-items: flex-start;
  gap: 6px;
  color: #1c2b23;
  font-size: 0.85rem;
  line-height: 1.4;
}

.uu-nhuoc__muc--nhuoc_diem {
  --mau: #c2410c;
}

.uu-nhuoc__dau {
  display: inline-flex;
  flex: 0 0 18px;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  margin-top: 1px;
  border-radius: 50%;
  background: var(--mau);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  line-height: 1;
}

.huong-card__chi-phi {
  color: #6b7780;
  font-size: 0.82rem;
}

.huong-card__xem {
  margin-top: auto;
  color: var(--guest-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.goi-y-card:focus-visible,
.huong-card:focus-visible,
.thcs__thu-lai:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .thcs__title {
    font-size: 1.4rem;
  }

  .thcs__lead {
    font-size: 0.9rem;
  }

  .goi-y-card__nut {
    width: 100%;
    text-align: center;
  }
}
</style>
