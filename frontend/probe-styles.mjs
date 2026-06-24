import { chromium } from 'playwright'

const BASE = process.env.PROBE_URL || 'http://127.0.0.1:5174'
const ROLE = process.env.PROBE_ROLE || 'student-zhang'
const PATH = process.env.PROBE_PATH || '/dashboard'

const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } })

await page.addInitScript((id) => {
  localStorage.setItem('learning-account-id', id)
}, ROLE)

await page.goto(BASE + PATH, { waitUntil: 'domcontentloaded' }).catch(() => {})
await page.waitForTimeout(2000)

function pickAll(document) {
  const pick = (sel, props) => {
    const el = document.querySelector(sel)
    if (!el) return { __missing: true }
    const cs = getComputedStyle(el)
    const out = {}
    for (const p of props) out[p] = cs.getPropertyValue(p)
    return out
  }
  return pick
}

const result = await page.evaluate(() => {
  const root = getComputedStyle(document.documentElement)
  const pick = (sel, props) => {
    const el = document.querySelector(sel)
    if (!el) return { __missing: true }
    const cs = getComputedStyle(el)
    const out = {}
    for (const p of props) out[p] = cs.getPropertyValue(p)
    return out
  }
  return {
    tokens: {
      '--primary': root.getPropertyValue('--primary').trim(),
      '--bg': root.getPropertyValue('--bg').trim(),
      '--ease-out': root.getPropertyValue('--ease-out').trim(),
      '--shadow': root.getPropertyValue('--shadow').trim(),
      '--green': root.getPropertyValue('--green').trim(),
    },
    '.app-shell': pick('.app-shell', ['display', 'grid-template-columns']),
    '.app-shell > .sidebar': pick('.app-shell > .sidebar', ['position', 'flex-direction', 'background-color', 'border-right-width', 'grid-template-columns']),
    '.nav-item': pick('.nav-item', ['color', 'background-color', 'border-radius']),
    '.nav-item.router-link-active': pick('.nav-item.router-link-active', ['color', 'background-color']),
    '.button': pick('.button', ['background-color', 'border-radius', 'color']),
    '.section-panel': pick('.section-panel', ['background-color', 'border-radius', 'box-shadow']),
    '.status-pill': pick('.status-pill', ['border-radius']),
    '.topbar h1': pick('.topbar h1', ['font-size', 'color']),
    '.role-badge': pick('.topbar .role-badge', ['color', 'background-color']),
    'body': pick('body', ['background-color', 'color']),
  }
})

console.log('=== COMPUTED STYLES PROBE (logged-in shell) ===')
console.log(JSON.stringify(result, null, 2))

await page.screenshot({ path: 'output/screenshots/phase1-' + ROLE + '.png', fullPage: false })
console.log('screenshot: output/screenshots/phase1-' + ROLE + '.png')

// --- Login page probe (logged out) ---
await page.evaluate(() => localStorage.removeItem('learning-account-id'))
await page.goto(BASE + '/', { waitUntil: 'domcontentloaded' }).catch(() => {})
await page.waitForTimeout(1500)

const loginResult = await page.evaluate(() => {
  const pick = (sel, props) => {
    const el = document.querySelector(sel)
    if (!el) return { __missing: true }
    const cs = getComputedStyle(el)
    const out = {}
    for (const p of props) out[p] = cs.getPropertyValue(p)
    return out
  }
  return {
    '.login-shell': pick('.login-shell', ['background-color', 'background-image', 'color']),
    '.login-copy': pick('.login-copy', ['color']),
    '.login-copy h1': pick('.login-copy h1', ['color', 'font-size']),
    '.login-brand': pick('.login-brand', ['color']),
    '.login-brand strong': pick('.login-brand strong', ['color']),
    '.login-proof-row span': pick('.login-proof-row span', ['color', 'background-color']),
    '.login-card': pick('.login-card', ['background-color', 'color']),
    '.login-submit': pick('.login-submit', ['background-color', 'border-radius', 'color']),
  }
})

console.log('=== COMPUTED STYLES PROBE (login page) ===')
console.log(JSON.stringify(loginResult, null, 2))

await page.screenshot({ path: 'output/screenshots/phase1-login.png', fullPage: false })
console.log('screenshot: output/screenshots/phase1-login.png')

await browser.close()
