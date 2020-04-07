'''define a Document class that is populated from the Kaggle json,
methods to parse into sentences, process each sentence into stemmed
tokens, run the word rank algorithm and score each token and sencence'''

import gensim.parsing.preprocessing
from gensim.parsing.preprocessing import remove_stopwords,strip_punctuation2,stem_text
import json
import re
import os
import networkx as nx

gensim.parsing.preprocessing.RE_PUNCT = re.compile('([\\!\\"\\#\\$\\%\\&\\\'\\(\\)\\*\\+\\,\\.\\/\\:\\;\\<\\=\\>\\?\\@\\[\\\\\\]\\^_\\`\\{\\|\\}\\~⁄])+')

def maybeLower(word):
    # return unchanged if word contains non-alphanumerics or more than
    # one capital letter
    numCapitals = 0
    for l in word.strip():
        if not l.isalpha():
            return word
        elif not l.islower():
            numCapitals += 1

        if numCapitals > 1: return word

    return word.lower()


sectionWeights = {'title':10,'abstract':5,'body':1,'results':2,'conclusions':3}

def getSection(text):
    text = text.lower()
    if 'result' in text: return 'results'
    if 'discuss' in text or 'concl' in text: return 'conclusions'
    return 'body'

sentDelim = re.compile('(?<=[\sA-Za-z\])])[.!?](?=\s*[A-Z])')
def parseSentences(text):
    return sentDelim.split(text)

class Sentence(object):

    def __init__(self,text,section):
        self.text = text.strip() # a string
        self.section = section.lower()
        self.tokens = [
            maybeLower(w) for w in
            stem_text(remove_stopwords(strip_punctuation2(self.text))).split()
        ]
        self.numTokens = len(self.tokens)
        self.weight = sectionWeights[self.section]
        

    def scoreWords(self,wordScores,query = None):
        base = self.tokens
        if query is not None:
            base = set(self.tokens) & set(query)
            
        return self.weight*sum(wordScores[t] for t in base if t in wordScores)
    

    def allOrderedPairs(self):
        score = self.weight/self.numTokens
        pairs = []
        for i in range(self.numTokens):
            for j in range(self.numTokens):
                if i >= j: continue
                # word i comes before word j
                pairs.append((self.tokens[i],self.tokens[j],score))

        return pairs

        
class Document(object):

    def __init__(self,path):
        self.data = json.load(open(path))
        self.sentences = []
        self.graph = nx.DiGraph()

        # is there a title?
        if self.data['metadata']['title']:
            for s in parseSentences(self.data['metadata']['title']):
                sentence = Sentence(s,'title')
                if sentence.numTokens > 2: self.sentences.append(sentence)
        
        # is there an abstract?
        if self.data['abstract']:
            for span in self.data['abstract']:
                for s in parseSentences(span['text']):
                    sentence = Sentence(s,'abstract')
                    if sentence.numTokens > 2: self.sentences.append(sentence)

        # text body
        for span in self.data['body_text']:
            for s in parseSentences(span['text']):
                sentence = Sentence(s,getSection(span['section']))
                if sentence.numTokens > 2: self.sentences.append(sentence)


    def buildGraph(self):
        for s in self.sentences:
            for a,b,score in s.allOrderedPairs():
                self.graph.add_edge(a,b)
                if 'weight' in self.graph[a][b]:
                    self.graph[a][b]['weight'] += score
                else:
                    self.graph[a][b]['weight'] = score


    def scoreWords(self):
        self.buildGraph()
        # compute pagerank scores
        self.ranks = nx.pagerank_numpy(self.graph)

