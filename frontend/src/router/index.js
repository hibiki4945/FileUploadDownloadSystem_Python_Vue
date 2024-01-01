import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
// import 'vue-easytable/libs/themes-base/index.css'
// import {
//    VTable,VPagination} from '../../node_modules/vue-easytable/libs'

// Vue.component(VTable.name, VTable)
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
