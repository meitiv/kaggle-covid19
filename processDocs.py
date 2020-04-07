#!/usr/bin/env python3

'''given a path to the Kaggle data, process all jsons into picked Document objects'''

import sys
from glob import glob
import os.path

if len(sys.argv) != 2:
    print('Usage:',sys.argv[0],'path_to_Kaggle_data')
    sys.exit(1)


dataPath = os.path.abspath(os.path.expanduser(sys.argv[1]))
    
from wordRank import Document
import pickle

for j in glob(dataPath + '/**/*.json',recursive = True):
    print(j)
    doc = Document(j)
    doc.scoreWords()
    p = j.replace('.json','.pkl')
    pickle.dump(doc,open(p,'wb'))
