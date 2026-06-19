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

ISITEUK_CMD = [sys.executable, '-m', 'isiteuk.main']

EXPECTED_HEADER = 'genome\tdomain\tnum_in_target_domain\tnum_not_in_target_domain'


def _is_zenodo_backpack(path):
    import json
    contents = os.path.join(path, 'CONTENTS.json')
    if not os.path.exists(contents):
        return False
    try:
        with open(contents) as f:
            return 'zenodo_backpack_version' in json.load(f)
    except Exception:
        return False


def _resolve_metapackage():
    """Return the path to the .smpkg, unwrapping a zenodo backpack if needed."""
    from isiteuk.metapackage import DATA_ENVIRONMENT_VARIABLE
    import zenodo_backpack

    env_path = os.environ.get(DATA_ENVIRONMENT_VARIABLE)
    candidates = [p for p in [env_path, DEFAULT_METAPACKAGE] if p]

    for path in candidates:
        if not os.path.isdir(path):
            continue
        if _is_zenodo_backpack(path):
            backpack = zenodo_backpack.acquire(path=path)
            return backpack.payload_directory_string(enter_single_payload_directory=True)
        return path

    return None


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


def _parse_output(content):
    """Parse isiteuk TSV output into {genome: {domain: total_hits}}."""
    result = {}
    for line in content.splitlines()[1:]:  # skip header
        parts = line.split('\t')
        if len(parts) < 4:
            continue
        genome, domain, in_target, not_in_target = parts[0], parts[1], parts[2], parts[3]
        if not domain:
            continue
        result.setdefault(genome, {})[domain] = float(in_target) + float(not_in_target)
    return result


def _dominant_domain(hits_by_domain):
    """Return the domain with the most total hits."""
    return max(hits_by_domain, key=hits_by_domain.get)


@pytest.fixture(scope='module')
def metapackage():
    from isiteuk.metapackage import DATA_ENVIRONMENT_VARIABLE
    path = _resolve_metapackage()
    if path is None:
        pytest.skip(
            f'Metapackage not found. Set {DATA_ENVIRONMENT_VARIABLE} to a zenodo backpack '
            f'directory (after running isiteuk data) or directly to a .smpkg path.'
        )
    return path


@pytest.mark.expensive
class TestProcess:
    def test_bacterial_genome(self, metapackage, tmp_path):
        output = str(tmp_path / 'output.tsv')
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', BACTERIAL_GENOME,
            '--threads', '12',
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
            '--threads', '12',
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
            '--threads', '12',
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
            '--threads', '12',
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            content = f.read()
        assert EXPECTED_HEADER in content

        hits = _parse_output(content)

        bac = hits['GCF_002008365.1_genomic']
        assert 'Bacteria' in _dominant_domain(bac), \
            f'Expected bacterial genome to have most hits in a Bacteria domain, got: {bac}'

        arc = hits['GCA_003139855.1_genomic']
        assert 'Archaea' in _dominant_domain(arc), \
            f'Expected archaeal genome to have most hits in an Archaea domain, got: {arc}'

        euk = hits['binchicken_co8412.34_euk']
        euk_dominant = _dominant_domain(euk)
        assert 'Bacteria' not in euk_dominant and 'Archaea' not in euk_dominant, \
            f'Expected eukaryotic genome dominant domain to be non-prokaryotic, got: {euk}'

    def test_continue_flag(self, metapackage, tmp_path):
        output = str(tmp_path / 'output.tsv')
        # First run: process just the bacterial genome
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', BACTERIAL_GENOME,
            '--threads', '12',
        )
        assert result.returncode == 0, result.stderr

        # Second run: continue and add the archaeal genome
        result = run_isiteuk(
            'process',
            '--metapackage', metapackage,
            '--output', output,
            '--genomes', BACTERIAL_GENOME, ARCHAEAL_GENOME,
            '--continue',
            '--threads', '12',
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
            '--threads', '12',
        )
        assert result.returncode == 0, result.stderr
        with open(output) as f:
            content = f.read()
        assert 'GCF_002008365.1_genomic' in content
        assert 'GCA_003139855.1_genomic' in content
