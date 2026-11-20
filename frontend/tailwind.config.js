import preset from "frappe-ui/tailwind";
import { content } from "frappe-ui/tailwind";

export default {
  presets: [preset],
  content: [...content, "./src/**/*.{vue,js}"],
};
