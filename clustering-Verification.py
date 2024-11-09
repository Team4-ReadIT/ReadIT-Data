from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib

sentences = ("네이버·KT·카카오 등 토종 클라우드 매출 '성장세'…영업이익 개선은 '과제'", 
"LG유플러스, 매출 늘었지만…영업익 3.2%↓·순이익 13.9%↓")
answer_string = "네이버·KT·카카오 등 토종 클라우드 매출 '성장세'…영업이익 개선은 '과제'"
input_string = "LG유플러스, 매출 늘었지만…영업익 3.2%↓·순이익 13.9%↓"

# Cosine Simillarity
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(sentences)
cos_similar = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
print(cos_similar[0][0])

# Jaccard Simillarity
intersection_cardinality = len(set.intersection(*[set(answer_string), set(input_string)]))
union_cardinality = len(set.union(*[set(answer_string), set(input_string)]))
similar = intersection_cardinality / float(union_cardinality)
print(similar)

# Sequence Matcher
answer_bytes = bytes(answer_string, 'utf-8')
input_bytes = bytes(input_string, 'utf-8')
answer_bytes_list = list(answer_bytes)
input_bytes_list = list(input_bytes)

sm = difflib.SequenceMatcher(None, answer_bytes_list, input_bytes_list)
similar = sm.ratio()
print(similar)
