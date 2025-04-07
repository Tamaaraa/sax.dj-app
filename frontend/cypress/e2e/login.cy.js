import "../support/commands";

describe("Login", () => {
  beforeEach(() => {
    cy.login();
  });

  it("should log the user out", () => {
    cy.visit("/browse");
    cy.wait(500);
    cy.get("button").contains("Logout").click();
    cy.wait(500);
    cy.get("button").contains("Login").should("exist");
  });
});
