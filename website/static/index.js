function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
function deletePrinter(printerId) {
  fetch("/delete-printer", {
    method: "POST",
    body: JSON.stringify({ printerId: printerId }),
  }).then((_res) => {
    window.location.href = "/printer";
  });
}

document.addEventListener('DOMContentLoaded', function() {
  const fetchDataButtons = document.querySelectorAll('.fetch-data-btn');
  fetchDataButtons.forEach(button => {
    button.addEventListener('click', function() {
      const printerId = this.getAttribute('data-id');
      fetch('/fetch-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ printerId: printerId })
      })
      .then(response => response.json())
      .then(data => {
        console.log(data);
        window.location.href = "/printer";

        // Optionally, update the UI or display a message based on the response
      })
      .catch(error => {
        console.error('Error:', error);
        // Optionally, display an error message to the user
      });
    });
  });
});


