# Sentence level search using the full text of 30k articles

Using [Kaggle's
dataset](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge)
we construct a word graph for every article.  Nodes are words and edge
weights are derived from the co-occurence of words in sentences.  Then
scores are assigned to all words in each article based on the
page-rank analysis of the graph.  Given a query each article is scored
using IDF weighted scores of the words in the query.  Top scoring
sencences are returned as well.  The complete dataset is in
`allPapers.json` while `searchAPI.py` is a Flask app which exposes a
search API endpoint at `http://localhost:5000/search?query=term1+term2+term3`
