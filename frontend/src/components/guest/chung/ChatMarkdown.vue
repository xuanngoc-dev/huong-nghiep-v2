<script>
import { defineComponent, h } from 'vue'
import { renderMarkdown } from '@/utils/chatMarkdown'

export default defineComponent({
  name: 'ChatMarkdown',
  props: { text: { type: String, default: '' } },
  setup: props => () => h('div', { class: 'ai-chat__markdown' }, renderMarkdown(props.text)),
})
</script>
