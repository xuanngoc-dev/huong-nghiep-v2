<template>
  <section id="holland" class="landing__section" aria-labelledby="holland-title">
    <div class="container-fluid">
      <div class="landing-holland" data-reveal>
        <div class="row g-lp align-items-center">
          <div class="col-xl-5">
            <p class="landing__eyebrow">Trắc nghiệm Holland RIASEC</p>
            <h2 id="holland-title" class="landing__title">Khám phá nhóm tính cách nghề nghiệp của bạn</h2>
            <p class="landing__lead">
              Mô hình Holland giúp nhận diện khuynh hướng nghề nghiệp qua sáu nhóm tính cách, từ đó
              gợi ý ngành học và môi trường làm việc phù hợp.
            </p>
            <div class="landing-holland__letters" aria-hidden="true">
              <span v-for="item in hollandGroups" :key="item.code" :style="{ '--c': item.color }">
                {{ item.code }}
              </span>
            </div>
            <RouterLink class="landing__btn landing__btn--light" :to="{ name: 'thpt-thi-dai-hoc-chua-co' }">
              Khám phá nhóm tính cách của bạn
              <el-icon aria-hidden="true"><Right /></el-icon>
            </RouterLink>
          </div>

          <div class="col-xl-7">
            <div class="row g-lp row-cols-2 row-cols-md-3" data-stagger>
              <div v-for="item in hollandGroups" :key="item.code" class="col">
                <article class="landing-holland__card h-100" :style="{ '--c': item.color }">
                  <div class="landing-holland__media">
                    <img :src="item.image" :alt="`Minh họa nhóm ${item.name}`" loading="lazy" decoding="async" />
                    <span class="landing-holland__code">{{ item.code }}</span>
                  </div>
                  <h3>{{ item.name }} <small>{{ item.en }}</small></h3>
                  <p>{{ item.text }}</p>
                </article>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { hollandGroups } from '@/data/landing'
</script>
