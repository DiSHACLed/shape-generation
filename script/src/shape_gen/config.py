from pathlib import Path
import os

_I_HAVE_GONE_OVER_THIS_CONFIG = True

assert _I_HAVE_GONE_OVER_THIS_CONFIG, "Please configure the constants in config.py!"

# Using rootless docker?
ROOTLESS = True
if ROOTLESS :
    # If so; change this
    SOCKET = "unix:///run/user/1000/docker.sock"

# HOME_DIR = f"{os.path.expanduser("~")}"
# _BASE = "shape-gen"

# Note this will be broken if you install without --editable
SCRIPT_FOLDER = Path(__file__).resolve().parent.parent.parent.parent 

# make sure these folders exists
VIRTUOSO_DIR = Path(f"{SCRIPT_FOLDER}/virtuoso-dbs")
RESULTS = Path(f"{SCRIPT_FOLDER}/generated-output")
SAMPLE_DATA = Path(f"{SCRIPT_FOLDER}/samples-input")
INTERMEDIATE = Path(f"{SCRIPT_FOLDER}/intermediate")

JAVA_HEAP_SIZE = 32

# make sure these exist
PLAY_JAR=Path(f'{SCRIPT_FOLDER}/external/shacl-play-app-0.12.0-onejar.jar')
QSE_DIR=Path(f'{SCRIPT_FOLDER}/external/qse')
JAVA_BIN=Path(f'{SCRIPT_FOLDER}/external/jdk-17.0.18+8-jre/bin/java')

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
