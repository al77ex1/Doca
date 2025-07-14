# Sample Document

This is a sample markdown document to test the indexing functionality of Doca.

## Section 1: What is Semantic Search?

Semantic search refers to search algorithms that consider the searcher's intent and the contextual meaning of terms as they appear in the searchable dataspace, rather than focusing solely on the literal matching of query terms.

Unlike traditional keyword-based search engines that look for literal matches of the query terms, semantic search systems aim to understand the context, intent, and conceptual meaning behind the query to provide more relevant results.

## Section 2: Embeddings in NLP

Word embeddings are a type of word representation that allows words with similar meaning to have similar representations. They are a distributed representation for text that is perhaps one of the key breakthroughs for the impressive performance of deep learning methods on challenging NLP problems.

Vector embeddings capture semantic relationships between words by representing them as vectors in a continuous vector space. Words that are semantically similar will be closer to each other in this vector space.

## Section 3: Elasticsearch and Vector Search

Elasticsearch now supports vector fields and vector similarity algorithms, making it possible to implement semantic search using embeddings.

The dense_vector field type in Elasticsearch allows you to index dense vectors of float values and to search on those vectors using the script_score query. This enables you to perform k-nearest neighbor (kNN) search and other vector-based operations.
