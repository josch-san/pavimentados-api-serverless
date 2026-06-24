# Pavimentados API Serverless

A serverless API for road pavement analysis using machine learning inference. The system processes road images and videos to detect pavement conditions, cracks, signals, and other infrastructure features.

## Overview

This project implements a serverless architecture on AWS for processing road pavement data. It uses AWS Lambda, API Gateway, Step Functions, SageMaker, and other services to provide a scalable API for submitting analysis tasks and retrieving results.

## Architecture

The system consists of the following main components:

### API Layer
- **API Gateway**: REST API endpoint with Cognito authentication
- **Task Microservice (Lambda)**: Main API handler for task management

### Processing Pipeline
- **Inference Queue (SQS)**: Receives a message for every submitted task
- **EventBridge Pipe**: Routes queue messages to the inference response workflow (no glue code)
- **Inference Response Workflow (Step Functions)**: Consumes the message and writes a terminal status back to the task. **This is currently a placeholder** (see [Task Processing Flow](#task-processing-flow)) — it returns a simulated result without running SageMaker, and will be replaced by the SageMaker workflow below once that pipeline is wired to the queue.
- **Road Section Inference Workflow (Step Functions)**: The real inference orchestration (not yet wired to the queue)
- **Build Payload (Lambda)**: Prepares input data for SageMaker
- **SageMaker Processing Job**: Runs ML inference in containers (CPU/GPU)
- **Discover Outputs (Lambda)**: Catalogs output files

### Data Storage
- **DynamoDB**: Task metadata and status
- **S3**: Input files (attachments), output results (datalake), artifacts (models)
- **Glue Catalog**: Metadata for parquet files in datalake

### Container Registry
- **ECR**: Docker images for CPU and GPU inference containers

## Key Classes and Components

### Lambda Functions

#### Task Microservice (`src/lambda/task-microservice/`)
- **Main Handler** (`app.py`): APIGatewayRestResolver with router for `/tasks`
- **Controller** (`controllers/task_controller.py`): REST endpoints
  - `GET /tasks`: List tasks
  - `POST /tasks`: Create task
  - `GET /tasks/{taskId}`: Get task details
  - `PUT /tasks/{taskId}`: Update task
  - `POST /tasks/{taskId}/generateAttachmentUploadUrl`: Generate S3 upload URL
  - `POST /tasks/{taskId}/submit`: Submit task for processing
  - `GET /taskTypes`: List available task types
- **Services**:
  - `TaskService`: CRUD operations on tasks
  - `QueueService`: Send messages to SQS
  - `StorageService`: Generate presigned S3 URLs
- **Models**: Task, S3Object data structures

#### Build Payload (`src/lambda/build-payload/`)
- Uses `InferenceBuilder` to prepare SageMaker job parameters from task inputs

#### Discover Outputs (`src/lambda/discover-outputs/`)
- Lists S3 output files and formats for DynamoDB storage

### SageMaker Components

#### Inference Container (`src/sagemaker/road-section-inference/`)
- **Entrypoint** (`entrypoint.py`): Main processing script
- **Container Code** (`sagemaker_container.py`): Argument parsing and utilities
- Supports input types:
  - `video_gps`: Video file with GPS data
  - `image_bundle_gps`: Image bundles with GPS
  - `image_bundle`: Image bundles only
- Uses `pavimentados` library for ML processing
- Outputs: sections, signals_detected, failures_detected, detections_over_photogram

#### ECR Images
- CPU version: `src/ecr/road-section-inference-cpu/Dockerfile`
- GPU version: `src/ecr/road-section-inference-gpu/Dockerfile`

### Step Functions Workflows

#### Road Section Inference Workflow (`src/stepfunctions/RoadSectionInferenceWorkflow.yaml`)
The real ML inference orchestration. **Not currently triggered** — it will replace the
placeholder workflow below once wired to the inference queue.
States:
1. **BuildPayload**: Prepare SageMaker parameters
2. **SetProcessingStatus**: Update task status
3. **InferenceRoadSection**: Run SageMaker processing job
4. **DiscoverOutputs**: Catalog output files
5. **SetCompletedStatus**: Mark task complete
Error handling: **SetFailedStatus** on failures

#### Inference Response Workflow (`src/stepfunctions/InferenceResponseWorkflow.yaml`)
> **Placeholder.** This workflow stands in for the SageMaker pipeline so the end-to-end
> task lifecycle works today. It does **not** run any inference — it simply writes a
> terminal status back to the task, mirroring the real workflow's DynamoDB transitions.
> When the SageMaker pipeline is ready, the EventBridge Pipe target is repointed at
> `RoadSectionInferenceWorkflow` and this workflow (plus the `ForceStatus` testing hook)
> is removed.

It is invoked by the **EventBridge Pipe** for each message on the inference queue.
States:
1. **ParseInput**: Parse the task payload from the SQS message body
2. **SetProcessingStatus**: Update task status to `processing`
3. **ProcessingDelay**: Brief wait so the status transition is observable
4. **EvaluateResult** (Choice): `failed` if `Inputs.ForceStatus == "failed"`, otherwise `completed`
5. **SetCompletedStatus** / **SetFailedStatus**: Write the terminal status and message

### Data Lake
- **Glue Database**: `pavimentados{env}` (e.g., `pavimentados_dev`)
- **Tables**:
  - `sections`: Road section analysis results
  - `signals_detected`: Detected traffic signals
  - `failures_detected`: Pavement failures
  - `detections_over_photogram`: Detailed detections
- Partitioned by: user, geography, task

## Deployment

The project uses AWS SAM for deployment.

### Prerequisites
- AWS CLI configured
- SAM CLI installed
- Docker (for building containers)

### Build and Deploy

1. **Build the application**:
   ```bash
   sam build
   ```

2. **Deploy to development**:
   ```bash
   sam deploy --config-env default
   ```

3. **Deploy to production**:
   ```bash
   sam deploy --config-env prod
   ```

### Parameters
The deployment requires several parameters defined in `samconfig.toml`:
- `UserPoolId`: Cognito user pool ID
- `InfraTableName`: DynamoDB table name
- `AttachmentsBucketName`: S3 bucket for inputs
- `DatalakeBucketName`: S3 bucket for outputs
- `ArtifactsBucketName`: S3 bucket for models
- `ProcessorType`: `cpu` or `gpu`
- `Mode`: `dev`, `test`, or `prod`

## Testing

### Unit Tests
Run unit tests with pytest:
```bash
pytest tests/unit/
```

### Functional Tests
Run functional tests:
```bash
pytest tests/functional/
```

### Local API Testing
Test the API locally using SAM Local:

1. **Start local API**:
   ```bash
   sam local start-api
   ```

2. **Test endpoints** (requires authentication setup)

### AWS Testing
After deployment, test against the deployed API URL (output from `sam deploy`).

### Postman Collection
A ready-to-use collection lives at
[`postman/Pavimentados-Tasks.postman_collection.json`](postman/Pavimentados-Tasks.postman_collection.json).
It exercises the full `/tasks` lifecycle plus `/taskTypes`.

1. **Import**: in Postman, *Import* → select the JSON file.
2. **Set collection variables** (collection → *Variables* tab):
   - `baseUrl`: your deploy URL, e.g. `https://xxxx.execute-api.us-east-1.amazonaws.com/dev` (the `ApiUrl` stack output).
   - `accessToken`: a Cognito **IdToken** (no `Bearer ` prefix). The collection sends it as a bearer token.
   - `taskId`: leave empty — **Create task** captures it automatically into this variable.
3. **Run in order**: List tasks → Create task → Get task → Update task → Generate attachment upload URL → Submit task → List tasks again. After *Submit task*, re-run *Get task by id* a few seconds later to watch the status move to `completed`.
4. **To demo the failed path**: edit the *Create task* body and add `"ForceStatus": "failed"` inside `Inputs`, then run Create → Submit → Get; the task ends as `failed`.

## API Usage

### Authentication
The API uses Cognito User Pool authentication. Include the Authorization header with a valid JWT token.

### Task Lifecycle

1. **Create Task**: `Inputs.Type` selects the input shape — one of `image_bundle`,
   `image_bundle_gps`, or `video_gps`. All shapes require `Geography` and `GeographySource`.
   ```http
   POST /tasks
   {
     "Name": "Road Analysis Task",
     "Description": "Analysis of highway section",
     "Inputs": {
       "Type": "image_bundle",
       "Geography": "Pichincha",
       "GeographySource": "manual"
     }
   }
   ```

2. **Upload Files**: `FieldName` is the attachment field of the chosen input type
   (`ImageBundle`, `VideoFile`, or `GpsFile`). `ArrayLength` applies to array fields
   like `ImageBundle`.
   ```http
   POST /tasks/{taskId}/generateAttachmentUploadUrl
   {
     "FieldName": "ImageBundle",
     "Extension": "zip",
     "ArrayLength": 1
   }
   ```
   Use the returned presigned URL(s) to upload the file(s).

3. **Submit Task** (only allowed from `draft`):
   ```http
   POST /tasks/{taskId}/submit
   ```
   This sets the task to `queued` and enqueues a message on the inference queue.

4. **Check Status** (poll until `completed` or `failed`):
   ```http
   GET /tasks/{taskId}
   ```

5. **List Tasks**:
   ```http
   GET /tasks
   ```

### Task Processing Flow

```
POST /submit ──> set status=queued ──> SQS (inference queue)
                                          │
                                  EventBridge Pipe (batch size 1)
                                          │
                                          ▼
                            Inference Response Workflow (Step Functions, placeholder)
                                          │
                          set status=processing ─> (delay) ─> evaluate
                                          │
                         ┌────────────────┴────────────────┐
                         ▼                                 ▼
                  status=completed                    status=failed
```

> **Placeholder behaviour:** the inference response workflow does not run SageMaker.
> By default a submitted task ends as `completed`. To exercise the failed path, set
> `"ForceStatus": "failed"` inside `Inputs` when creating the task. `ForceStatus` is a
> temporary testing hook and will be removed when the real SageMaker workflow is wired in.

#### SQS Message Contract
On submit, the task microservice sends this JSON body to the inference queue
(`build_event_payload` in `models/base_task.py`):
```json
{
  "Id": "<task uuid>",
  "Name": "Road Analysis Task",
  "AccessLevel": "app",
  "AppServiceSlug": "pavimenta2#road_sections_inference",
  "UserSub": "<cognito sub>",
  "Inputs": { "Type": "image_bundle", "Geography": "Pichincha", "GeographySource": "manual", "...": "..." }
}
```

### Task Statuses
- `draft`: Task created, editable, awaiting files (initial state)
- `queued`: Submitted; message placed on the inference queue
- `processing`: Inference workflow is running
- `completed`: Processing finished successfully
- `failed`: Processing failed
- `requesting`, `canceled`: reserved states defined in the model

### Output Data
Results are stored in the data lake as Parquet files. Access via:
- Athena queries
- Direct S3 access
- Task `Outputs` field contains file references

## Development

### Environment Setup
```bash
# Create conda environment
conda env create -f environment.yml
conda activate pavimentados

# Install dependencies
pip install -e .
```

### Code Structure
- `src/lambda/`: Lambda function code
- `src/sagemaker/`: SageMaker processing code
- `src/ecr/`: Docker images
- `src/stepfunctions/`: Workflow definitions
- `src/apigateway/`: API definitions
- `tests/`: Unit and functional tests

### Key Dependencies
- `aws-lambda-powertools`: Lambda utilities
- `boto3`: AWS SDK
- `pavimentados`: ML processing library (custom)
- `pandas`, `pyarrow`: Data processing