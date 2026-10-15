import { h } from 'vue'

export function safeLink(value) {
  try {
    const url = new URL(value, 'https://local.invalid')
    return ['http:', 'https:'].includes(url.protocol) ? value : null
  } catch { return null }
}

const MATH_SYMBOLS = {
  '\\times': '×', '\\cdot': '·', '\\div': '÷', '\\approx': '≈', '\\ast': '∗', '\\star': '⋆', '\\bullet': '•',
  '\\le': '≤', '\\leq': '≤', '\\ge': '≥', '\\geq': '≥', '\\neq': '≠', '\\ne': '≠', '\\pm': '±', '\\mp': '∓',
  '\\infty': '∞', '\\partial': '∂', '\\nabla': '∇', '\\sum': '∑', '\\prod': '∏', '\\int': '∫', '\\oint': '∮',
  '\\to': '→', '\\rightarrow': '→', '\\leftarrow': '←', '\\leftrightarrow': '↔', '\\mapsto': '↦',
  '\\Rightarrow': '⇒', '\\Leftarrow': '⇐', '\\Leftrightarrow': '⇔', '\\implies': '⇒', '\\iff': '⇔',
  '\\in': '∈', '\\notin': '∉', '\\ni': '∋', '\\subset': '⊂', '\\supset': '⊃', '\\subseteq': '⊆', '\\supseteq': '⊇',
  '\\cup': '∪', '\\cap': '∩', '\\emptyset': '∅', '\\varnothing': '∅', '\\setminus': '∖',
  '\\forall': '∀', '\\exists': '∃', '\\neg': '¬', '\\lnot': '¬', '\\land': '∧', '\\lor': '∨', '\\not': '¬',
  '\\sim': '∼', '\\simeq': '≃', '\\cong': '≅', '\\equiv': '≡', '\\propto': '∝', '\\asymp': '≍',
  '\\ll': '≪', '\\gg': '≫', '\\prec': '≺', '\\succ': '≻',
  '\\ldots': '…', '\\cdots': '⋯', '\\dots': '…', '\\vdots': '⋮', '\\ddots': '⋱',
  '\\degree': '°', '\\circ': '∘', '\\prime': '′', '\\angle': '∠', '\\triangle': '△',
  '\\langle': '⟨', '\\rangle': '⟩', '\\lbrace': '{', '\\rbrace': '}',
  '\\lceil': '⌈', '\\rceil': '⌉', '\\lfloor': '⌊', '\\rfloor': '⌋',
  '\\mid': '|', '\\parallel': '∥', '\\perp': '⊥', '\\therefore': '∴', '\\because': '∵',
  '\\oplus': '⊕', '\\otimes': '⊗', '\\ominus': '⊖', '\\odot': '⊙',
  '\\alpha': 'α', '\\beta': 'β', '\\gamma': 'γ', '\\delta': 'δ', '\\epsilon': 'ε', '\\varepsilon': 'ε',
  '\\zeta': 'ζ', '\\eta': 'η', '\\theta': 'θ', '\\vartheta': 'ϑ', '\\iota': 'ι', '\\kappa': 'κ',
  '\\lambda': 'λ', '\\mu': 'μ', '\\nu': 'ν', '\\xi': 'ξ', '\\pi': 'π', '\\varpi': 'ϖ',
  '\\rho': 'ρ', '\\varrho': 'ϱ', '\\sigma': 'σ', '\\varsigma': 'ς', '\\tau': 'τ', '\\upsilon': 'υ',
  '\\phi': 'φ', '\\varphi': 'φ', '\\chi': 'χ', '\\psi': 'ψ', '\\omega': 'ω',
  '\\Gamma': 'Γ', '\\Delta': 'Δ', '\\Theta': 'Θ', '\\Lambda': 'Λ', '\\Xi': 'Ξ', '\\Pi': 'Π',
  '\\Sigma': 'Σ', '\\Upsilon': 'Υ', '\\Phi': 'Φ', '\\Psi': 'Ψ', '\\Omega': 'Ω',
  '\\quad': ' ', '\\qquad': ' ', '\\,': ' ', '\\;': ' ', '\\:': ' ', '\\%': '%',
}

/** Lệnh phông/kiểu: bỏ tên lệnh, giữ nội dung và đổi kiểu chữ cho dễ đọc. */
const MATH_FONTS = {
  mathbf: 'bold', textbf: 'bold', pmb: 'bold',
  mathit: 'italic', textit: 'italic', emph: 'italic',
  boldsymbol: 'bolditalic', bm: 'bolditalic',
  mathbb: 'double', mathcal: 'script', mathscr: 'script', mathfrak: 'fraktur',
  mathsf: 'sans', textsf: 'sans', mathtt: 'mono', texttt: 'mono',
  text: 'plain', textrm: 'plain', mathrm: 'plain', mathnormal: 'plain', textnormal: 'plain',
  textup: 'plain', textmd: 'plain', textsc: 'plain', textsl: 'plain',
  operatorname: 'plain', mathop: 'plain', mathbin: 'plain', mathrel: 'plain', mathord: 'plain',
  mathopen: 'plain', mathclose: 'plain', mathinner: 'plain', mathpunct: 'plain',
  boxed: 'plain', mbox: 'plain', hbox: 'plain', underline: 'plain', overbrace: 'plain', underbrace: 'plain',
}

