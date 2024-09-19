import globals from "globals";
import pluginJs from "@eslint/js";
import tseslint from "@typescript-eslint/eslint-plugin";
import prettierPlugin from "eslint-plugin-prettier";
import airbnbConfig from "eslint-config-airbnb";
import tsParser from "@typescript-eslint/parser";

export default [{
    files: ["**/*.js"],
    languageOptions: {
        parser: tsParser,
        globals: {
            ...globals.commonjs,
            ...globals.node,
            ...globals.mocha,
            ...globals.node, process: "readonly"
        },

        ecmaVersion: 2022,
        sourceType: "module",
    },
    plugins: {
        prettier: prettierPlugin,
        "@typescript-eslint": tseslint
    },
    rules: {
        ...pluginJs.configs.recommended.rules,
        ...tseslint.configs.recommended.rules,
        ...airbnbConfig.rules,
        "prettier/prettier": ["error", { semi: true }],
        "@typescript-eslint/no-explicit-any": "warn",
        "@typescript-eslint/explicit-function-return-type": "warn",
        "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
        "no-const-assign": "warn",
        "no-this-before-super": "warn",
        "no-undef": "warn",
        "no-unreachable": "warn",
        "no-unused-vars": "warn",
        "constructor-super": "warn",
        "valid-typeof": "warn",
    },
}];