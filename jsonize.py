#!/usr/bin/env python3

'''read the pickle objects which contain un-necessary crap, distill to
a couple of dicts and save as json dict with keys that are hashes'''

import json
from glob import glob
import os
import pickle

files = glob(
    os.path.join(os.path.expanduser('~'),'Data','COVID19','**','*pkl'),
    recursive = True
)

import wordRank

data = {}
for idx,f in enumerate(files):
    print(f,idx+1,'out of',len(files))
    doc = pickle.load(open(f,'rb'))
    data[doc.data['paper_id']] = {
        'sentences':[
            {'text':s.text,'tokens':s.tokens,'section':s.section}
            for s in doc.sentences
        ],
        'scores':doc.ranks,
        'metadata':doc.data['metadata'],
    }

json.dump(data,open('allPapers.json','w'))
