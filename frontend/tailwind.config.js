import preset from "./node_modules/frappe-ui/tailwind/preset.js";

export default {
  presets: [preset],
  content: [
    "./index.html",
    "./src/**/*.{vue,js}",
    "./node_modules/frappe-ui/src/**/*.{vue,js,ts}",
  ],
};

import preset from "./node_modules/frappe-ui/tailwind/preset.js";
import { content } from "./node_modules/frappe-ui/tailwind/content.js";


export default {
  presets: [preset],
  content: [...content, "./src/**/*.{vue,js}"],
};

import preset from "frappe-ui/tailwind";
import { content } from "frappe-ui/tailwind";

export default {
  presets: [preset],
  content: [...content, "./src/**/*.{vue,js}"],
};

export default {
  plugins: { tailwindcss: {}, autoprefixer: {} },
};