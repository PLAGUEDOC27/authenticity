// =====================
// UPLOAD PAGE LOGIC
// =====================
const uploadBox = document.getElementById("uploadBox");
const fileInput = document.getElementById("fileInput");
const fileName = document.getElementById("fileName");

if (uploadBox && fileInput && fileName) {

    // Click anywhere to open file picker
    uploadBox.addEventListener("click", () => fileInput.click());

    // Drag over
    uploadBox.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadBox.classList.add("dragover");
    });

    // Drag leave
    uploadBox.addEventListener("dragleave", () => {
        uploadBox.classList.remove("dragover");
    });

    // Drop file
    uploadBox.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadBox.classList.remove("dragover");

        const file = e.dataTransfer.files[0];
        fileInput.files = e.dataTransfer.files;

        fileName.textContent = "Selected: " + file.name;
    });

    // File selected manually
    fileInput.addEventListener("change", () => {
        fileName.textContent = "Selected: " + fileInput.files[0].name;
    });

}


// =====================
// ADMIN CHART LOGIC
// =====================
const chartElement = document.getElementById("adminChart");

if (chartElement && typeof Chart !== "undefined") {

    // Optional safety check (if variables exist)
    if (typeof total_users !== "undefined") {

        new Chart(chartElement, {
            type: 'bar',
            data: {
                labels: ['Users', 'Documents', 'Avg Plagiarism', 'Avg AI'],
                datasets: [{
                    data: [
                        total_users,
                        total_docs,
                        avg_plagiarism,
                        avg_ai
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false }
                }
            }
        });

    }
}

const analysisChart = document.getElementById("analysisChart");

if (analysisChart && typeof Chart !== "undefined") {

    new Chart(analysisChart, {
        type: 'doughnut',
        data: {
            labels: ['Plagiarism', 'AI'],
            datasets: [{
                data: [plagiarism, ai]
            }]
        }
    });

}