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
- **Step Functions Workflow**: Orchestrates the inference process
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

### Step Functions Workflow (`src/stepfunctions/RoadSectionInferenceWorkflow.yaml`)
States:
1. **BuildPayload**: Prepare SageMaker parameters
2. **SetProcessingStatus**: Update task status
3. **InferenceRoadSection**: Run SageMaker processing job
4. **DiscoverOutputs**: Catalog output files
5. **SetCompletedStatus**: Mark task complete
Error handling: **SetFailedStatus** on failures

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

## API Usage

### Authentication
The API uses Cognito User Pool authentication. Include the Authorization header with a valid JWT token.

### Task Lifecycle

1. **Create Task**:
   ```http
   POST /tasks
   {
     "Name": "Road Analysis Task",
     "Description": "Analysis of highway section",
     "Inputs": {
       "type": "video_gps",
       "video_file": "video.mp4",
       "gps_file": "gps.csv"
     }
   }
   ```

2. **Upload Files**:
   ```http
   POST /tasks/{taskId}/generateAttachmentUploadUrl
   {
     "FieldName": "video_file",
     "Extension": "mp4"
   }
   ```
   Use the returned URL to upload the file.

3. **Submit Task**:
   ```http
   POST /tasks/{taskId}/submit
   ```

4. **Check Status**:
   ```http
   GET /tasks/{taskId}
   ```

5. **List Tasks**:
   ```http
   GET /tasks
   ```

### Task Statuses
- `created`: Task created, awaiting files
- `processing`: Inference in progress
- `completed`: Processing finished successfully
- `failed`: Processing failed

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

## Monitoring and Logging

- **CloudWatch**: Logs and metrics
- **X-Ray**: Distributed tracing
- **Step Functions**: Workflow execution monitoring

## Security

- Cognito authentication
- IAM roles with least privilege
- S3 bucket policies
- API Gateway throttling

## Cost Optimization

- Serverless architecture (pay per use)
- Spot instances for SageMaker (if available)
- S3 lifecycle policies for data retention

## Troubleshooting

### Common Issues
- **Deployment failures**: Check IAM permissions and parameter values
- **Inference timeouts**: Increase Lambda timeout or optimize processing
- **S3 access errors**: Verify bucket policies and IAM roles
- **Cognito auth issues**: Check user pool configuration

### Logs
Check CloudWatch logs for Lambda functions and Step Functions executions.
