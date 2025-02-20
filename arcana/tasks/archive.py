import os.path
import sys
import tempfile
import tarfile
import zipfile
from pathlib import Path
import attr
from pydra import mark
from pydra.engine.specs import (
    MultiInputObj, MultiOutputObj, File, Directory)
from arcana.core.utils import set_cwd
from arcana.exceptions import ArcanaUsageError


TAR_COMPRESSION_TYPES = ['gz', 'bz2', 'xz']
ZIP_COMPRESSION_TYPES = {
    '': zipfile.ZIP_STORED,
    'zlib': zipfile.ZIP_DEFLATED,
    'bz2': zipfile.ZIP_BZIP2,
    'xz': zipfile.ZIP_LZMA}

@mark.task
@mark.annotate({
    'in_file': MultiInputObj,
    'out_file': str,
    'filter': str,
    'compression': (str, 
                    {'help_string': (
                         f"The type of compression applied to tar file, "
                         "', '".join(TAR_COMPRESSION_TYPES)),
                     'allowed_values': list(TAR_COMPRESSION_TYPES)}),
    'format': str,
    'ignore_zeros': bool,
    'return': {
        'out_file': File}})
def create_tar(in_file, out_file=None, base_dir='.', filter=None,
               compression=None, format=tarfile.DEFAULT_FORMAT,
               ignore_zeros=False, encoding=tarfile.ENCODING):

    if not compression:
        compression = ''
        ext = '.tar'
    else:
        ext = '.tar.' + compression

    if not out_file:
        out_file = in_file[0] + ext

    out_file = os.path.abspath(out_file)

    with tarfile.open(
            out_file, mode=f'w:{compression}', format=format,
            ignore_zeros=ignore_zeros,
            encoding=encoding) as tfile, set_cwd(base_dir):
        for path in in_file:
            tfile.add(relative_path(path, base_dir), filter=filter)

    return out_file


@mark.task
@mark.annotate({'return': {'out_file': MultiOutputObj}})
def extract_tar(in_file: File, extract_dir: Directory, bufsize: int=10240,
                compression_type: str='*'):

    if extract_dir == attr.NOTHING:
        extract_dir = tempfile.mkdtemp()
    else:
        extract_dir = os.path.abspath(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

    if not compression_type:
        compression_type = ''

    with tarfile.open(in_file, mode=f'r:{compression_type}') as tfile:
        tfile.extractall(path=extract_dir)

    return [os.path.join(extract_dir, f) for f in os.listdir(extract_dir)]


@mark.task
@mark.annotate({
    'in_file': MultiInputObj,
    'out_file': str,
    'compression': (str, 
                    {'help_string': (
                         f"The type of compression applied to zip file, "
                         "', '".join(ZIP_COMPRESSION_TYPES)),
                     'allowed_values': list(ZIP_COMPRESSION_TYPES)}),
    'allowZip64': bool,
    'return': {
        'out_file': File}})
def create_zip(in_file, out_file, base_dir, compression='', allowZip64=True,
               compresslevel=None, strict_timestamps=True):

    if out_file == attr.NOTHING:
        out_file = Path(in_file[0]).name + '.zip'

    if base_dir == attr.NOTHING:
        base_dir = Path(in_file[0]).parent

    out_file = os.path.abspath(out_file)

    zip_kwargs = {}
    if not strict_timestamps:  # Truthy is the default in earlier versions
        if sys.version_info.major <= 3 and sys.version_info.minor < 8:
            raise Exception("Must be using Python >= 3.8 to pass "
                            f"strict_timestamps={strict_timestamps!r}")

        zip_kwargs['strict_timestamps'] = strict_timestamps

    with zipfile.ZipFile(
            out_file, mode='w', compression=ZIP_COMPRESSION_TYPES[compression],
            allowZip64=allowZip64, compresslevel=compresslevel,
            **zip_kwargs) as zfile, set_cwd(base_dir):
        for path in in_file:
            path = Path(path)
            if path.is_dir():
                for dpath, _, files in os.walk(path):
                    zfile.write(relative_path(dpath, base_dir))
                    for fname in files:
                        fpath = os.path.join(dpath, fname)
                        zfile.write(relative_path(fpath, base_dir))
            else:
                zfile.write(relative_path(path, base_dir))
    return out_file


@mark.task
@mark.annotate({'return': {'out_file': MultiOutputObj}})
def extract_zip(in_file: File, extract_dir: Directory):

    if extract_dir == attr.NOTHING:
        extract_dir = tempfile.mkdtemp()
    else:
        extract_dir = os.path.abspath(extract_dir)
        os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(in_file) as zfile:
        zfile.extractall(path=extract_dir)

    return [os.path.join(extract_dir, f) for f in os.listdir(extract_dir)]

def relative_path(path, base_dir):
    path = os.path.abspath(path)
    relpath = os.path.relpath(path, base_dir)
    if '..' in relpath:
        raise ArcanaUsageError(
            f"Cannot add {path} to archive as it is not a "
            f"subdirectory of {base_dir}")
    return relpath
