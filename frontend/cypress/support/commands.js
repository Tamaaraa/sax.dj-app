Cypress.Commands.add("login", () => {
  cy.visit("/login");
  cy.get("input[type=email]").type("testing1@gmail.com");
  cy.get("input[type=password]").type(Cypress.env("TEST_ACC_1_PASS"));
  cy.get("button[type=submit]").click();
  cy.wait(1000);
});

Cypress.Commands.add("login2", () => {
  cy.visit("/login");
  cy.get("input[type=email]").type("testing2@gmail.com");
  cy.get("input[type=password]").type(Cypress.env("TEST_ACC_2_PASS"));
  cy.get("button[type=submit]").click();
  cy.wait(1000);
});
