function escapeHTML(value) {
    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


function showLoading(button, text) {
    button.disabled = true;
    button.dataset.originalText = button.innerText;
    button.innerText = text;
}


function hideLoading(button) {
    button.disabled = false;
    button.innerText = button.dataset.originalText;
}


function displayList(elementId, items) {
    const element = document.getElementById(elementId);

    element.innerHTML = "";

    if (!items || items.length === 0) {
        element.innerHTML = "<li>No information available.</li>";
        return;
    }

    items.forEach(item => {
        const li = document.createElement("li");
        li.innerHTML = escapeHTML(item);
        element.appendChild(li);
    });
}


async function createPlan() {

    const question =
        document.getElementById("question").value.trim();

    const button =
        document.getElementById("planButton");

    if (!question) {
        alert("Please enter what you want to achieve.");
        return;
    }

    showLoading(button, "Creating your plan...");

    try {

        const response = await fetch("/plan", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(
                data.detail || "Something went wrong."
            );
        }


        document.getElementById("result")
            .classList.remove("hidden");


        document.getElementById("goal").innerHTML =
            escapeHTML(data.goal);


        displayList(
            "assumptions",
            data.assumptions
        );


        displayList(
            "priorities",
            data.priorities
        );


        const actionPlan =
            document.getElementById("actionPlan");

        actionPlan.innerHTML = "";


        if (data.action_plan) {

            data.action_plan.forEach(phase => {

                const phaseDiv =
                    document.createElement("div");

                phaseDiv.className = "phase";

                phaseDiv.innerHTML = `
                    <h3>${escapeHTML(phase.phase)}</h3>
                    <p class="duration">
                        ${escapeHTML(phase.duration)}
                    </p>
                    <ul>
                        ${(phase.tasks || [])
                            .map(task =>
                                `<li>${escapeHTML(task)}</li>`
                            )
                            .join("")
                        }
                    </ul>
                `;

                actionPlan.appendChild(phaseDiv);

            });
        }


        displayList(
            "todayActions",
            data.today_actions
        );


        document.getElementById(
            "successCheckpoint"
        ).innerHTML =
            escapeHTML(data.success_checkpoint);


        window.scrollTo({
            top: document.getElementById("result").offsetTop - 30,
            behavior: "smooth"
        });

    }

    catch (error) {

        alert(
            "Error: " + error.message
        );

    }

    finally {

        hideLoading(button);

    }
}


async function replanPlan() {

    const progress =
        document.getElementById("progress")
            .value
            .trim();

    const button =
        document.getElementById("replanButton");


    if (!progress) {

        alert(
            "Please describe your progress first."
        );

        return;
    }


    showLoading(
        button,
        "Replanning..."
    );


    try {

        const response = await fetch(
            "/replan",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    progress: progress
                })
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Replanning failed."
            );

        }


        document.getElementById(
            "replanResult"
        ).classList.remove("hidden");


        const updatedPlan =
            document.getElementById(
                "updatedPlan"
            );


        updatedPlan.innerHTML = "";


        (data.updated_plan || [])
            .forEach(step => {

                const div =
                    document.createElement("div");

                div.className = "updated-step";

                div.innerHTML =
                    escapeHTML(step);

                updatedPlan.appendChild(div);

            });


        displayList(
            "newTodayActions",
            data.today_actions
        );


        document.getElementById(
            "nextCheckpoint"
        ).innerHTML =
            escapeHTML(
                data.next_checkpoint
            );


        window.scrollTo({
            top: document.getElementById(
                "replanResult"
            ).offsetTop - 30,
            behavior: "smooth"
        });

    }

    catch (error) {

        alert(
            "Error: " + error.message
        );

    }

    finally {

        hideLoading(button);

    }
}
