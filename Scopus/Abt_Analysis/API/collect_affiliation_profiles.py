'''
collect_affiliation_profiles.py

    This script utilizes the ScopusInterface script to populate affiliation profile related CSV files based on API HTML responses.

 Author: VJ Davey
'''

import ScopusInterface as si
import argparse
import sys
from time import sleep
parser = argparse.ArgumentParser(description='''
 Collect profile information where available for a list of author ids
''', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-k','--api_key',help='Elsevier provided API key', required=True)
args = parser.parse_args()

# CSV file set up
profiles=['affiliations']
files={header:open('{}.csv'.format(header),'wa') for header in profiles}
cols={
'affiliations':['affiliation_id','parent_affiliation_id','scopus_author_count','scopus_document_count','affiliation_name','address','city','state','country','postal_code','organization_type']
}
for k in cols.keys():
    files[k].write((",".join(col for col in cols[k]) + "\n").encode('utf8'))

# Collect base affiliation profile information and mapping information from the API
for line in sys.stdin:
    sleep(0.05)
    affiliation_id=line.strip('\n')
    # Collect Affiliation Info
    aff_profile=si.affiliation_retrieval(affiliation_id,args.api_key)
    if aff_profile is None:
        continue
    line=",".join(aff_profile[col] for col in cols['affiliations'])
    files['affiliations'].write((line+"\n").encode('utf8'))
