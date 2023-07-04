import logging
import tarfile
from pathlib import Path

import awswrangler as wr
logger = logging.getLogger()


def uncompress_models(compressed_models_path: Path) -> Path:
    with tarfile.open(compressed_models_path, mode='r:gz') as tfile:
        tfile.extractall(compressed_models_path.parent)

    # os.remove(compressed_models_path)
    logger.info('Models uncompress completed.')
    return compressed_models_path.parent / 'artifacts'


def upload_to_datalake(df, args, table_name, table_partitions_keys, database_name):
    datalake_partition = [args[partition] for partition in table_partitions_keys]
    logger.info(f'Writing data to "{table_name}" in partition: {datalake_partition}')

    df[table_partitions_keys] = datalake_partition
    wr.s3.to_parquet(df, dataset=True, mode='overwrite_partitions',
        database=database_name, table=table_name, partition_cols=table_partitions_keys)


def get_exportable_dfs(results):
    table_summary_sections = results['table_summary_sections']
    data_resulting = results['data_resulting']
    data_resulting_fails = results['data_resulting_fails']
    signals_summary = results['signals_summary']

    table_summary_sections = table_summary_sections.rename({
        'section': 'tramo',
        'Grieta Lineal Longitudinal': 'grieta_lineal_longitudinal',
        'Intervalo Lineal Longitudinal': 'intervalo_lineal_longitudinal',
        'Grieta Lineal Transversal': 'grieta_lineal_transversal',
        'Intervalo Lineal Transversal': 'intervalo_lineal_transversal',
        'Piel de Cocodrilo': 'piel_de_cocodrilo',
        'Protuberancia, Bache': 'protuberancia_bache',
        'Otras Fallas': 'otras_fallas',
        'latitude': 'latitud',
        'longitude': 'longitud',
        'end_longitude': 'longitud_final',
        'end_latitude': 'latitud_final',
        'section_distance': 'distancia_tramo'
    }, axis=1)

    data_resulting = data_resulting.rename({
        'section': 'tramo', 'classes': 'clases',
        'class_id': 'id_clase', 'center': 'centro',
        'height': 'altura', 'width': 'base', 'total_area': 'area_total',
        'fail_id_section': 'id_tramo_falla', 'longitude': 'longitud'
    }, axis=1)

    data_resulting_fails = data_resulting_fails.rename({
        'start_coordinate': 'coordenada_inicio',
        'end_longitude': 'longitud_final',
        'classes': 'clases',
        'end_latitude': 'latitude_final',
        'fail_id_section': 'id_tramo_falla',
        'width': 'base',
        'start_latitude': 'latitud_inicio',
        'end_coordenate': 'coordenada_final',
        'start_longitude': 'longitud_inicio',
        'class_id': 'id_clase'
    }, axis=1)

    signals_summary = signals_summary.rename({
        'signal_class_base': 'signal_classes_base',
        'signal_class': 'classes_signal',
        'ID': 'id',
        'signal_class_siames_names': 'signal_classes_siames_names',
        'signal_class_names': 'classes_signal_names',
        'signal_class_siames': 'signal_classes_siames'
    }, axis=1)

    table_summary_sections = table_summary_sections[[
        'tramo', 'grieta_lineal_longitudinal',
        'intervalo_lineal_longitudinal', 'grieta_lineal_transversal',
        'intervalo_lineal_transversal', 'piel_de_cocodrilo',
        'protuberancia_bache', 'otras_fallas', 'latitud', 'longitud',
        'latitud_final', 'longitud_final', 'distancia_tramo'
    ]].reset_index(drop=True)

    data_resulting = data_resulting[[
        'latitude', 'longitud', 'distances', 'ind', 'fotograma', 'tramo',
        'clases', 'ind2', 'scores', 'boxes', 'id_clase', 'area', 'centro',
        'altura', 'base', 'area_total', 'perc_area', 'id_tramo_falla'
    ]].reset_index(drop=True)

    data_resulting_fails = data_resulting_fails[[
        'id_clase', 'clases', 'id_tramo_falla', 'distances', 'coordenada_inicio',
        'latitud_inicio', 'longitud_inicio', 'coordenada_final', 'latitude_final',
        'longitud_final', 'base', 'area', 'boxes'
    ]].reset_index(drop=True)

    signals_summary = signals_summary[[
        'fotogram', 'position_boxes', 'score', 'signal_state', 'signal_classes_siames',
        'signal_classes_base', 'classes_signal','latitude', 'longitude',
         'signal_classes_siames_names', 'classes_signal_names', 'final_classes', 'id'
    ]].reset_index(drop=True)

    data_resulting['id_clase'] = 0
    data_resulting_fails['id_clase'] = 0
    return table_summary_sections, data_resulting, data_resulting_fails, signals_summary
