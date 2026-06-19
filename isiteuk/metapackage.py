import os
import logging
import zenodo_backpack

DATA_ENVIRONMENT_VARIABLE = 'ISITEUK_METAPACKAGE_PATH'
DATA_DEFAULT_VERSION = '0.0.1'
# TODO: Update DATA_DOI after uploading the metapackage to Zenodo
DATA_DOI = '10.5281/zenodo.20755874'


class Metapackage:
    @staticmethod
    def acquire_default():
        import singlem.metapackage
        env_path = os.environ.get(DATA_ENVIRONMENT_VARIABLE)
        if env_path is None:
            raise Exception(
                f"No metapackage specified. Either set the {DATA_ENVIRONMENT_VARIABLE} "
                "environment variable, use --metapackage, or run 'isiteuk data' to download."
            )
        # Support both a zenodo backpack directory and a direct .smpkg path
        if os.path.exists(os.path.join(env_path, 'CONTENTS.json')):
            backpack = zenodo_backpack.acquire(path=env_path, version=DATA_DEFAULT_VERSION)
            return singlem.metapackage.Metapackage.acquire(
                backpack.payload_directory_string(enter_single_payload_directory=True)
            )
        else:
            return singlem.metapackage.Metapackage.acquire(env_path)

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
        zenodo_backpack.acquire(
            env_var_name=DATA_ENVIRONMENT_VARIABLE,
            md5sum=True,
            version=DATA_DEFAULT_VERSION,
        )
        logging.info("Metapackage verified successfully.")
