import pytest
import subprocess
import sys
import os

import isiteuk

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
BACTERIAL_GENOME = os.path.join(TEST_DATA_DIR, 'GCF_002008365.1_genomic.fna.gz')
ARCHAEAL_GENOME = os.path.join(TEST_DATA_DIR, 'GCA_003139855.1_genomic.fna.gz')
EUK_GENOME = os.path.join(TEST_DATA_DIR, 'binchicken_co8412.34_euk.fna.gz')

DEFAULT_METAPACKAGE = '/work/microbiome/db/isiteuk/isiteuk-0.0.1.smpkg'
METAPACKAGE = os.environ.get('ISITEUK_METAPACKAGE_PATH', DEFAULT_METAPACKAGE)

ISITEUK_CMD = [sys.executable, '-m', 'isiteuk.main']

EXPECTED_HEADER = 'genome\tdomain\tnum_in_target_domain\tnum_not_in_target_domain'


class TestVersion:
    def test_version(self):
        assert isiteuk.__version__ is not None

    def test_cli_version(self):
        result = subprocess.run(
            ISITEUK_CMD + ['--version'],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        assert isiteuk.__version__ in result.stdout


def run_isiteuk(*args):
    return subprocess.run(
        ISITEUK_CMD + list(args),
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope='module')
def metapackage():
    if not os.path.exists(METAPACKAGE):
        pytest.skip(f'Metapackage not found at {METAPACKAGE}. '
                    f'Set ISITEUK_METAPACKAGE_PATH or run isiteuk data.')
    return METAPACKAGE


@pytest.mark.expensive
class TestProcess:
    def test_bacterial_genome(self, metapackage, tmp_path):
        output = str(tmp_path / 'output.tsv')
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', BACTERIAL_GENOME,
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            lines = f.readlines()
        assert lines[0].rstrip() == EXPECTED_HEADER
        genome_names = [line.split('\t')[0] for line in lines[1:]]
        assert 'GCF_002008365.1_genomic' in genome_names

    def test_archaeal_genome(self, metapackage, tmp_path):
        output = str(tmp_path / 'output.tsv')
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', ARCHAEAL_GENOME,
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            lines = f.readlines()
        assert lines[0].rstrip() == EXPECTED_HEADER
        genome_names = [line.split('\t')[0] for line in lines[1:]]
        assert 'GCA_003139855.1_genomic' in genome_names

    def test_eukaryotic_genome(self, metapackage, tmp_path):
        output = str(tmp_path / 'output.tsv')
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', EUK_GENOME,
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            lines = f.readlines()
        assert lines[0].rstrip() == EXPECTED_HEADER
        genome_names = [line.split('\t')[0] for line in lines[1:]]
        assert 'binchicken_co8412.34_euk' in genome_names

    def test_all_three_genomes(self, metapackage, tmp_path):
        output = str(tmp_path / 'output.tsv')
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', BACTERIAL_GENOME, ARCHAEAL_GENOME, EUK_GENOME,
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            content = f.read()
        assert EXPECTED_HEADER in content
        assert 'GCF_002008365.1_genomic' in content
        assert 'GCA_003139855.1_genomic' in content
        assert 'binchicken_co8412.34_euk' in content

    def test_continue_flag(self, metapackage, tmp_path):
        output = str(tmp_path / 'output.tsv')
        # First run: process just the bacterial genome
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', BACTERIAL_GENOME,
        )
        assert result.returncode == 0, result.stderr

        # Second run: continue and add the archaeal genome
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', BACTERIAL_GENOME, ARCHAEAL_GENOME,
            '--continue',
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            content = f.read()
        assert 'GCF_002008365.1_genomic' in content
        assert 'GCA_003139855.1_genomic' in content

    def test_genome_list_file(self, metapackage, tmp_path):
        genome_list = str(tmp_path / 'genomes.txt')
        output = str(tmp_path / 'output.tsv')
        with open(genome_list, 'w') as f:
            f.write(BACTERIAL_GENOME + '\n')
            f.write(ARCHAEAL_GENOME + '\n')
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genome-list', genome_list,
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            content = f.read()
        assert 'GCF_002008365.1_genomic' in content
        assert 'GCA_003139855.1_genomic' in content
