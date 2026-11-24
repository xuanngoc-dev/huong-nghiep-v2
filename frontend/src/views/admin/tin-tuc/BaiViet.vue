<template>
  <div class="catalog-page">
    <CustomCard shadow="never" class="catalog-card">
      <BoLoc>
        <CustomInput
          v-model="filters.q"
          class="filter-search"
          placeholder="Tìm theo tiêu đề, slug, tóm tắt, tác giả"
          clearable
          @keyup.enter="onSearch"
          @clear="onSearch"
        >
          <template #prefix>
            <CustomIcon><Search /></CustomIcon>
          </template>
        </CustomInput>
        <CustomSelect v-model="filters.nhom_tin_tuc_id" placeholder="Chọn nhóm tin" clearable filterable @change="onSearch">
          <CustomOption v-for="item in nhomOptions" :key="item.id" :label="item.ten_nhom" :value="item.id" />
        </CustomSelect>
        <CustomSelect v-model="filters.trang_thai" placeholder="Chọn trạng thái" clearable @change="onSearch">
          <CustomOption v-for="item in TRANG_THAI" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <CustomSelect v-model="filters.is_noi_bat" placeholder="Chọn bài nổi bật" clearable @change="onSearch">
          <CustomOption v-for="item in NOI_BAT" :key="item.value" :label="item.label" :value="item.value" />
        </CustomSelect>
        <template #nut>
          <CustomButton type="primary" @click="onSearch">Tìm kiếm</CustomButton>
        </template>
      </BoLoc>
    </CustomCard>

    <CustomCard shadow="never" class="catalog-card">
      <div class="toolbar">
        <h2 class="toolbar__title">Danh sách bài viết</h2>
        <div class="toolbar__actions">
          <CustomBadge :value="selectedRows.length" :hidden="!selectedRows.length" type="danger">
            <CustomButton
              type="danger"
              plain
              :disabled="!selectedRows.length"
              :loading="deleting"
              @click="onDeleteSelected"
            >
              <CustomIcon><Delete /></CustomIcon>
              Xóa
            </CustomButton>
          </CustomBadge>
          <CustomButton type="primary" @click="openCreate">
            <CustomIcon><Plus /></CustomIcon>
            Thêm bài viết
          </CustomButton>
        </div>
      </div>

      <CustomTable
        ref="tableRef"
        :loading="loading"
        :data="rows"
        row-key="id"
        stripe
        border
        @selection-change="onSelectionChange"
      >
        <CustomTableColumn type="selection" width="48" reserve-selection align="center" />
        <CustomTableColumn label="STT" width="72" align="center">
          <template #default="{ $index }">{{ rowIndex($index) }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Ảnh" width="100" align="center">
          <template #default="{ row }">
            <img v-if="row.anh_dai_dien" class="bai-viet__anh" :src="apiAssetUrl(row.anh_dai_dien)" alt="" loading="lazy" />
            <span v-else class="bai-viet__khong-anh">—</span>
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Tiêu đề" min-width="300">
          <template #default="{ row }">
            <div class="bai-viet__tieu-de">{{ row.tieu_de }}</div>
            <div class="bai-viet__slug">/{{ row.slug }}</div>
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="ten_nhom" label="Nhóm tin" min-width="160" />
        <CustomTableColumn label="Tác giả" min-width="140">
          <template #default="{ row }">{{ row.tac_gia || '—' }}</template>
        </CustomTableColumn>
        <!-- `?? 0`: el-table dựng sẵn template cột với row rỗng (hidden-columns), tránh cảnh báo của ElSwitch. -->
        <CustomTableColumn label="Xuất bản" width="110" align="center">
          <template #default="{ row }">
            <CustomSwitch
              :model-value="row.trang_thai ?? 0"
              :active-value="1"
              :inactive-value="0"
              :loading="dangDoi[`${row.id}-trang_thai`]"
              :before-change="() => doiHienThi(row, 'trang_thai')"
              :aria-label="`Xuất bản ${row.tieu_de}`"
            />
          </template>
        </CustomTableColumn>
        <CustomTableColumn label="Nổi bật" width="100" align="center">
          <template #default="{ row }">
            <CustomSwitch
              :model-value="row.is_noi_bat ?? 0"
              :active-value="1"
              :inactive-value="0"
              :loading="dangDoi[`${row.id}-is_noi_bat`]"
              :before-change="() => doiHienThi(row, 'is_noi_bat')"
              :aria-label="`Nổi bật ${row.tieu_de}`"
            />
          </template>
        </CustomTableColumn>
        <CustomTableColumn prop="luot_xem" label="Lượt xem" width="100" align="center" />
        <CustomTableColumn label="Ngày đăng" width="120" align="center">
          <template #default="{ row }">{{ dinhDangNgay(row.created_at, '—') }}</template>
        </CustomTableColumn>
        <CustomTableColumn label="Thao tác" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <div class="row-actions">
              <CustomTooltip content="Sửa" placement="top">
                <CustomButton link type="primary" aria-label="Sửa" @click="openEdit(row)">
                  <CustomIcon><Edit /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
              <CustomTooltip content="Xóa" placement="top">
                <CustomButton link type="danger" aria-label="Xóa" @click="onDelete(row, row.tieu_de)">
                  <CustomIcon><Delete /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </div>
          </template>
        </CustomTableColumn>
        <template #empty>
          <CustomEmpty description="Chưa có bài viết nào." />
        </template>
      </CustomTable>

      <div class="pager">
        <CustomPagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          layout="total, sizes, prev, pager, next"
          background
          @current-change="load"
          @size-change="onSearch"
        />
      </div>
    </CustomCard>
  </div>

  <CustomDialog
    v-model="dialogVisible"
    :title="editingId ? 'Cập nhật bài viết' : 'Thêm bài viết'"
    destroy-on-close
    @closed="resetForm"
  >
    <CustomForm
      ref="formRef"
      v-loading="dangTaiChiTiet"
      class="form-grid"
      :model="form"
      :rules="rules"
      label-position="top"
    >
      <div class="form-grid__body">
        <CustomFormItem class="form-grid__span-2" label="Tiêu đề" prop="tieu_de">
          <CustomInput v-model="form.tieu_de" maxlength="500" placeholder="Nhập tiêu đề" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__span-2" label="Slug" prop="slug">
          <CustomInput
            v-model="form.slug"
            maxlength="255"
            placeholder="Tự tạo từ tiêu đề"
            @update:model-value="suaSlugTay"
          >
            <template #append>
              <CustomTooltip content="Tạo lại slug từ tiêu đề" placement="top">
                <CustomButton aria-label="Tạo lại slug từ tiêu đề" :disabled="!form.tieu_de.trim()" @click="taoLaiSlug">
                  <CustomIcon><Refresh /></CustomIcon>
                </CustomButton>
              </CustomTooltip>
            </template>
          </CustomInput>
        </CustomFormItem>
        <CustomFormItem label="Nhóm tin" prop="nhom_tin_tuc_id">
          <CustomSelect v-model="form.nhom_tin_tuc_id" placeholder="Chọn nhóm tin" filterable>
            <CustomOption v-for="item in nhomOptions" :key="item.id" :label="item.ten_nhom" :value="item.id" />
          </CustomSelect>
        </CustomFormItem>
        <CustomFormItem label="Tác giả" prop="tac_gia">
          <CustomInput v-model="form.tac_gia" maxlength="255" placeholder="Nhập tác giả" />
        </CustomFormItem>
        <CustomFormItem label="Xuất bản" prop="trang_thai">
          <CustomSwitch
            v-model="form.trang_thai"
            :active-value="1"
            :inactive-value="0"
            active-text="Xuất bản"
            inactive-text="Nháp"
          />
        </CustomFormItem>
        <CustomFormItem label="Nổi bật" prop="is_noi_bat">
          <CustomSwitch v-model="form.is_noi_bat" :active-value="1" :inactive-value="0" active-text="Có" inactive-text="Không" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Ảnh đại diện" prop="anh_dai_dien">
          <ChonHinhAnh v-model="form.anh_dai_dien" thu-muc="tin-tuc" :alt="form.tieu_de || 'Ảnh đại diện bài viết'" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Tóm tắt" prop="tom_tat">
          <CustomInput v-model="form.tom_tat" type="textarea" :rows="3" maxlength="5000" placeholder="Nhập tóm tắt" />
        </CustomFormItem>
        <CustomFormItem class="form-grid__full" label="Nội dung" prop="noi_dung">
          <SoanThaoNoiDung v-model="form.noi_dung" thu-muc="tin-tuc" />
        </CustomFormItem>
      </div>
    </CustomForm>
    <template #footer>
      <CustomButton @click="dialogVisible = false">Hủy</CustomButton>
      <CustomButton type="primary" :loading="saving" :disabled="dangTaiChiTiet" @click="onSubmit">Lưu</CustomButton>
    </template>
  </CustomDialog>
