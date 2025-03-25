describe("Video Queue", () => {
  it("should create a room", () => {
    cy.visit("/browse");
    cy.get("button").contains("Create Room").click();
    cy.get("input[type=text]").type("Test Room");
    cy.get("button[type=submit]").click();
  });

  it("should load the video queue", () => {
    cy.get(".video-queue h3").should("contain", "Video Queue");
  });

  it("should add a video to the queue", () => {
    const videoUrl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";

    cy.get("input[placeholder='Add YouTube URL...']").type(videoUrl);
    cy.contains("Add to Queue").click();

    cy.get(".video-queue ul li").should("contain", "By");
  });

  it("should remove a video from the queue", () => {
    cy.get(".video-queue ul li")
      .first()
      .within(() => {
        cy.contains("Remove").click();
      });

    cy.get(".video-queue ul li").should("have.length.lessThan", 1);
  });
});
