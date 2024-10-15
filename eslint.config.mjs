import globals from "globals";
import pluginJs from "@eslint/js";
import prettierPlugin from "eslint-plugin-prettier";
import airbnbConfig from "eslint-config-airbnb";

export default [
  {
    files: ["*.js"],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        ...globals.mocha
      },
      ecmaVersion: 2022,
      sourceType: "module",
    },
    plugins: {
      prettier: prettierPlugin,
    },

    rules: {
      ...pluginJs.configs.recommended.rules,
      ...airbnbConfig.rules,
      "prettier/prettier": "error",
    }
  },
];