</template>

<script setup>
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { apiAssetUrl } from '@/api/apiUrl'
import { baiVietApi, nhomTinApi } from '@/api/tinTuc'
import { errorMessage, giaTriTuyChon, loadAll, useBangDuHoc } from '@/composables/useThptDuHoc'
import SoanThaoNoiDung from '@/components/admin/soan-thao/SoanThaoNoiDung.vue'
import { taoSlug } from '@/utils/slug'
import { dinhDangNgay } from '@/utils/thoiGian'

defineOptions({ name: 'BaiViet' })

const TRANG_THAI = [
  { value: 1, label: 'Xuất bản' },
  { value: 0, label: 'Nháp' },
]
const NOI_BAT = [
  { value: 1, label: 'Nổi bật' },
  { value: 0, label: 'Không nổi bật' },
]

const filters = reactive({ q: '', nhom_tin_tuc_id: '', trang_thai: '', is_noi_bat: '' })
const nhomOptions = ref([])

const {
  loading,
  deleting,
  rows,
  selectedRows,
  tableRef,
  total,
  page,
  pageSize,
  load,
  onSelectionChange,
  rowIndex,
  onSearch,
  onDelete,
  onDeleteSelected,
} = useBangDuHoc({
  api: baiVietApi,
  nhan: 'bài viết',
  params: () => {
    const params = {}
    if (filters.q.trim()) params.q = filters.q.trim()
    if (filters.nhom_tin_tuc_id) params.nhom_tin_tuc_id = filters.nhom_tin_tuc_id
    if (filters.trang_thai === 0 || filters.trang_thai === 1) params.trang_thai = filters.trang_thai
    if (filters.is_noi_bat === 0 || filters.is_noi_bat === 1) params.is_noi_bat = filters.is_noi_bat
    return params
  },
})

