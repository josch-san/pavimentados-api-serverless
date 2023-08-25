import os
import logging
from pathlib import Path

logger = logging.getLogger()
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logger.setLevel(getattr(logging, LOG_LEVEL))


INPUTS_BASE_PATH = Path(os.environ.get('INPUTS_BASE_PATH', '/opt/ml/processing/inputs'))
OUTPUTS_BASE_PATH = Path(os.environ.get('OUTPUTS_BASE_PATH', '/opt/ml/processing/outputs'))
MODELS_BASE_PATH = Path(os.environ.get('MODELS_BASE_PATH', '/opt/ml/processing/models'))

GPU_ENABLED = os.environ.get('GPU_ENABLED', 'false').lower() == 'true'
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'pavimenta2')
DATALAKE_PARTITIONS_KEYS = ['user', 'geography', 'task']


from pavimentados.processing.processors import MultiImage_Processor
from pavimentados.processing.workflows import Workflow_Processor

from scripts_pavimentados.utils import (
    uncompress_models,
    get_exportable_dfs,
    upload_to_datalake
)

from sagemaker_container import parse_args, unzip


def processing_routine(payload: dict, artifacts_path: Path):
    logger.info('Initializing data inference.')
    ml_processor = MultiImage_Processor(
        assign_devices=True,
        gpu_enabled=GPU_ENABLED,
        total_mem=10 * 1024,
        artifacts_path=artifacts_path.as_posix()
    )

    if payload['type'] == 'video_gps':
        workflow = Workflow_Processor(payload['video_file_path'], image_source_type='video',
            gps_source_type='loc', gps_input=payload['gps_file_path'], adjust_gps=True)

    elif payload['type'] == 'image_bundle':
        for bundle_path in payload['image_bundle_paths']:
            unzip(bundle_path, payload['images_path'])

        workflow = Workflow_Processor(payload['images_path'], image_source_type='image_folder',
            gps_source_type='image_folder', adjust_gps=True)

    elif payload['type'] == 'image_bundle_gps':
        for bundle_path in payload['image_bundle_paths']:
            unzip(bundle_path, payload['images_path'])

        workflow = Workflow_Processor(payload['images_path'], image_source_type='image_folder',
            gps_source_type='loc', gps_input=payload['gps_file_path'], adjust_gps=True)


    results = workflow.execute(ml_processor)
    table_summary_sections, data_resulting, data_resulting_fails, signals_summary = get_exportable_dfs(results)

    logger.info('Completed data inference.')

    upload_to_datalake(table_summary_sections, payload, 'sections', DATALAKE_PARTITIONS_KEYS, DATABASE_NAME)
    table_summary_sections.to_csv((OUTPUTS_BASE_PATH / 'sections.csv').as_posix(), index=False)

    upload_to_datalake(data_resulting, payload, 'detections_over_photogram', DATALAKE_PARTITIONS_KEYS, DATABASE_NAME)
    data_resulting.to_csv((OUTPUTS_BASE_PATH / 'detections_over_photogram.csv').as_posix(), index=False)

    upload_to_datalake(data_resulting_fails, payload, 'failures_detected', DATALAKE_PARTITIONS_KEYS, DATABASE_NAME)
    data_resulting_fails.to_csv((OUTPUTS_BASE_PATH / 'failures_detected.csv').as_posix(), index=False)

    upload_to_datalake(signals_summary, payload, 'signals_detected', DATALAKE_PARTITIONS_KEYS, DATABASE_NAME)
    signals_summary.to_csv((OUTPUTS_BASE_PATH / 'signals_detected.csv').as_posix(), index=False)

    logger.info('Completed results export.')


if __name__ =='__main__':
    args = parse_args(INPUTS_BASE_PATH)

    artifacts_path = uncompress_models(MODELS_BASE_PATH / 'models.tar.gz')
    processing_routine(args, artifacts_path)
