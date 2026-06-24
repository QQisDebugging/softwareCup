import './styles/impeccable-overrides.css'
import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './styles/main.css'
import './styles/product-final.css'
import './styles/premium-product.css'
import './styles/design-system.css' // 单一真相源，最后导入以赢级联

import './styles/today-product-lock.css'
createApp(App).use(createPinia()).use(router).mount('#app')