const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const dangTaiChiTiet = ref(false)
// Slug tự theo tiêu đề cho tới khi người dùng tự sửa ô slug (xóa trắng thì tự theo lại).
// Sửa bài đã có: giữ slug cũ để không đổi đường dẫn bài, muốn đổi thì bấm "Tạo lại slug từ tiêu đề".
const slugTuDong = ref(true)
const formRef = ref()
const form = reactive(emptyForm())
// Khóa "id-trường" đang gọi API đổi xuất bản / nổi bật (hiện vòng quay trên công tắc).
const dangDoi = ref({})

const rules = {
  tieu_de: [{ required: true, message: 'Vui lòng nhập tiêu đề', trigger: 'blur' }],
  nhom_tin_tuc_id: [{ required: true, message: 'Vui lòng chọn nhóm tin', trigger: 'change' }],
}

function emptyForm() {
  return {
    nhom_tin_tuc_id: null,
    tieu_de: '',
    slug: '',
    tom_tat: '',
    noi_dung: '',
    anh_dai_dien: '',
    tac_gia: '',
    trang_thai: 1,
    is_noi_bat: 0,
  }
}

function resetForm() {
  Object.assign(form, emptyForm())
  editingId.value = null
  slugTuDong.value = true
  formRef.value?.clearValidate()
}

