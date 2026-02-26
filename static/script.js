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

document.addEventListener("DOMContentLoaded", function () {

    const analyticsDiv = document.getElementById("analytics-data");
    if (!analyticsDiv) return; // Prevent running on other pages

    const labels = JSON.parse(analyticsDiv.dataset.labels);
    const values = JSON.parse(analyticsDiv.dataset.values);
    const overdue = parseInt(analyticsDiv.dataset.overdue);
    const high = parseInt(analyticsDiv.dataset.high);
    const avg = parseFloat(analyticsDiv.dataset.avg);

    // 📊 Completed Tasks Per User (Bar)
    new Chart(document.getElementById("completedChart"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Completed Tasks",
                data: values,
                backgroundColor: "rgba(54, 162, 235, 0.6)"
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });

    // 📊 Task Health (Pie)
    new Chart(document.getElementById("healthChart"), {
        type: "pie",
        data: {
            labels: ["Overdue", "High Priority"],
            datasets: [{
                data: [overdue, high],
                backgroundColor: [
                    "rgba(255, 99, 132, 0.7)",
                    "rgba(255, 206, 86, 0.7)"
                ]
            }]
        },
        options: {
            responsive: true
        }
    });

    // 📊 Average Completion Time (Doughnut)
    new Chart(document.getElementById("avgChart"), {
        type: "doughnut",
        data: {
            labels: ["Avg Completion (Days)"],
            datasets: [{
                data: [avg],
                backgroundColor: ["rgba(75, 192, 192, 0.7)"]
            }]
        },
        options: {
            responsive: true
        }
    });

});