const MATH_ACCENTS = {
  hat: '\u0302', widehat: '\u0302', bar: '\u0304', overline: '\u0305', tilde: '\u0303', widetilde: '\u0303',
  vec: '\u20D7', overrightarrow: '\u20D7', overleftarrow: '\u20D6', overleftrightarrow: '\u20E1',
  dot: '\u0307', ddot: '\u0308', acute: '\u0301', grave: '\u0300', breve: '\u0306', check: '\u030C',
}

const MATH_DROP = new Set([
  'left', 'right', 'middle',
  'big', 'Big', 'bigg', 'Bigg',
  'bigl', 'bigr', 'Bigl', 'Bigr', 'biggl', 'biggr', 'Biggl', 'Biggr',
  'displaystyle', 'textstyle', 'scriptstyle', 'scriptscriptstyle',
  'limits', 'nolimits', 'displaylimits', '!',
])

const DOUBLE_UPPER = [...'𝔸𝔹ℂ𝔻𝔼𝔽𝔾ℍ𝕀𝕁𝕂𝕃𝕄ℕ𝕆ℙℚℝ𝕊𝕋𝕌𝕍𝕎𝕏𝕐ℤ']
const SCRIPT_UPPER = [...'𝒜ℬ𝒞𝒟ℰℱ𝒢ℋℐ𝒥𝒦ℒℳ𝒩𝒪𝒫𝒬ℛ𝒮𝒯𝒰𝒱𝒲𝒳𝒴𝒵']
const FRAKTUR_UPPER = [...'𝔄𝔅ℭ𝔇𝔈𝔉𝔊ℌℑ𝔍𝔎𝔏𝔐𝔑𝔒𝔓𝔔ℜ𝔖𝔗𝔘𝔙𝔚𝔛𝔜ℨ']

function styleMath(kind, text) {
  const write = (upperBase, lowerBase, digitBase, upperChars, lowerSkip) => [...text].map(ch => {
    const code = ch.codePointAt(0)
    if (code >= 65 && code <= 90) return upperChars ? upperChars[code - 65] : String.fromCodePoint(upperBase + code - 65)
    if (code >= 97 && code <= 122) {
      if (lowerSkip?.[ch]) return lowerSkip[ch]
      return String.fromCodePoint(lowerBase + code - 97)
    }
    if (code >= 48 && code <= 57 && digitBase != null) return String.fromCodePoint(digitBase + code - 48)
    return ch
  }).join('')
  if (kind === 'bold') return write(0x1D400, 0x1D41A, 0x1D7CE)
  if (kind === 'italic') return write(0x1D434, 0x1D44E, null, null, { h: '\u210E' })
  if (kind === 'bolditalic') return write(0x1D468, 0x1D482, 0x1D7CE)
  if (kind === 'double') return write(0, 0x1D552, 0x1D7D8, DOUBLE_UPPER)
  if (kind === 'script') return write(0, 0x1D4B6, null, SCRIPT_UPPER)
  if (kind === 'fraktur') return write(0, 0x1D51E, null, FRAKTUR_UPPER)
  if (kind === 'sans') return write(0x1D5A0, 0x1D5BA, 0x1D7E2)
  if (kind === 'mono') return write(0x1D670, 0x1D68A, 0x1D7F6)
  return text
}

function readableMath(source) {
  let result = ''
  for (let i = 0; i < source.length;) {
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
    if (source[i] === '\\') {
      const command = /^\\([a-zA-Z]+|.)/.exec(source.slice(i))
      if (command) {
        i += command[0].length
        const name = command[1]
        if (name === 'frac') result += `(${readGroup()}) / (${readGroup()})`
        else if (name === 'sqrt') {
          while (/\s/.test(source[i] || '')) i++
          let degree = ''
          if (source[i] === '[') {
            const end = source.indexOf(']', i + 1)
            if (end !== -1) {
              degree = readableMath(source.slice(i + 1, end))
              i = end + 1
            }
          }
          const body = readGroup()
          result += `${degree ? `${degree}√` : '√'}(${body})`
        } else if (MATH_FONTS[name]) result += styleMath(MATH_FONTS[name], readGroup())
        else if (MATH_ACCENTS[name]) {
          const body = readGroup()
          result += body ? `${body}${MATH_ACCENTS[name]}` : ''
        } else if (!MATH_DROP.has(name)) result += MATH_SYMBOLS[command[0]] ?? name
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
