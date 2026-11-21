<template>
  <section class="xkld py-4">
    <div class="container-fluid">
      <div class="row g-4">
        <div class="col-lg-9">
          <article class="intro-card mb-3">
            <h1 class="xkld__title">Xuất khẩu lao động</h1>
            <p class="xkld__lead">
              Đi làm việc có thời hạn ở nước ngoài giúp bạn có thu nhập, tay nghề và ngoại ngữ ngay sau THPT. Hãy chọn
              nhóm nghề phù hợp với sức khỏe và sở thích, xem chi tiết thị trường, chi phí, thủ tục và chỉ đi qua kênh chính
              thống để tránh rủi ro.
            </p>

            <div v-if="dangTaiNhom" class="xkld__trang-thai" role="status">Đang tải các nhóm nghề…</div>
            <div v-else-if="loiNhom" class="xkld__trang-thai">
              {{ loiNhom }}
              <button type="button" class="xkld__thu-lai" @click="taiNhomNghe">Thử lại</button>
            </div>
            <div v-else-if="!dsNhom.length" class="xkld__trang-thai">Chưa có dữ liệu nhóm nghề xuất khẩu lao động.</div>

            <div v-else class="row g-3">
              <div v-for="nhom in dsNhom" :key="nhom.id" class="col-12 col-sm-6 col-xl-4">
                <RouterLink
                  class="huong-card h-100"
                  :to="{ name: tenRoute('thpt-xuat-khau-lao-dong-nhom-nghe'), params: { maNhom: nhom.ma_nhom } }"
                >
                  <span v-if="thuNhap(nhom)" class="huong-card__loai">{{ thuNhap(nhom) }}</span>
                  <span class="huong-card__ten">{{ nhom.ten_nhom }}</span>
                  <span class="huong-card__mo-ta">{{ nhom.mo_ta_cong_viec }}</span>
                  <span class="huong-card__xem">Xem chi tiết →</span>
                </RouterLink>
              </div>
            </div>
          </article>

          <div class="d-flex flex-column gap-3 mt-3">
            <HoTroDinhHuong />
            <CauHoiThuongGap />
          </div>
        </div>

        <div class="col-lg-3">
          <div class="paths-card">
            <h2 id="chon-huong-di" class="h4 mb-3">Một số hướng đi khác cho bạn.</h2>
            <div class="d-flex flex-column gap-3" aria-labelledby="chon-huong-di">
              <button
                v-for="item in dinhHuongThptList"
                :key="item.code"
                type="button"
                class="switch-card"
                :class="{ 'is-selected': currentDirection === item.code, 'is-locked': !item.moTruyCap }"
                :disabled="!item.moTruyCap"
                @click="chonHuong(item)"
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
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import HoTroDinhHuong from '@/components/guest/chung/HoTroDinhHuong.vue'
import CauHoiThuongGap from '@/components/guest/chung/CauHoiThuongGap.vue'
import { nhomNgheApi } from '@/api/thptXkld'
import { thuNhap } from './xuat-khau-lao-dong/xkld'
import { DINH_HUONG_THPT_KEY, dinhHuongThptList } from './dinhHuong'
import { routeNameDinhHuongThpt } from './routes'
import { useTenRouteThpt } from './useTenRouteThpt'

defineOptions({ name: 'ThptXuatKhauLaoDong' })

const { tienTo, tenRoute } = useTenRouteThpt()
const route = useRoute()
const router = useRouter()
const currentDirection = computed(() => route.meta.dinhHuong || '')

const dsNhom = ref([])
const dangTaiNhom = ref(false)
const loiNhom = ref('')

async function taiNhomNghe() {
  dangTaiNhom.value = true
  loiNhom.value = ''
  try {
    const data = await nhomNgheApi.fetch({ trang_thai: 1, page: 1, page_size: 100 })
    dsNhom.value = data.items || []
  } catch {
    loiNhom.value = 'Không tải được danh sách nhóm nghề.'
  } finally {
    dangTaiNhom.value = false
  }
}

function chonHuong(direction) {
  if (!direction.moTruyCap) return
  sessionStorage.setItem(DINH_HUONG_THPT_KEY, direction.code)
  const name = routeNameDinhHuongThpt(direction.code, tienTo.value)
  if (name && name !== route.name) router.push({ name })
}

onMounted(taiNhomNghe)
</script>

<style scoped>
.xkld__title {
  margin: 0 0 8px;
  font-size: 1.75rem;
  font-weight: 600;
  line-height: 1.35;
}

.xkld__lead {
  margin: 0 0 16px;
  color: #3a4742;
  line-height: 1.6;
}

.xkld__trang-thai {
  padding: 24px 12px;
  color: #5b6770;
  text-align: center;
}

.xkld__thu-lai {
  margin-left: 8px;
  border: 0;
  background: none;
  color: var(--guest-primary);
  font-weight: 500;
  text-decoration: underline;
  cursor: pointer;
}

.huong-card {
  --mau-loai: var(--guest-primary);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
  width: 100%;
  padding: 14px;
  border: 1px solid #d7eadf;
  border-top: 4px solid var(--mau-loai);
  border-radius: var(--guest-radius);
  background: #fff;
  color: inherit;
  text-align: left;
  text-decoration: none;
  cursor: pointer;
  transition:
    box-shadow 0.3s ease,
    background-color 0.2s ease;
}

.huong-card:hover {
  box-shadow: 0 12px 24px rgba(31, 122, 77, 0.12);
}

.huong-card__loai {
  border-radius: 999px;
  padding: 3px 10px;
  background: var(--mau-loai);
  color: #fff;
  font-size: 0.78rem;
  line-height: 1.3;
}

.huong-card__ten {
  color: #1c2b23;
  font-size: 1.05rem;
  font-weight: 600;
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

.huong-card__xem {
  margin-top: auto;
  color: var(--guest-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.huong-card:focus-visible,
.xkld__thu-lai:focus-visible {
  outline: 2px solid var(--guest-primary);
  outline-offset: 2px;
}

@media (max-width: 575.98px) {
  .xkld__title {
    font-size: 1.4rem;
  }

  .xkld__lead {
    font-size: 0.9rem;
  }
}
</style>
