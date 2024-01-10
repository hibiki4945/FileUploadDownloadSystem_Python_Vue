// import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import Vue3EasyDataTable from 'vue3-easy-data-table';
import 'vue3-easy-data-table/dist/style.css';

// import FileAgent from 'vue-file-agent';
// import 'vue-file-agent/dist/vue-file-agent.css';

// import ElementPlus from 'element-plus';
// import 'element-plus/theme-chalk/index.css';

const app = createApp(App)

app.use(createPinia())
app.use(router)
// app.use(ElementPlus)
app.component('EasyDataTable', Vue3EasyDataTable);
// app.component('FileAgent', FileAgent);
// app.component('ElementPlus', ElementPlus);

app.mount('#app')