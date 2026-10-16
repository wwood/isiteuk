# isiteuk

isiteuk classifies genomes by domain (Bacteria, Archaea, Eukaryota) using [SingleM](https://github.com/wwood/SingleM) marker genes.

## Installation

### Conda (recommended)

```bash
conda create -c conda-forge -c bioconda --override-channels --name isiteuk isiteuk
conda activate isiteuk
```

### PyPI

```bash
pip install isiteuk
```

This installs the Python package only. Native dependencies (DIAMOND and SingleM's other binaries) must be installed separately — conda is recommended instead.

### GitHub (development)

```bash
git clone https://github.com/wwood/isiteuk
cd isiteuk
pixi shell
isiteuk --help
```

This installs isiteuk and all dependencies (including SingleM) into a managed environment via [pixi](https://pixi.sh).

## Reference data

Download the isiteuk metapackage from Zenodo:

```bash
isiteuk data --output-directory /path/to/isiteuk-data
export ISITEUK_METAPACKAGE_PATH=/path/to/isiteuk-data/isiteuk-backpack-0.0.1
```

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

The `--metapackage` flag can override `ISITEUK_METAPACKAGE_PATH` for a one-off run (a `.smpkg` or the backpack directory from `isiteuk data`):

```bash
isiteuk process \
    --metapackage /path/to/isiteuk-backpack-0.0.1 \
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
