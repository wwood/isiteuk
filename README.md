# isiteuk

isiteuk classifies genomes by domain (Bacteria, Archaea, Eukaryota) using [SingleM](https://github.com/wwood/SingleM) marker genes.

## Installation

### Pixi (recommended)

After installing [pixi](https://pixi.sh), enter a pixi shell and check that isiteuk is available:

```bash
cat >pixi.toml <<EOL
[workspace]
authors = ["Ben Woodcroft <possibly@somewhere.com>"]
channels = ["conda-forge", "bioconda"]
name = "isiteuk"
platforms = ["linux-64"]
version = "0.1.0"

[dependencies]
isiteuk = "*"
EOL

pixi shell
isiteuk --help
```

### Conda (recommended)

```bash
conda create -c conda-forge -c bioconda --override-channels --name isiteuk isiteuk
conda activate isiteuk
```

### PyPI

```bash
pip install isiteuk
```

This installs the Python package only. Native dependencies (DIAMOND and other binary dependencies of SingleM) must be installed separately — [pixi](https://pixi.sh) or conda is recommended instead.

### GitHub (development)

```bash
git clone https://github.com/wwood/isiteuk
cd isiteuk
pixi shell
isiteuk --help
```

This installs isiteuk and all dependencies (including SingleM) into a managed environment via [pixi](https://pixi.sh).

## Reference data

Download the isiteuk metapackage (`isiteuk-0.0.1.smpkg`) with:

```bash
$ isiteuk data --output-directory /path/to/isiteuk-data
2026/10/16 03:28:06 PM INFO: Downloading isiteuk metapackage version 0.0.1 from 10.5281/zenodo.20755874 ...
2026/10/16 03:28:12 PM INFO: Downloading https://zenodo.org/api/records/20755875/files/isiteuk-0.0.1.smpkg.zb.tar.gz/content to out/isiteuk-0.0.1.smpkg.zb.tar.gz.
100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 973M/973M [12:56<00:00, 1.25MiB/s]
2026/10/16 03:41:11 PM INFO: Extracting files from archive...
2026/10/16 03:41:49 PM INFO: Verifying version and checksums...
2026/10/16 03:42:02 PM INFO: Verification success.
2026/10/16 03:42:02 PM INFO: Finished downloading data
2026/10/16 03:42:02 PM INFO: export ISITEUK_METAPACKAGE_PATH='/path/to/isiteuk-data/isiteuk-0.0.1'
```
Then follow the instructions from the final line of above. Set the environment variable so that this data is used automatically, by adding the following to your .bashrc file. Note that this export can point either to the extracted directory or to the `.smpkg` file within the `payload_directory`.
```
export ISITEUK_METAPACKAGE_PATH=/path/to/isiteuk-data/isiteuk-0.0.1
```

Or download it manually from https://doi.org/10.5281/zenodo.20755874.

Add the `export` line to your `.bashrc` or equivalent to avoid repeating it. To verify the download:

```bash
isiteuk data --verify-only
```

## Usage

### Classify genomes

```bash
isiteuk process \
    --output results.tsv \
    --genome-list genomes.txt \
    --threads 64
```

Or pass genomes directly:

```bash
isiteuk process \
    --output results.tsv \
    --genomes genome1.fna.gz genome2.fna.gz \
    --threads 64
```

The `--metapackage` flag can override `ISITEUK_METAPACKAGE_PATH` for a one-off run:

```bash
isiteuk process \
    --metapackage /path/to/isiteuk-0.0.1.smpkg \
    --output results.tsv \
    --genomes genome1.fna.gz
```

To resume an interrupted run:

```bash
isiteuk process --continue \
    --output results.tsv \
    --genome-list genomes.txt
```

### Output format

Tab-separated file with one row per genome per domain detected:

| genome | domain | num_in_target_domain | num_not_in_target_domain |
|--------|--------|---------------------|--------------------------|
| genome1 | d__Bacteria | 14.2 | 0.0 |
| genome2 | d__Eukaryota | 8.7 | 1.3 |

## Running tests

Quick tests (no metapackage required):

```bash
pixi run test
```

Full integration tests (requires `ISITEUK_METAPACKAGE_PATH` to be set):

```bash
pixi run test-expensive
```

Run a single integration test by name (also requires the metapackage):

```bash
pixi run run-a-test test_bacterial_genome
```
