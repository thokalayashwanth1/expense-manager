import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./pages/Dashboard.vue";
import Expenses from "./pages/Expenses.vue";
import Categories from "./pages/Categories.vue";
import Budgets from "./pages/Budgets.vue";
import Dependents from "./pages/Dependents.vue";
import Reports from "./pages/Reports.vue";
import Telegram from "./pages/Telegram.vue";

export default createRouter({
  history: createWebHistory("/expense-manager"),
  routes: [
    { path: "/", name: "Dashboard", component: Dashboard },
    { path: "/expenses", name: "Expenses", component: Expenses },
    { path: "/categories", name: "Categories", component: Categories },
    { path: "/budgets", name: "Budgets", component: Budgets },
    { path: "/dependents", name: "Dependents", component: Dependents },
    { path: "/reports", name: "Reports", component: Reports },
    { path: "/telegram", name: "Telegram", component: Telegram },
  ],
});