async function loadOptions() {
  try {
    nhomOptions.value = await loadAll(nhomTinApi.fetch)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được danh sách nhóm tin'))
  }
}

function openCreate() {
  resetForm()
  // Đang lọc theo một nhóm thì chọn sẵn nhóm đó.
  form.nhom_tin_tuc_id = filters.nhom_tin_tuc_id || null
  dialogVisible.value = true
}

// Danh sách không kèm nội dung: mở form sửa thì tải chi tiết bài viết.
async function openEdit(row) {
  resetForm()
  editingId.value = row.id
  slugTuDong.value = false
  dialogVisible.value = true
  dangTaiChiTiet.value = true
  try {
    const data = await baiVietApi.get(row.id)
    const values = emptyForm()
    for (const key of Object.keys(values)) {
      if (data[key] != null) values[key] = data[key]
    }
    Object.assign(form, values)
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không tải được bài viết'))
    dialogVisible.value = false
  } finally {
    dangTaiChiTiet.value = false
  }
}

watch(
  () => form.tieu_de,
  (tieuDe) => {
    if (slugTuDong.value) form.slug = taoSlug(tieuDe)
  },
)

function suaSlugTay(value) {
  slugTuDong.value = !String(value || '').trim()
  if (slugTuDong.value) form.slug = taoSlug(form.tieu_de)
}

function taoLaiSlug() {
  form.slug = taoSlug(form.tieu_de)
  slugTuDong.value = !editingId.value
}

async function doiHienThi(row, truong) {
  const khoa = `${row.id}-${truong}`
  const moi = row[truong] === 1 ? 0 : 1
  dangDoi.value = { ...dangDoi.value, [khoa]: true }
  try {
    const data = await baiVietApi.hienThi(row.id, { [truong]: moi })
    row[truong] = data[truong]
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không cập nhật được bài viết'))
  } finally {
    const conLai = { ...dangDoi.value }
    delete conLai[khoa]
    dangDoi.value = conLai
  }
  // Giá trị đã cập nhật theo API ở trên, không để công tắc tự đảo.
  return false
}

async function onSubmit() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const payload = {
      nhom_tin_tuc_id: form.nhom_tin_tuc_id,
      tieu_de: form.tieu_de.trim(),
      slug: giaTriTuyChon(form.slug),
      tom_tat: giaTriTuyChon(form.tom_tat),
      noi_dung: giaTriTuyChon(form.noi_dung),
      anh_dai_dien: giaTriTuyChon(form.anh_dai_dien),
      tac_gia: giaTriTuyChon(form.tac_gia),
      trang_thai: form.trang_thai,
      is_noi_bat: form.is_noi_bat,
    }
    if (editingId.value) {
      await baiVietApi.update(editingId.value, payload)
      ElMessage.success('Đã cập nhật bài viết')
    } else {
      await baiVietApi.create(payload)
      ElMessage.success('Đã thêm bài viết')
    }
    dialogVisible.value = false
    await load()
  } catch (error) {
    ElMessage.error(errorMessage(error, 'Không lưu được bài viết'))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadOptions()
  load()
})
</script>

<style scoped>
.bai-viet__anh {
  width: 72px;
  height: 45px;
  border-radius: 4px;
  object-fit: cover;
  vertical-align: middle;
}

.bai-viet__khong-anh {
  color: var(--el-text-color-placeholder);
}

.bai-viet__tieu-de {
  font-weight: 500;
  line-height: 1.4;
}

.bai-viet__slug {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  overflow-wrap: anywhere;
}
</style>
