import re
from pathlib import Path


class InputFile(object):
    def __init__(self, s3_object, filename_regex):
        if not all(s3_object.get(key) is not None for key in ['Key', 'Bucket']):
            raise Exception(f'There is a problem with the file: {s3_object}.')

        self.path = Path(s3_object['Bucket']) / s3_object['Key']

        if not re.search(filename_regex, self.file_name, flags=re.IGNORECASE):
            raise Exception(f'File {self.file_name} in not compatible with {filename_regex} format.')

    @property
    def file_name(self) -> str:
        return self.path.name

    @staticmethod
    def get_s3_uri(path: Path) -> str:
        return 's3://' + path.as_posix()

    @property
    def inputs_s3_uri(self) -> str:
        return self.get_s3_uri(self.path.parent)

    def build_s3_uri_for_ancestor(self, new_child, ancestor=1) -> str:
        return self.get_s3_uri(self.path.parents[ancestor] / new_child)
