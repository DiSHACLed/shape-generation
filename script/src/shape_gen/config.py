from pathlib import Path
import os

_I_HAVE_GONE_OVER_THIS_CONFIG = True

assert _I_HAVE_GONE_OVER_THIS_CONFIG, "Please configure the constants in config.py!"

# Using rootless docker?
ROOTLESS = True
if ROOTLESS :
    # If so; change this
    SOCKET = "unix:///run/user/1000/docker.sock"

HOME_DIR = f"{os.path.expanduser("~")}"

# make sure these folders exists
_BASE = "shape-gen"
VIRTUOSO_DIR = Path(f"{HOME_DIR}/{_BASE}/virtuoso-dbs")
RESULTS = Path(f"{HOME_DIR}/{_BASE}/results")
SAMPLE_DATA = Path(f"{HOME_DIR}/{_BASE}/sample-data")
INTERMEDIATE = Path(f"{HOME_DIR}/{_BASE}/intermediate")

# Note this will be broken if you install without --editable
SCRIPT_FOLDER = Path(__file__).resolve().parent.parent.parent.parent 
# make sure these exist
PLAY_JAR=Path(f'{SCRIPT_FOLDER}/external/shacl-play-app-0.11.7-onejar.jar')
QSE_DIR=Path(f'{SCRIPT_FOLDER}/external/qse')

NAMESPACES={
    'sh': 'http://www.w3.org/ns/shacl#',
    'vl_besl': 'http://data.vlaanderen.be/ns/besluit#',
    'vl_mand': 'http://data.vlaanderen.be/ns/mandaat#',
    'vl_pers': 'http://data.vlaanderen.be/ns/persoon#',

    'example': 'http://example.com/',
    'mu_core': 'http://mu.semte.ch/vocabularies/core/',

    'mu_ext': 'http://mu.semte.ch/vocabularies/ext/',
    'lblod_org': 'http://lblod.data.gift/vocabularies/organisatie/',
    'lblod_ere': 'http://data.lblod.info/vocabularies/erediensten/',
}

VIRTUOSO_DIR = "/media/koen/big-ssd/data"
RESULTS = "/home/koen/shape-generation-clean/generated-output"
SAMPLE_DATA=Path('/media/koen/big-ssd/sample-data')
INTERMEDIATE=Path('/media/koen/big-ssd/intermediate')