import { createApp } from "vue";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import dayjs from "dayjs";
import "dayjs/locale/zh-cn";

import App from "./App.vue";
import router from "./router";
import pinia from "./stores";
import "./styles/base.css";
import "./styles/element.css";

const app = createApp(App);

app.use(pinia);
app.use(router);
dayjs.locale("zh-cn");
app.use(ElementPlus, { locale: zhCn });

app.mount("#app");
