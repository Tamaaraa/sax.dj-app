describe("Login", () => {
  it("should register a user", () => {
    cy.visit("/login");
    cy.get("p").contains("Register").click();
    cy.get("input[type=email]").type("testing@gmail.com");
    cy.get("input[type=password]").type("password123");
    cy.get("input[type=text]").type("testing");
    cy.get("button[type=submit]").click();
    cy.wait(1000);
    cy.request("DELETE", "http://127.0.0.1:5000/api/login/delete");
  });
});
