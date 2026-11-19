<script>
import { defineComponent, h } from 'vue'
import { renderMarkdown } from '@/utils/chatMarkdown'

export default defineComponent({
  name: 'ChatMarkdown',
  props: { text: { type: String, default: '' } },
  setup: props => () => h('div', { class: 'ai-chat__markdown' }, renderMarkdown(props.text)),
})
</script>

<style>
/*
 * Code trong câu trả lời AI: nền pha từ màu chữ hiện tại nên đọc được trên mọi nền bong bóng
 * (bong bóng xanh chữ trắng ở trang quản trị, bong bóng trắng chữ tối, giao diện tối);
 * style `code` chung (index.scss) có nền sáng cố định → chữ trắng trên nền trắng.
 */
.ai-chat__markdown code {
  padding: 1px 5px;
  border-radius: 4px;
  background: color-mix(in srgb, currentColor 14%, transparent);
  color: inherit;
  font-family: ui-monospace, Consolas, monospace;
  font-size: 0.9em;
}

.ai-chat__markdown pre {
  max-width: 100%;
  margin: 8px 0;
  padding: 10px 12px;
  overflow-x: auto;
  border-radius: 8px;
  background: color-mix(in srgb, currentColor 10%, transparent);
  color: inherit;
}

.ai-chat__markdown pre code {
  padding: 0;
  background: none;
  white-space: pre;
}
</style>
