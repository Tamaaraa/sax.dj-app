const dotenv = require("dotenv");

dotenv.config({ path: "../.env" });

module.exports = {
  e2e: {
    baseUrl: "http://localhost:5173",
    specPattern: "cypress/e2e/**/*.cy.js",
    supportFile: false,
    setupNodeEvents(on, config) {
      config.env.TEST_ACC_1_PASS = process.env.TEST_ACC_1_PASS;
      return config;
    },
  },
};
