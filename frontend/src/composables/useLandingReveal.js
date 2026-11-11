import { onMounted, onUnmounted } from 'vue'

// `data-reveal` hiện từng khối; `data-stagger` hiện lần lượt các phần tử con theo chỉ số `--i`.
export function useLandingReveal(rootSelector = '.landing :is([data-reveal], [data-stagger])') {
  let observer = null

  onMounted(() => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const nodes = document.querySelectorAll(rootSelector)

    nodes.forEach((el) => {
      if (!el.hasAttribute('data-stagger')) return
      Array.from(el.children).forEach((child, index) => child.style.setProperty('--i', index))
    })

    if (reduceMotion) {
      nodes.forEach((el) => el.classList.add('is-visible'))
      return
    }

    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return
          entry.target.classList.add('is-visible')
          observer?.unobserve(entry.target)
        })
      },
      { threshold: 0.14, rootMargin: '0px 0px -40px 0px' },
    )

    nodes.forEach((el) => observer.observe(el))
  })

  onUnmounted(() => {
    observer?.disconnect()
    observer = null
  })
}
