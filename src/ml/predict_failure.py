from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "src"
    / "ml"
    / "models"
    / "machine_failure_model.joblib"
)


def load_model():

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}\n"
            "Run the training script first."
        )

    return joblib.load(
        MODEL_PATH
    )


def predict_failure(
    temperature_celsius,
    vibration_mm_s,
    pressure_psi,
):

    artifact = load_model()

    model = artifact["model"]

    features = artifact["features"]

    input_data = pd.DataFrame(
        [
            {
                "temperature_celsius":
                    temperature_celsius,

                "vibration_mm_s":
                    vibration_mm_s,

                "pressure_psi":
                    pressure_psi,
            }
        ]
    )

    input_data = input_data.reindex(
        columns=features,
        fill_value=0,
    )

    prediction = model.predict(
        input_data
    )[0]

    probabilities = model.predict_proba(
        input_data
    )[0]

    if len(probabilities) > 1:

        failure_probability = (
            probabilities[1]
        )

    else:

        failure_probability = 0.0

    return {
        "failure_prediction":
            int(prediction),

        "failure_probability":
            float(
                failure_probability
            ),
    }


if __name__ == "__main__":

    print(
        "===== MACHINE FAILURE PREDICTION ====="
    )

    print()

    artifact = load_model()

    print(
        "Model features:"
    )

    print(
        artifact["features"]
    )

    print()

    # Example sensor readings.
    #
    # These are only an example of how the
    # prediction function can be called.

    result = predict_failure(
        temperature_celsius=75.0,
        vibration_mm_s=4.5,
        pressure_psi=100.0,
    )

    print(
        "Example prediction:"
    )

    print(
        result
    )