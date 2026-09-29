const { defineConfig } = require("../frappe/node_modules/cypress");

module.exports = defineConfig({
    e2e: {
        baseUrl: "http://localhost:8000",
        supportFile: "../frappe/cypress/support/e2e.js",
        specPattern: [
            "./cypress/integration/*.js",
            "**/ui_test_*.js",
        ],
    },
});
