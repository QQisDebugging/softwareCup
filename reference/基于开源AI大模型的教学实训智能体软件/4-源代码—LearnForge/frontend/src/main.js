/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'
import App from './App.vue'

// 全局样式文件
import './assets/styles/globals.css'

import { createApp } from 'vue'
import router from './router'
import VueCodeMirror from 'vue-codemirror'

import VueMarkdownIt from 'vue3-markdown-it';

import VHighlight from 'v-highlight';
import 'highlight.js/styles/default.css';

import createTodoListPlugin from '@kangc/v-md-editor/lib/plugins/todo-list/index';
import '@kangc/v-md-editor/lib/plugins/todo-list/todo-list.css';
import createKatexPlugin from '@kangc/v-md-editor/lib/plugins/katex/cdn';
import VMdPreview from '@kangc/v-md-editor/lib/preview';
import '@kangc/v-md-editor/lib/style/preview.css';
import githubTheme from '@kangc/v-md-editor/lib/theme/github.js';
import '@kangc/v-md-editor/lib/theme/style/github.css';

import hljs from 'highlight.js';

VMdPreview.use(githubTheme, {
  Hljs: hljs,
});
VMdPreview.use(createKatexPlugin());
VMdPreview.use(createTodoListPlugin());
// VMdPreview.use(createCopyCodePreview());





// VMEDITOR
import VMdEditor from '@kangc/v-md-editor';
import '@kangc/v-md-editor/lib/style/base-editor.css';

VMdEditor.use(githubTheme, {
  Hljs: hljs,
});
VMdEditor.use(createKatexPlugin());
VMdEditor.use(createTodoListPlugin());

const app = createApp(App)
app.use(VHighlight);
app.use(VMdPreview);
app.use(VMdEditor);
// import 'codemirror/lib/codemirror.css'

// 在开发环境中使用代理，生产环境中使用完整URL
export const backendUrl = import.meta.env.DEV ? '' : 'http://127.0.0.1:5000';

// 设置 axios 的默认 baseURL
// axios.defaults.baseURL = backendUrl
registerPlugins(app)
app.use(router)
app.use(VueCodeMirror)
app.use(VueMarkdownIt);
app.config.globalProperties.$backendUrl = backendUrl

// 创建全局Toast实例
const toastInstance = {
  success: (message) => {
    const event = new CustomEvent('toast-show', {
      detail: { message, type: 'success' }
    });
    window.dispatchEvent(event);
  },
  error: (message) => {
    const event = new CustomEvent('toast-show', {
      detail: { message, type: 'error' }
    });
    window.dispatchEvent(event);
  },
  warning: (message) => {
    const event = new CustomEvent('toast-show', {
      detail: { message, type: 'warning' }
    });
    window.dispatchEvent(event);
  },
  info: (message) => {
    const event = new CustomEvent('toast-show', {
      detail: { message, type: 'info' }
    });
    window.dispatchEvent(event);
  }
};

app.config.globalProperties.$toast = toastInstance;
app.mount('#app')
