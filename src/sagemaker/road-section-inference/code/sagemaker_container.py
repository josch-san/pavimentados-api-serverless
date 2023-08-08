import logging
import zipfile
import argparse
from pathlib import Path

logger = logging.getLogger()


def parse_args(inputs_base_path: Path):
    parser = argparse.ArgumentParser()

    parser.add_argument("--task", type=str, required=True)
    parser.add_argument("--user", type=str, required=True)

    parser.add_argument("--type", type=str, required=True)
    parser.add_argument("--geography", type=str, required=True)

    parser.add_argument("--video_file_name", type=str)
    parser.add_argument("--gps_file_name", type=str)
    parser.add_argument("--image_bundle_file_names", nargs='+', type=str)

    payload = vars(parser.parse_args())

    if payload['type'] == 'video_gps':
        payload['video_file_path'] = inputs_base_path / payload.pop('video_file_name')
        payload['gps_file_path'] = inputs_base_path / payload.pop('gps_file_name')

    elif payload['type'] == 'image_bundle_gps':
        payload['gps_file_path'] = inputs_base_path / payload.pop('gps_file_name')
        payload['image_bundle_paths'] = [
            (inputs_base_path / bundle_name) for bundle_name in payload.pop('image_bundle_file_names')
        ]
        payload['images_path'] = inputs_base_path / 'images'

    elif payload['type'] == 'image_bundle':
        payload['image_bundle_paths'] = [
            (inputs_base_path / bundle_name) for bundle_name in payload.pop('image_bundle_file_names')
        ]
        payload['images_path'] = inputs_base_path / 'images'

    else:
        raise Exception(f"Input type {payload['type']} is not available.")

    logger.info(f"Payload: {payload}")
    return payload


def unzip(source_filename: Path, dest_dir: Path):
    with zipfile.ZipFile(source_filename.as_posix()) as zf:
        zf.extractall(dest_dir.as_posix())
