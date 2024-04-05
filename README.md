# isiteuk

## Installation

```bash
mamba env create -f isiteuk.yml -n isiteuk
```

## Example usage

```bash
conda activate isiteuk
PATH=~/src/singlem/bin:$PATH PYTHONPATH=~/src/singlem ~/src/isiteuk/bin/isiteuk \
    --metapackage ~/m/db/isiteuk/isiteuk-0.0.1.smpkg \
    --output results/isiteuk/20240405 \
    --genome-list data/genome_list_20240315.tsv \
    --threads 64
```
