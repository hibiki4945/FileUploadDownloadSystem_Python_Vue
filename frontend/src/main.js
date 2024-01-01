// import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'import Vue from "vue";
// import "vue-easytable/libs/theme-default/index.css";
// import VueEasytable from "vue-easytable";

// Vue.use(VueEasytable);

// new Vue({
//     el: "#app",
//     render: (h) => h(App),
// });

const app = createApp(App)

app.use(createPinia())
app.use(router)
// app.use(VueEasytable);

app.mount('#app')
