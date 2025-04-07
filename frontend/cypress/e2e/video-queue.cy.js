import "../support/commands";

describe("Video Queue", () => {
  const randomRoomName = Math.random().toString(36).substring(2, 12);

  beforeEach(() => {
    cy.login();
  });

  it("should create a room", () => {
    cy.visit("/browse");
    cy.get("button").contains("Create Room").click();
    cy.wait(100);
    cy.get("input[id=roomName]").type(randomRoomName);
    cy.get("button[id=roomCreateBtn]").click();
    cy.wait(200);
    cy.contains(randomRoomName).should("exist");
  });

  it("should add a video to the queue", () => {
    cy.visit("/browse");
    cy.contains(randomRoomName).click();
    cy.wait(500);

    const videoUrl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

    cy.get("input[placeholder='Add YouTube URL...']").type(videoUrl);
    cy.contains("Add to Queue").click();

    cy.wait(500);
    cy.get(".video-queue ul li").should("contain", "By");
    cy.get(
      'iframe[src="https://www.youtube.com/embed/dQw4w9WgXcQ?autoplay=1&showinfo=0&controls=0"]'
    ).should("exist");
  });

  it("should remove a video from the queue", () => {
    cy.visit("/browse");
    cy.contains(randomRoomName).click();
    cy.wait(500);

    const videoUrl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

    cy.get("input[placeholder='Add YouTube URL...']").type(videoUrl);
    cy.contains("Add to Queue").click();

    cy.wait(500);

    cy.get(".video-queue ul li").should("have.length.greaterThan", 0);

    cy.get(".video-queue ul li")
      .first()
      .within(() => {
        cy.contains("Remove").click();
      });

    cy.wait(500);

    cy.get(".video-queue ul li").should("have.length.lessThan", 1);
  });

  after(() => {
    cy.visit("/browse");
    cy.contains(randomRoomName).click();
    cy.wait(500);
    cy.get("button").contains("Remove room").click();
    cy.wait(1000);
    cy.contains(randomRoomName).should("not.exist");
  });
});
