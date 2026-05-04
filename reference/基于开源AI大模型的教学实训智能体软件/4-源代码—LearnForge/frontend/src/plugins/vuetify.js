/**
 * plugins/vuetify.js
 *
 * Framework documentation: https://vuetifyjs.com`
 */

// Styles
// import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import { pl, zhHans } from 'vuetify/locale'
// import { md3 } from 'vuetify/blueprints'
// Composables
import { createVuetify } from 'vuetify'
const defaultTheme = 'light';

// https://vuetifyjs.com/en/introduction/why-vuetify/#feature-guides
export default createVuetify({
  
  theme: {
    defaultTheme: defaultTheme,
    lang:{
      locales: {zhHans},
      current: 'zhHans'
    },
    icons:{
      iconfont: 'mdi',	// 设置使用本地的icon资源
    },
    themes: {
      light: {
        colors: {
        
          chatcontent: '#f5f5f5',
        },
      },
      dark: {
        colors: {
        
          chatcontent: '#000000',
        },
      }
    }
  },
})
