import "../support/commands";

describe("Video Queue", () => {
  const chatMessage = "Hello, this is a test message!";
  const username = "Testing1";

  const randomRoomName = Math.random().toString(36).substring(2, 12);

  it("should create a room", () => {
    cy.login();
    cy.visit("/browse");
    cy.get("button").contains("Create Room").click();
    cy.wait(100);
    cy.get("input[id=roomName]").type(randomRoomName);
    cy.get("button[id=roomCreateBtn]").click();
    cy.wait(200);
    cy.contains(randomRoomName).should("exist");
  });

  it("should send the message to the chat", () => {
    cy.login();
    cy.visit("/browse");
    cy.contains(randomRoomName).click();
    cy.wait(500);

    cy.get("input[placeholder='Type a message...']").type(chatMessage);
    cy.get("button").contains("Send").click();
    cy.wait(500);
    cy.get(".chat-messages .chat-message").should(
      "contain",
      `${username}: ${chatMessage}`
    );
  });

  it("should see the message from a different user", () => {
    cy.login2();
    cy.visit("/browse");
    cy.contains(randomRoomName).click();
    cy.wait(500);

    cy.get(".chat-messages .chat-message").should(
      "contain",
      `${username}: ${chatMessage}`
    );
  });

  after(() => {
    cy.visit("/browse");
    cy.get("button").contains("Logout").click();
    cy.wait(500);
    cy.login();
    cy.visit("/browse");
    cy.contains(randomRoomName).click();
    cy.wait(1000);
    cy.get("button").contains("Remove room").click();
    cy.wait(1000);
    cy.contains(randomRoomName).should("not.exist");
  });
});
