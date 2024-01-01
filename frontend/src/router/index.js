import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
// import 'vue-eaasytable/libs/themes-base/index.css'
// import 'vue-easytable/libs/theme-default/index.css'
// import {
//   VTable,VPagination
// } from 'vue-easytable'

// Vue.component(VTable.name, VTable)
// Vue.component('ve-table', VTable)
// Vue.component(VPagination.name, VPagination)

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "index",
      component: Home,
      meta: { title: "menu.home" },
    },
  ]
})

export default router