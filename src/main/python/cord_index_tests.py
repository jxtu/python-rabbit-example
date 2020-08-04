import nose
from cord_index import *

METADATA_FILE = '/var/corpora/covid/2020-06-28/metadata.csv'

SAMPLE_PMCID = ['PMC544965', 'PMC545053', 'PMC546175', 'PMC549431', 'PMC551583', 'PMC554992', 'PMC1054884', 'PMC1072802', 'PMC1072806', 'PMC1072807']

def test_load_metadata():
    index = CordIndex(METADATA_FILE)
    index.print_sizes()

def lookup_by_pmcid():
    index = CordIndex(METADATA_FILE)
    for id in SAMPLE_PMCID:
        record = index.get_by_pmcid(id)
        assert record is not None
        r2 = index.get_by_cord_uid(record[CORD_UID])
        assert r2 is record
        print(r2)

def print_pmcid():
    index = CordIndex(METADATA_FILE)
    ids = ", ".join([ "'{}'".format(id) for id in list(index.pmcid_index.keys())[20:30]])
    print("SAMPLE_PMCID = [{}]".format(ids))


if __name__ == '__main__':
    lookup_by_pmcid()
