#!/usr/bin/env python3

'''read the metadata and add DOI links to allPapers.json'''

import pandas as pd

meta = pd.read_csv('/home/leapfrog/Data/COVID19/metadata.csv')

meta.dropna(subset = ['sha','doi'],inplace = True)

dois = dict(zip(meta['sha'],meta['doi']))

import json

data = json.load(open('allPapers.json'))

for sha,record in data.items():
    record['doi'] = dois.get(sha)

json.dump(data,open('allPapers.json','w'))

