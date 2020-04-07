#!/usr/bin/env python3

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from smart_open import open
import re
import gensim.parsing.preprocessing
from gensim.parsing.preprocessing import remove_stopwords,strip_punctuation2,stem_text
gensim.parsing.preprocessing.RE_PUNCT = re.compile('([\\!\\"\\#\\$\\%\\&\\\'\\(\\)\\*\\+\\,\\.\\/\\:\\;\\<\\=\\>\\?\\@\\[\\\\\\]\\^_\\`\\{\\|\\}\\~⁄])+')

app = Flask(__name__)
api = Api(app)

import json
papers = json.load(open('allPapers.json.bz2'))

sectionWeights = {'title':0,'abstract':5,'body':1,'results':2,'conclusions':3}

# count the frequencies of all tokens
from collections import defaultdict
docCount = defaultdict(int)
for paper in papers.values():
    for token in paper['scores'].keys():
        docCount[token] += 1

def topPapers(query,numResults = 10):
    # sort by scores weighted by IDF
    return sorted(
        papers.items(),
        key = lambda record: sum(
            record[1]['scores'][term]/docCount[term]
            for term in query
            if term in record[1]['scores']
        ),
        reverse = True
    )[:numResults]


def scoreSentence(sent,query,scores):
    return sectionWeights[sent['section']]*sum(
        scores[t] for t in sent['tokens']
        if t in query and t in scores
    )

    
def topSentences(paperID,query,numResults = 10):
    paper = papers[paperID]
    return sorted(
        paper['sentences'],
        key = lambda sent: scoreSentence(sent,query,paper['scores']),
        reverse = True
    )[:numResults]


parser = reqparse.RequestParser()
parser.add_argument('query')

class Search(Resource):
    def get(self):
        args = parser.parse_args()
        query = stem_text(
            strip_punctuation2(remove_stopwords(args['query']))
        ).split()
        results = []
        for paperID,paper in topPapers(query,10):
            result = {}
            result['title'] = paper['metadata']['title']
            result['doi'] = paper['doi']
            result['sentences'] = [
                s['text'] for s in topSentences(paperID,query,10)
            ]
            results.append(result)

        return results

    
api.add_resource(Search,'/search')

if __name__ == '__main__':
    app.run(debug = True)
