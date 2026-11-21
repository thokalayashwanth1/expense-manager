import { createRouter, createWebHistory } from "vue-router";
import Dashboard from "./pages/Dashboard.vue";
import Expenses from "./pages/Expenses.vue";
import Budgets from "./pages/Budgets.vue";
import Dependents from "./pages/Dependents.vue";

export default createRouter({
  history: createWebHistory("/expense-manager"),
  routes: [
    { path: "/", name: "Dashboard", component: Dashboard },
    { path: "/expenses", name: "Expenses", component: Expenses },
    { path: "/budgets", name: "Budgets", component: Budgets },
    { path: "/dependents", name: "Dependents", component: Dependents },
  ],
});
