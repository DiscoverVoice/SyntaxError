import globals from "globals";
import pluginJs from "@eslint/js";
import prettierPlugin from "eslint-plugin-prettier";
import airbnbConfig from "eslint-config-airbnb";

export default [{
    files: ["*/.js"],
    languageOptions: {
        globals: {
            ...globals.commonjs,
            ...globals.node,
            ...globals.mocha,
            process: "readonly"
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
        "prettier/prettier": ["error", { semi: true }],
        "no-const-assign": "warn",
        "no-this-before-super": "warn",
        "no-undef": "warn",
        "no-unreachable": "warn",
        "no-unused-vars": "warn",
        "constructor-super": "warn",
        "valid-typeof": "warn",
    },
}];