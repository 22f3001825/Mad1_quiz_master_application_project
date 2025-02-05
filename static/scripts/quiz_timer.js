// quiz_timer.js

document.addEventListener("DOMContentLoaded", function () {
    let timerElement = document.querySelector(".time");
    let remainingTime = 300; // Default to 5 minutes
    let timerInterval;
  
    // Fetch the saved timer value from the backend
    fetch("/user/get_timer")
      .then((response) => response.json())
      .then((data) => {
        remainingTime = data.remaining_time;
        updateTimerDisplay();
        startTimer();
      });
  
    function updateTimerDisplay() {
      let minutes = Math.floor(remainingTime / 60);
      let seconds = remainingTime % 60;
      timerElement.textContent = `${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
    }
  
    function startTimer() {
      timerInterval = setInterval(function () {
        if (remainingTime > 0) {
          remainingTime--;
          updateTimerDisplay();
        } else {
          clearInterval(timerInterval);
          alert("Time's up! Submitting the quiz.");
          submitForm(); // Call the submitForm function
        }
      }, 1000);
    }
  
    // Function to submit the form with all required data
    function submitForm() {
      const form = document.querySelector("form");
      const questionId = form.querySelector('input[name="question_id"]').value;
      const selectedOption = form.querySelector('input[name="selected_option"]:checked')?.value || -1; // Default to -1 if no option is selected
      const remainingTimeInput = form.querySelector('input[name="remaining_time"]');
  
      // Set the remaining time to 0
      remainingTimeInput.value = 0;
  
      // Create hidden inputs for missing data
      const hiddenQuestionId = document.createElement("input");
      hiddenQuestionId.type = "hidden";
      hiddenQuestionId.name = "question_id";
      hiddenQuestionId.value = questionId;
  
      const hiddenSelectedOption = document.createElement("input");
      hiddenSelectedOption.type = "hidden";
      hiddenSelectedOption.name = "selected_option";
      hiddenSelectedOption.value = selectedOption;
  
      // Append hidden inputs to the form
      form.appendChild(hiddenQuestionId);
      form.appendChild(hiddenSelectedOption);
  
      // Submit the form
      form.submit();
    }
  
    // Save timer before page reload or form submission
    function saveRemainingTime() {
      fetch("/user/update_timer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ remaining_time: remainingTime }),
      });
    }
  
    // Before page unload (navigation or reload)
    window.addEventListener("beforeunload", saveRemainingTime);
  
    // Before form submission
    document.querySelector("form").addEventListener("submit", function () {
      document.getElementById("remaining_time").value = remainingTime;
      saveRemainingTime();
    });
  });