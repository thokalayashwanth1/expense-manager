import { createApp } from "vue";
import { setConfig, frappeRequest } from "frappe-ui";
import "frappe-ui/style.css";
import App from "./App.vue";
import router from "./router";
import "./style.css";

setConfig("resourceFetcher", frappeRequest);
createApp(App).use(router).mount("#app");
