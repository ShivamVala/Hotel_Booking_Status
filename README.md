# Hotel Reservation Prediction MLOps Project

This project predicts whether a hotel reservation is likely to be cancelled. It includes a complete machine learning workflow: data ingestion from Google Cloud Storage, preprocessing, model training with LightGBM, experiment tracking with MLflow, a FastAPI prediction app, Docker image creation, Jenkins CI/CD, image push to Google Container Registry, and deployment to Google Cloud Run.

## Tech Stack

- Python
- Pandas, NumPy
- Scikit-learn
- Imbalanced-learn SMOTE
- LightGBM
- MLflow
- FastAPI
- Jinja2 templates
- Docker
- Jenkins
- Google Cloud Storage
- Google Container Registry
- Google Cloud Run

## Project Structure

```text
.
+-- app.py                         # FastAPI web app for predictions
+-- config/
|   +-- config.yaml                # Data ingestion and processing config
|   +-- model_params.py            # LightGBM and RandomizedSearchCV params
|   +-- paths_config.py            # Common artifact paths
+-- src/
|   +-- data_ingestion.py          # Downloads data from GCS and splits it
|   +-- data_processing.py         # Cleans, encodes, balances, and selects features
|   +-- model_training.py          # Trains LightGBM and logs to MLflow
|   +-- logger.py                  # Logging setup
|   +-- custom_exception.py        # Custom exception handling
+-- pipeline/
|   +-- training_pipeline.py       # Runs full training pipeline
+-- artifacts/
|   +-- raw/                       # Raw train/test data
|   +-- processed/                 # Processed train/test data
|   +-- models/                    # Trained model file
+-- templates/
|   +-- index.html                 # Prediction form UI
+-- static/
|   +-- style.css                  # UI styling
+-- mlruns/                        # Local MLflow experiment logs
+-- Dockerfile                     # Docker image definition
+-- Jenkinsfile                    # Jenkins CI/CD pipeline
+-- requirements.txt               # Python dependencies
+-- setup.py                       # Package setup
```

## Machine Learning Pipeline

The training pipeline is defined in:

```bash
pipeline/training_pipeline.py
```

It runs the following steps:

1. **Data ingestion**
   - Downloads `Hotel_Reservations.csv` from the configured GCS bucket.
   - Saves raw data under `artifacts/raw/`.
   - Splits data into train and test sets.

2. **Data processing**
   - Drops unnecessary columns.
   - Removes duplicates.
   - Label-encodes categorical columns.
   - Handles skewed numerical columns.
   - Balances the target class using SMOTE.
   - Selects top features using RandomForest feature importance.
   - Saves processed data under `artifacts/processed/`.

3. **Model training**
   - Trains a LightGBM classifier.
   - Uses `RandomizedSearchCV` for hyperparameter tuning.
   - Evaluates accuracy, precision, recall, and F1 score.
   - Saves the trained model to:

```text
artifacts/models/lgbm_model.pkl
```

4. **MLflow tracking**
   - Logs processed datasets.
   - Logs the trained model artifact.
   - Logs model parameters and metrics.

## Configuration

Main configuration is stored in:

```bash
config/config.yaml
```

Current data source:

```yaml
bucket_name: hotel_reservation_data_shivam
bucket_file_name: Hotel_Reservations.csv
```

The train/test split ratio is:

```yaml
train_ratio: 0.8
```

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -e .
```

Make sure your Google Cloud credentials are available before running the training pipeline:

```bash
set GOOGLE_APPLICATION_CREDENTIALS=path\to\service-account-key.json
```

Run the full training pipeline:

```bash
python pipeline/training_pipeline.py
```

## Run the FastAPI App Locally

After training, start the API:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000
```

The app loads the trained model from:

```text
artifacts/models/lgbm_model.pkl
```

## MLflow

This project uses MLflow for experiment tracking.

By default, MLflow logs are stored locally in:

```text
mlruns/
```

To view MLflow locally:

```bash
mlflow ui
```

Then open:

```text
http://localhost:5000
```

Important: GCR and Cloud Run do not automatically provide an MLflow dashboard. If training runs during Docker build, MLflow artifacts are created inside the Docker build environment/image context unless a remote MLflow tracking server is configured.

For online MLflow tracking, configure a remote tracking URI:

```bash
set MLFLOW_TRACKING_URI=http://your-mlflow-server-url
```

or set it in Python before `mlflow.start_run()`.

## Docker

Build the Docker image:

```bash
docker build -t hotel-reservation-app .
```

Run the container:

```bash
docker run -p 8000:8000 hotel-reservation-app
```

Current Docker behavior:

```dockerfile
RUN python pipeline/training_pipeline.py
```

This means the model is trained during Docker image build and saved inside the image.

When the Docker image is pushed to GCR, the trained model inside `artifacts/models/lgbm_model.pkl` is also included in that image.

## Jenkins CI/CD Flow

The Jenkins pipeline performs:

1. Clones the GitHub repository.
2. Creates a Python virtual environment.
3. Installs dependencies.
4. Builds a Docker image.
5. Runs model training during Docker build.
6. Pushes the image to Google Container Registry.
7. Deploys the image to Google Cloud Run.

Image path format:

```text
gcr.io/<GCP_PROJECT>/ml-project:latest
```

Cloud Run service:

```text
ml-project
```

## Retraining Workflow

With the current setup, retraining happens during Docker image build.

If new rows are added to the bucket CSV:

```text
gs://hotel_reservation_data_shivam/Hotel_Reservations.csv
```

then run the Jenkins pipeline again using **Build Now**.

Jenkins will rebuild the Docker image, run the training pipeline, create a new model, push the updated image to GCR, and redeploy Cloud Run.

If only the bucket CSV changed and no code changed, a GitHub push is not required. Triggering Jenkins is enough.

To guarantee retraining when only the bucket data changes, build without Docker cache:

```bash
docker build --no-cache -t gcr.io/<GCP_PROJECT>/ml-project:latest .
```

This is important because Docker may otherwise reuse cached layers and skip the training command.

## Prediction App

The FastAPI app is defined in:

```bash
app.py
```

It accepts reservation details from the HTML form and returns whether the customer is likely to cancel the reservation.

Prediction output:

- `0`: Customer is likely to cancel the reservation.
- `1`: Customer is not likely to cancel the reservation.

## Notes and Improvements

- Training during Docker build works for learning and demonstration, but production systems usually separate training and serving.
- A better production approach is to train the model separately, store it in GCS or MLflow Model Registry, and let Cloud Run only serve predictions.
- Remote MLflow tracking is required if experiment logs need to be visible online.
- Service account credentials should never be committed to GitHub.
- If deploying with Cloud Run, make sure the Docker `CMD` points to the correct FastAPI module.
