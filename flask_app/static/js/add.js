document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("form");

    form.addEventListener("submit", async (event) => {
        event.preventDefault(); 

        const formData = new FormData(form);
        const id = formData.get("id");

        try {
            const response = await fetch('/upload_data', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                console.log(response);
                const result = await response.text();
                console.log("Server response:", result);
                window.location.href = `/submit?id=${encodeURIComponent(id)}`;
            } else {
                console.error("Error submitting data:", response.statusText);
                alert("Failed to submit data. Please try again.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred. Please check the console.");
        }
    });
});



