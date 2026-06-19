#!/usr/bin/env python3
"""Create a zenodo_backpack-compatible archive from the isiteuk metapackage.

Usage:
pixi run \
python extras/create_zenodo_backpack.py \
    --metapackage /work/microbiome/db/isiteuk/isiteuk-0.0.1.smpkg \
    --version 0.0.1 \
    --output /work/microbiome/db/isiteuk/isiteuk-0.0.1.smpkg.zb.tar.gz
"""

import argparse
import hashlib
import json
import os
import shutil
import sys
import tarfile
import tempfile


ZENODO_BACKPACK_VERSION = 1
PAYLOAD_DIR_NAME = 'payload_directory'


def md5(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def build_backpack(metapackage_path, version, output_tar):
    metapackage_path = os.path.abspath(metapackage_path)
    metapackage_name = os.path.basename(metapackage_path)
    backpack_dir_name = f'isiteuk-backpack-{version}'

    with tempfile.TemporaryDirectory() as tmpdir:
        backpack_root = os.path.join(tmpdir, backpack_dir_name)
        payload_dir = os.path.join(backpack_root, PAYLOAD_DIR_NAME)
        os.makedirs(payload_dir)

        print(f'Copying {metapackage_path} into backpack payload...')
        dest = os.path.join(payload_dir, metapackage_name)
        shutil.copytree(metapackage_path, dest)

        print('Computing MD5 checksums...')
        md5sums = {}
        for dirpath, _, filenames in os.walk(payload_dir):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                rel_path = '/' + os.path.relpath(full_path, backpack_root)
                md5sums[rel_path] = md5(full_path)
                print(f'  {rel_path}')

        contents = {
            'zenodo_backpack_version': ZENODO_BACKPACK_VERSION,
            'data_version': version,
            'payload_directory': PAYLOAD_DIR_NAME,
            'md5sums': md5sums,
        }
        contents_path = os.path.join(backpack_root, 'CONTENTS.json')
        with open(contents_path, 'w') as f:
            json.dump(contents, f, indent=2)
        print(f'Wrote CONTENTS.json with {len(md5sums)} file checksums')

        print(f'Creating archive {output_tar}...')
        with tarfile.open(output_tar, 'w:gz') as tar:
            tar.add(backpack_root, arcname=backpack_dir_name)

        size_mb = os.path.getsize(output_tar) / 1e6
        print(f'Done: {output_tar} ({size_mb:.1f} MB)')
        print()
        print('Next steps:')
        print('  1. Create a new deposit at https://zenodo.org/uploads/new')
        print(f'  2. Upload {os.path.basename(output_tar)}')
        print(f'  3. Set "Version" metadata field to: {version}')
        print('  4. Publish and copy the concept DOI (the series DOI, not the version DOI)')
        print('  5. Update DATA_DOI in isiteuk/metapackage.py with the concept DOI')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metapackage', required=True,
                        help='Path to the .smpkg directory')
    parser.add_argument('--version', required=True,
                        help='Data version string (e.g. 0.0.1)')
    parser.add_argument('--output', required=True,
                        help='Output .tar.gz path')
    args = parser.parse_args()

    if not os.path.isdir(args.metapackage):
        print(f'Error: {args.metapackage} is not a directory', file=sys.stderr)
        sys.exit(1)

    build_backpack(args.metapackage, args.version, args.output)


if __name__ == '__main__':
    main()
