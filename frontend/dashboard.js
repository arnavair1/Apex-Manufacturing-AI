const API_URL = "http://127.0.0.1:8000";


const questionInput =
    document.getElementById("question");


const askButton =
    document.getElementById("ask-button");


const answerBox =
    document.getElementById("answer");


const loading =
    document.getElementById("loading");


const apiStatus =
    document.getElementById("api-status");


async function checkAPI() {

    try {

        const response =
            await fetch(`${API_URL}/health`);


        if (!response.ok) {

            throw new Error(
                "API health check failed"
            );

        }


        apiStatus.textContent =
            "API: Online";


        apiStatus.classList.remove(
            "checking",
            "offline"
        );


        apiStatus.classList.add(
            "online"
        );


    } catch (error) {

        apiStatus.textContent =
            "API: Offline";


        apiStatus.classList.remove(
            "checking",
            "online"
        );


        apiStatus.classList.add(
            "offline"
        );

    }

}


async function askApexAI() {

    const question =
        questionInput.value.trim();


    if (!question) {

        answerBox.textContent =
            "Please enter a manufacturing question.";

        return;

    }


    askButton.disabled = true;

    loading.classList.remove(
        "hidden"
    );


    answerBox.textContent =
        "Apex AI is analyzing the manufacturing data...";


    try {

        const response =
            await fetch(
                `${API_URL}/chat`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "The API returned an error."
            );

        }


        answerBox.textContent =
            data.answer ||
            "The AI returned an empty response.";


    } catch (error) {

        answerBox.textContent =
            `Error connecting to Apex AI:

${error.message}

Make sure the FastAPI server is running
on port 8000.`;


    } finally {

        askButton.disabled = false;

        loading.classList.add(
            "hidden"
        );

    }

}


askButton.addEventListener(
    "click",
    askApexAI
);


document
    .querySelectorAll(".quick-button")
    .forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    questionInput.value =
                        button.dataset.question;


                    questionInput.focus();

                }
            );

        }
    );


checkAPI();