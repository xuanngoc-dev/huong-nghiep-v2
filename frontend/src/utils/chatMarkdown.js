import { h } from 'vue'

export function safeLink(value) {
  try {
    const url = new URL(value, 'https://local.invalid')
    return ['http:', 'https:'].includes(url.protocol) ? value : null
  } catch { return null }
}

function readableMath(source) {
  const symbols = {
    '\\times': '×', '\\cdot': '·', '\\div': '÷', '\\approx': '≈',
    '\\le': '≤', '\\leq': '≤', '\\ge': '≥', '\\geq': '≥',
    '\\neq': '≠', '\\pm': '±', '\\%': '%', '\\text': '',
  }
  let result = ''
  for (let i = 0; i < source.length;) {
    if (source[i] === '\\') {
      const command = /^\\([a-zA-Z]+|.)/.exec(source.slice(i))
      if (command) {
        i += command[0].length
        if (command[1] === 'frac') {
          const readGroup = () => {
            while (/\s/.test(source[i] || '')) i++
            if (source[i] !== '{') return ''
            let depth = 1
            const start = ++i
            while (i < source.length && depth) {
              if (source[i] === '{') depth++
              if (source[i] === '}') depth--
              i++
            }
            return readableMath(source.slice(start, i - 1))
          }
          result += `(${readGroup()}) / (${readGroup()})`
        } else if (command[1] === 'text') {
          while (/\s/.test(source[i] || '')) i++
          if (source[i] === '{') {
            let depth = 1
            const start = ++i
            while (i < source.length && depth) {
              if (source[i] === '{') depth++
              if (source[i] === '}') depth--
              i++
            }
            result += readableMath(source.slice(start, i - 1))
          }
        } else if (command[1] === 'left' || command[1] === 'right') {
          // TeX sizing commands do not change the readable text representation.
        } else {
          result += symbols[command[0]] ?? command[1]
        }
        continue
      }
    }
    if (source[i] === '{' || source[i] === '}') { i++; continue }
    result += source[i++]
  }
  return result.replace(/\s+/g, ' ').trim()
}

function inline(text) {
  const output = []
  const pattern = /(`[^`\n]+`|\$\$[^$\n]+\$\$|\$[^$\n]+\$|\*\*[^*\n]+\*\*|\*[^*\n]+\*|\[[^\]\n]+\]\([^\s)]+\))/g
  let cursor = 0
  for (const match of text.matchAll(pattern)) {
    output.push(text.slice(cursor, match.index))
    const token = match[0]
    if (token.startsWith('`')) output.push(h('code', token.slice(1, -1)))
    else if (token.startsWith('$')) {
      const display = token.startsWith('$$')
      const value = readableMath(token.slice(display ? 2 : 1, display ? -2 : -1))
      output.push(h(display ? 'span' : 'span', {
        class: display ? 'ai-chat__math ai-chat__math--display' : 'ai-chat__math',
        role: 'math', 'aria-label': value,
      }, value))
    }
    else if (token.startsWith('**')) output.push(h('strong', inline(token.slice(2, -2))))
    else if (token.startsWith('*')) output.push(h('em', inline(token.slice(1, -1))))
    else {
      const link = /^\[([^\]]+)\]\((.+)\)$/.exec(token)
      const href = safeLink(link[2])
      output.push(href ? h('a', { href, target: '_blank', rel: 'noopener noreferrer' }, link[1]) : link[1])
    }
    cursor = match.index + token.length
  }
  output.push(text.slice(cursor))
  return output
}

const cells = line => line.trim().replace(/^\|/, '').replace(/\|$/, '').split(/(?<!\\)\|/).map(c => c.trim().replace(/\\\|/g, '|'))

/** Render text as Vue nodes: raw HTML and unsafe links are never executed. */
export function renderMarkdown(text) {
  const lines = String(text || '').split(/\r?\n/)
  const nodes = []
  for (let i = 0; i < lines.length;) {
    const line = lines[i]
    if (!line.trim()) { i++; continue }
    const displayMath = /^\s*\$\$(.+)\$\$\s*$/.exec(line)
    if (displayMath) {
      const value = readableMath(displayMath[1])
      nodes.push(h('div', { class: 'ai-chat__math ai-chat__math--display', role: 'math', 'aria-label': value }, value))
      i++
      continue
    }
    if (line.trim().startsWith('```')) {
      const content = []
      i++
      while (i < lines.length && !lines[i].trim().startsWith('```')) content.push(lines[i++])
      i++
      nodes.push(h('pre', [h('code', content.join('\n'))]))
      continue
    }
    if (line.includes('|') && /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(lines[i + 1] || '')) {
      const headers = cells(line)
      const rows = []
      i += 2
      while (i < lines.length && lines[i].includes('|') && lines[i].trim()) {
        const row = cells(lines[i++])
        rows.push(h('tr', headers.map((_, index) => h('td', inline(row[index] || '')))))
      }
      nodes.push(h('div', { class: 'ai-chat__table-wrap', tabindex: 0, 'aria-label': 'Bảng thông tin' }, [h('table', [
        h('thead', [h('tr', headers.map(c => h('th', { scope: 'col' }, inline(c))))]), h('tbody', rows),
      ])]))
      continue
    }
    const heading = /^(#{1,6})\s+(.+)$/.exec(line)
    if (heading) { nodes.push(h(`h${Math.min(6, heading[1].length + 2)}`, inline(heading[2]))); i++; continue }
    const listMatch = /^\s*(?:([-*+])|\d+[.)])\s+(.+)$/.exec(line)
    if (listMatch) {
      const ordered = !listMatch[1]
      const items = []
      while (i < lines.length) {
        const item = /^\s*(?:([-*+])|\d+[.)])\s+(.+)$/.exec(lines[i])
        if (!item || Boolean(!item[1]) !== ordered) break
        items.push(h('li', inline(item[2])))
        i++
      }
      nodes.push(h(ordered ? 'ol' : 'ul', items))
      continue
    }
    if (/^>\s?/.test(line)) { nodes.push(h('blockquote', inline(line.replace(/^>\s?/, '')))); i++; continue }
    if (/^\s*([-*_])\1{2,}\s*$/.test(line)) { nodes.push(h('hr')); i++; continue }
    nodes.push(h('p', inline(line)))
    i++
  }
  return nodes
}
