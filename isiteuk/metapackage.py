import json
import os
import logging
import zenodo_backpack

DATA_ENVIRONMENT_VARIABLE = 'ISITEUK_METAPACKAGE_PATH'
DATA_DEFAULT_VERSION = '0.0.1'
# TODO: Update DATA_DOI after uploading the metapackage to Zenodo
DATA_DOI = '10.5281/zenodo.20755874'


def _contents(path):
    contents_path = os.path.join(path, 'CONTENTS.json')
    if not os.path.exists(contents_path):
        return None
    try:
        with open(contents_path) as f:
            return json.load(f)
    except Exception:
        return None


def _is_backpack(path):
    contents = _contents(path)
    return bool(contents) and 'zenodo_backpack_version' in contents


def _is_smpkg(path):
    contents = _contents(path)
    return bool(contents) and 'singlem_metapackage_version' in contents


class Metapackage:
    @staticmethod
    def resolve_path(metapackage_path, version=None):
        if _is_backpack(metapackage_path):
            backpack = zenodo_backpack.acquire(path=metapackage_path, version=version)
            payload = backpack.payload_directory_string()
            if _is_smpkg(payload):
                return payload
            return backpack.payload_directory_string(enter_single_payload_directory=True)
        return metapackage_path

    @staticmethod
    def acquire(metapackage_path, version=None):
        import singlem.metapackage
        return singlem.metapackage.Metapackage.acquire(
            Metapackage.resolve_path(metapackage_path, version=version)
        )

    @staticmethod
    def acquire_default():
        env_path = os.environ.get(DATA_ENVIRONMENT_VARIABLE)
        if env_path is None:
            raise Exception(
                f"No metapackage specified. Either set the {DATA_ENVIRONMENT_VARIABLE} "
                "environment variable, use --metapackage, or run 'isiteuk data' to download."
            )
        version = DATA_DEFAULT_VERSION if _is_backpack(env_path) else None
        return Metapackage.acquire(env_path, version=version)

    @staticmethod
    def download(output_directory=None):
        if not output_directory:
            raise Exception("Must specify an output directory to download the isiteuk metapackage to")
        logging.info(f"Downloading isiteuk metapackage version {DATA_DEFAULT_VERSION} from {DATA_DOI} ...")
        backpack = zenodo_backpack.ZenodoBackpackDownloader().download_and_extract(
            output_directory,
            DATA_DOI,
            progress_bar=True,
        )
        logging.info("Finished downloading data")
        logging.info(f"export {DATA_ENVIRONMENT_VARIABLE}='{os.path.abspath(backpack.base_directory)}'")

    @staticmethod
    def verify(output_directory=None):
        if output_directory is not None:
            raise Exception(
                f"Verification does not take an output directory. "
                f"Set {DATA_ENVIRONMENT_VARIABLE} to the downloaded data location."
            )
        if DATA_ENVIRONMENT_VARIABLE not in os.environ:
            raise Exception(
                f"The {DATA_ENVIRONMENT_VARIABLE} environment variable is not set. "
                "Run 'isiteuk data' to download the metapackage first."
            )
        backpack = zenodo_backpack.acquire(
            env_var_name=DATA_ENVIRONMENT_VARIABLE,
            version=DATA_DEFAULT_VERSION,
        )
        zenodo_backpack.ZenodoBackpackDownloader().verify(backpack)
        logging.info("Metapackage verified successfully.")
