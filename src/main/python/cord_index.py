import csv

# Keys for the columns with ID values we are interested in.
CORD_UID = 'cord_uid'
PMCID = 'pmcid'
SHA = 'sha'

class CordIndex(object):
    '''
    Parses the metadata.csv file included with each CORD-19 dataset and
    provides mappings between the various ID types.  Currently only the
    CORD-UID, SHA, and PMCID are supported.  The DOI and PMID are ignored
    for now.
    '''
    def __init__(self, metadata_path):
        self.uid_index = dict()
        self.sha_index = dict()
        self.pmcid_index = dict()
        print("Loading metadata from " + metadata_path)
        with open(metadata_path, 'r') as csv_file:
            # csv.reader(csv_file).next()
            rows = list(csv.reader(csv_file))
            keys = rows[0]
            for line in rows[1:]:
                record = dict()
                for key, value in zip(keys, line):
                    record[key] = value
                self.add_to_index(record, CORD_UID)
                self.add_to_index(record, SHA)
                self.add_to_index(record, PMCID)
        print("Loaded {} records".format(len(self.pmcid_index)))

    def add_to_index(self, record, column):
        key = record[column]
        if key != '':
            if column == CORD_UID:
                self.uid_index[key] = record
            elif column == PMCID:
                self.pmcid_index[key] = record
            elif column == SHA:
                self.sha_index[key] = record
            else:
                raise KeyError("{} is not a valid column name".format(column))

    def get_by_cord_uid(self, id):
        return self.uid_index[id]

    def get_by_pmcid(self, id):
        return self.pmcid_index[id]

    def get_by_sha(self, id):
        return self.sha_index[id]

    def size(self):
        return len(self.pmcid_index)

    def print_sizes(self):
        print("UID: {}".format(len(self.uid_index)))
        print("SHA: {}".format(len(self.sha_index)))
        print("PMC: {}".format(len(self.pmcid_index)))
