document.addEventListener("DOMContentLoaded", function() {
    // Event delegation for 'click' events on buttons
    document.addEventListener("click", function(event) {
      var target = event.target;
  
      if (target.id === "submitButton") {
        // ... code for handling the 'Submit' button click
        // Example: sendChatMessage();
      } else if (target.id === "likeButton") {
        sendFeedback("like");
      } else if (target.id === "dislikeButton") {
        sendFeedback("dislike");
      }
    });
  });
  
  function sendFeedback(reaction) {
    // Check if the 'response' element exists before reading its content
    var responseElement = document.getElementById("response");
    if (responseElement) {
      var response = responseElement.textContent;
  
      // Send the data to the Flask server using the Fetch API
      fetch("/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          "response": response,
          "reaction": reaction
        })
      })
      .then(response => response.json())
      .then(data => {
        // Handle the response from the Flask server
        console.log("Feedback received:", data);
      })
      .catch(error => {
        console.error("Error:", error);
      });
    }
  }