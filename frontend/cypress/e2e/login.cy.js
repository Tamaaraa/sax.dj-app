import "../support/commands";

describe("Login", () => {
  let userId;
  let localStorageMap = { token: null, username: null };

  it("should register a user", () => {
    cy.visit("/login");
    cy.get("p").contains("Register").click();
    cy.intercept("POST", "/api/register").as("registerRequest");
    cy.get("input[type=email]").type("testing@gmail.com");
    cy.get("input[type=password]").type("password123");
    cy.get("input[type=text]").type("testing");
    cy.get("button[type=submit]").click();
    cy.wait(1000);
    cy.wait("@registerRequest").then((interception) => {
      userId = interception.response.body.user_id;
      localStorageMap.token = interception.response.body.token;
      localStorageMap.username = interception.response.body.username;
      cy.window().then((win) => {
        expect(win.localStorage.getItem("token")).to.equal(
          interception.response.body.token
        );
        expect(win.localStorage.getItem("username")).to.equal(
          interception.response.body.username
        );
      });
    });
  });

  it("should log the user out", () => {
    window.localStorage.setItem("token", localStorageMap.token);
    window.localStorage.setItem("username", localStorageMap.username);
    cy.visit("/browse");
    cy.wait(2000);
    cy.get("button").contains("Logout").click();
    cy.wait(1000);
    cy.get("button").contains("Login").should("exist");
  });

  after(() => {
    cy.request("DELETE", `127.0.0.1:5000/api/login/delete`, {
      body: JSON.stringify({ user_id: userId }),
      headers: {
        "Content-Type": "application/json",
      },
    });
  });
});
