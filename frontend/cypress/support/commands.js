Cypress.Commands.add("login", () => {
  cy.visit("/login");
  cy.get("input[type=email]").type("testing1@gmail.com");
  cy.get("input[type=password]").type(Cypress.env("TEST_ACC_1_PASS"));
  cy.get("button[type=submit]").click();
  cy.wait(1000);
});
