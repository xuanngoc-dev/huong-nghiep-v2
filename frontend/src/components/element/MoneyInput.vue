<script setup>
import CustomInput from './CustomInput.vue'

defineOptions({ name: 'MoneyInput', inheritAttrs: false })

const model = defineModel({ type: [Number, null], default: null })
</script>

<template>
  <CustomInput v-model="model" type="number" v-bind="$attrs" />
</template>
