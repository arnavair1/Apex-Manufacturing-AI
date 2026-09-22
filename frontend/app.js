const API_URL = "http://127.0.0.1:8000";


const questionInput =
    document.getElementById("question");

const askButton =
    document.getElementById("ask-button");

const answerBox =
    document.getElementById("answer");

const loading =
    document.getElementById("loading");

const status =
    document.getElementById("status");


async function checkAPI() {

    try {

        const response =
            await fetch(`${API_URL}/health`);

        if (!response.ok) {
            throw new Error("API unavailable");
        }

        status.textContent = "API: online";
        status.classList.add("online");
        status.classList.remove("offline");

    } catch (error) {

        status.textContent = "API: offline";
        status.classList.add("offline");
        status.classList.remove("online");

    }
}


async function askApex() {

    const question =
        questionInput.value.trim();


    if (!question) {

        answerBox.textContent =
            "Please enter a manufacturing question.";

        return;
    }


    askButton.disabled = true;

    loading.classList.remove("hidden");

    answerBox.textContent =
        "Apex AI is analyzing the manufacturing data...";


    try {

        const response =
            await fetch(`${API_URL}/chat`, {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })

            });


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "The API returned an error."
            );

        }


        answerBox.textContent =
            data.answer || "No answer returned.";


    } catch (error) {

        answerBox.textContent =
            `Error: ${error.message}

Make sure the FastAPI server is running on port 8000.`;

    } finally {

        askButton.disabled = false;

        loading.classList.add("hidden");

    }

}


askButton.addEventListener(
    "click",
    askApex
);


questionInput.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            (event.metaKey || event.ctrlKey)
        ) {

            askApex();

        }

    }
);


document
    .querySelectorAll(".example-button")
    .forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                questionInput.value =
                    button.dataset.question;

                questionInput.focus();

            }
        );

    });


checkAPI();