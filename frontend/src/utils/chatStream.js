/** Parse complete SSE frames, including fragmented UTF-8 and CRLF boundaries. */
export function createEventParser(onEvent) {
  let buffer = ''
  return {
    push(text, final = false) {
      buffer += text
      if (buffer.length > 1_000_000) throw new Error('Phản hồi quá lớn.')
      let match
      while ((match = /\r?\n\r?\n/.exec(buffer))) {
        const frame = buffer.slice(0, match.index)
        buffer = buffer.slice(match.index + match[0].length)
        let event = 'message'
        const data = []
        for (const line of frame.split(/\r?\n/)) {
          if (line.startsWith('event:')) event = line.slice(6).trim()
          if (line.startsWith('data:')) data.push(line.slice(5).replace(/^ /, ''))
        }
        if (data.length) onEvent(event, JSON.parse(data.join('\n')))
      }
      if (final && buffer.trim()) throw new Error('Kết nối bị gián đoạn trước khi nhận đủ dữ liệu.')
    },
  }
}

export async function readChatStream(response, onEvent) {
  if (!response.body) throw new Error('Trình duyệt chưa hỗ trợ nhận câu trả lời trực tiếp.')
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let completed = false
  const parser = createEventParser((event, data) => {
    if (event === 'error') throw new Error(data.message || 'Không thể hoàn thành câu trả lời.')
    if (event === 'done') completed = true
    onEvent(event, data)
  })
  try {
    while (true) {
      const { value, done } = await reader.read()
      if (done) {
        parser.push(decoder.decode(), true)
        break
      }
      parser.push(decoder.decode(value, { stream: true }))
    }
    if (!completed) throw new Error('Mất kết nối trước khi AI hoàn thành. Bạn có thể thử lại.')
  } finally {
    await reader.cancel().catch(() => {})
    reader.releaseLock()
  }
}
