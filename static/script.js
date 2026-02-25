// Drag & Drop
function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
  ev.preventDefault();

  const data = ev.dataTransfer.getData("text");
  const taskCard = document.getElementById(data);

  const column = ev.currentTarget;
  const status = column.dataset.status;
  const taskContainer = column.querySelector(".kanban-tasks");

  const taskId = data.split("-")[1];

  fetch(`/tasks/${taskId}/update_status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ status: status })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      taskContainer.appendChild(taskCard);
    } else {
      alert("Failed to update task status");
    }
  })
  .catch(err => console.error(err));
}