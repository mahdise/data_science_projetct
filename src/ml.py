#!/usr/bin/env python
# coding: utf-8

import numpy as np
import nltk
import string
import json
import pandas as pd

import dill
import pickle

from sklearn.metrics import pairwise_distances
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow_hub as hub


def load_tfidf_model_from_image(img):
    return dill.load(open(img, "rb"))


def load_tfidf_model_from_path(path):
    with open(path) as json_file:
        corpus = json.load(json_file)

    flat_corpus = []
    for pair in corpus:
        flat_corpus.append(pair[0])
        flat_corpus.append(pair[1])

    lemmatizer = nltk.stem.WordNetLemmatizer()
    punctuation_removal = dict((ord(punctuation), None) for punctuation in string.punctuation)

    def preprocess(doc):
        return [lemmatizer.lemmatize(token) for token in
                nltk.word_tokenize(doc.lower().translate(punctuation_removal))]

    word_vectorizer = TfidfVectorizer(tokenizer=preprocess, stop_words='english')

    # TF-IDF vectorising the corpus
    vectorised_flat_corpus = word_vectorizer.fit_transform(pd.DataFrame(flat_corpus)[0].values)

    return {"vectorised_flat_corpus": vectorised_flat_corpus,
            "flat_corpus": flat_corpus,
            "word_vectorizer": word_vectorizer}


def generate_tfidf_response(model, user_input):
    """
    Retrieves the chatbot's answer, depending on the current user_input.
    The selection process uses cosine similarity over tf-idf vectors and
    returns the appropriate answer to the most similar question from the corpus.
    """

    flat_corpus = model["flat_corpus"]
    flat_corpus_qs = flat_corpus[0::2]
    vectorised_flat_corpus = model["vectorised_flat_corpus"]
    word_vectorizer = model["word_vectorizer"]

    vectorised_user_input = word_vectorizer.transform([user_input]).toarray()

    # Calculating cosine distance to the Q's
    cos = 1 - pairwise_distances(vectorised_flat_corpus[0::2],
                                 vectorised_user_input,
                                 metric="cosine")

    # ... If similarity equals zero, the chatbot apparently did not understand the input, at all.
    if cos.max() == 0:
        return None
    else:
        # Position of selected Q in vectorised_flat_corpus[0::2]
        q_idx = cos.argmax()
        # Selected Q's original utterance
        q = flat_corpus_qs[q_idx]

        # Retrieve all answer indeces for the selected Q.
        possible_answer_idxs = [idx for idx, elem in enumerate(flat_corpus_qs) if elem == q]

        # Calculating cosine distance between the possible A's and the user input
        cos = 1 - pairwise_distances(vectorised_flat_corpus[1::2][possible_answer_idxs],
                                     vectorised_user_input,
                                     metric="cosine")
        # Position of selected A in flat_corpus[1::2]
        a_idx = possible_answer_idxs[cos.argmax()]

        return flat_corpus[1::2][a_idx]


def load_embeddings_model_from_image(img_path, model_url):
    """
    Initialises the sentence encoding model and load the corresponding, pickled corpus.
    """

    with open(img_path, 'rb') as pickled_file:
        embedded_corpus = pickle.load(pickled_file)

    sent_embed_model = hub.load(model_url)

    def embed(txt_input):
        return sent_embed_model(txt_input)

    return {"embed": embed,
            "qa_pairs_embedded": embedded_corpus}


def load_embeddings_model_from_path(corpus_path, model_url):
    """
    Initialises the sentence encoding model and the corresponding, embedded corpus.
    """

    with open(corpus_path) as json_file:
        corpus = json.load(json_file)

    sent_embed_model = hub.load(model_url)

    def embed(txt_input):
        return sent_embed_model(txt_input)

    # Vectorising the corpus via sentence embeddings into one unified datastructure of Q and A pairs
    qa_pairs_embedded = [[[elem[0], embed([elem[0]])], [elem[1], embed([elem[1]])]] for elem in corpus]

    return {"embed": embed,
            "qa_pairs_embedded": qa_pairs_embedded}


def generate_embeddings_response(model, user_input):
    """
    Retrieves the chatbot's answer, depending on the current user_input.
    The selection process uses sentence embeddings and returns
    the appropriate answer to the most similar question from the corpus.
    """

    embed = model["embed"]
    qa_pairs_embedded = model["qa_pairs_embedded"]

    user_input_embedded = embed([user_input])

    # Sorting corpus_embedded according to inner product between input and the corpus questions
    ranked_corpus_q = sorted(qa_pairs_embedded,
                             key=lambda elem: np.inner(elem[0][1], user_input_embedded),
                             reverse=True)

    return (np.inner(user_input_embedded, ranked_corpus_q[0][0][1]),
            retrieve_embeddings_answer(model, ranked_corpus_q[0][0][0], user_input_embedded))


def retrieve_embeddings_answer(model, corpus_question, user_input_embedded):
    """
    Retrieves the "most appropriate" answer, calculated
    via sentence embeddings distance between answers and user_input.
    """
    qa_pairs_embedded = model["qa_pairs_embedded"]

    # Retrieving all answers to most similar question from corpus
    answers = list(filter(lambda elem: elem[0][0] == corpus_question, qa_pairs_embedded))

    # Sorting according to similarity between input and answers
    ranked_answers = sorted(answers,
                            key=lambda elem: np.inner(elem[1][1], user_input_embedded),
                            reverse=True)

    return ranked_answers[0][1][0]


def load_lda_model(lda_model_path, count_vectorizer_path, corpus_path):
    """
    Initialising the LDA model and the corresponding corpus.
    """
    # load lda model
    pickle_in = open(lda_model_path,"rb")
    lda = pickle.load(pickle_in)

    # load count vectorizer
    pickle_in = open(count_vectorizer_path,"rb")
    count_vectorizer = pickle.load(pickle_in)

    print("lda model loaded")

    #corpus_path = "../data/docs_preprocessed_topicDistribution_match.csv"
    docs_preprocessed_topics_match = pd.read_csv(corpus_path)

    # calculate topic distributions for the stemmed corpus
    #docs_preprocessed_topics_match_path = generate_docs_preprocessed_topicDistribution_match(lda, count_vectorizer, corpus_path)
    # load the file matching preprocessed docs, docs and topic distributions
    #docs_preprocessed_topics_match = pd.read_csv(docs_preprocessed_topics_match_path)
    
    # convert the topic distribution columns from string into array of float
    docs_preprocessed_topics_match['question_topic_distribution'] = docs_preprocessed_topics_match['question_topic_distribution'].map(lambda distribution: convert_to_array(distribution))
    docs_preprocessed_topics_match['answer_topic_distribution'] = docs_preprocessed_topics_match['answer_topic_distribution'].map(lambda distribution: convert_to_array(distribution))   
    
    return lda, count_vectorizer, docs_preprocessed_topics_match
    

def convert_to_array(entry):
    """
    Convert string entry (describing the topic distribution) to array
    """
    entry = entry.replace('[', '')
    entry = entry.replace(']', '')  
    entry = np.fromstring(entry, dtype=float, sep=' ')
    
    return entry
    

def generate_lda_response(lda_model, count_vectorizer, docs_preprocessed_topics_match, user_input):
    """
    Retrieves the chatbot's answer, depending on the current user_input.
    The selection process uses LDA and returns the appropriate answer 
    to the most similar question from the corpus.
    """
    # vectorize user_input
    x_test = count_vectorizer.transform([user_input])
    
    # generate it's topic distribution
    topic_distribution = lda_model.transform(x_test)

    # find most similar topic distribution from corpus questions
    matchingQuestionIndex = find_most_similar_topic_distribution(topic_distribution[0], 
                                                                 docs_preprocessed_topics_match['question_topic_distribution'])   
    matchingQuestion = docs_preprocessed_topics_match['question'][matchingQuestionIndex]
    
    # find most similar topic distribution from corpus answers (that belong to current question)
    matchingAnswerIndex = find_most_similar_topic_distribution(topic_distribution[0], 
                                                               docs_preprocessed_topics_match[docs_preprocessed_topics_match['question'] == matchingQuestion]['answer_topic_distribution'])
    matchingAnswer = docs_preprocessed_topics_match['answer'][matchingAnswerIndex]
    
    return 0.9, matchingAnswer



def find_most_similar_topic_distribution(input_distribution, corpus_distribution):
    """
    Finds the most similar topic distribution from the corpus to the user input.
    """    
    # convert the dataframe column (each row contains an array) into a numpy array of arrays
    corpus_distribution_array = np.vstack(corpus_distribution)
    
    # initalize the closest document with the first entry
    closest_doc_topic_distribution = corpus_distribution_array[0]
 
    # initialize a data structure keeping track of the currently best fitting (closest) document index for each topic 
    doc_indices = np.empty(closest_doc_topic_distribution.size)
      
    # iterate over number of topics
    for i in range(closest_doc_topic_distribution.size):
               
        # for the current topic, find the best fitting document index
        doc_indices[i] = corpus_distribution_array[:,i].argmax()
               
    # count how many times each document index is most similar to user input
    # format: [local doc_index, count]
    value_counts = np.unique(doc_indices, return_counts=True)   
    
    # get index of all documents that have the maximum count
    suitable_docs_local_indeces = np.argwhere(value_counts[1] == np.max(value_counts[1]))
    suitable_docs = value_counts[0][suitable_docs_local_indeces][:,0]
    
    # make sure, the suitable docs are encoded as integers
    suitable_docs = suitable_docs.astype(int)
    
    # if there are multiple suitable enties, randomly select one of them as final answer (because they are equivalently similar to user input)
    selected_index = 0
    if suitable_docs.shape[0] > 1:
        selected_index = np.random.choice(suitable_docs.shape[0]-1, replace=False)  
    else:
        selected_index = suitable_docs[0]           
        
    # return index in overall corpus    
    return corpus_distribution.index[selected_index]



def generate_docs_preprocessed_topicDistribution_match(lda_model, count_vectorizer, corpus_path):
    """
    Calculates topic distribution for the corpus and stores it in a file with the 
    original documents and their preprocessed version.
    Format:
    question | question_preprocessed | question_topic_distribution | answer | answer_preprocessed |answer_topic_distribution
    """  
    # read the stemmed documents and their original 
    stemmed_docs_docs_map = pd.read_csv(corpus_path)
 
    # drop nan values
    stemmed_docs_docs_map = stemmed_docs_docs_map.dropna()
    
    # caclulate the topic distributions for all preprocessed stemmed documents
    question_docs = count_vectorizer.transform(stemmed_docs_docs_map.question_preprocessed)
    question_docs = lda_model.transform(question_docs)
    
    answer_docs = count_vectorizer.transform(stemmed_docs_docs_map.answer_preprocessed)
    answer_docs = lda_model.transform(answer_docs)
    
    # append the topic distributions to the dataframe
    stemmed_docs_docs_map["question_topic_distribution"] = list(question_docs)
    stemmed_docs_docs_map["answer_topic_distribution"] = list(answer_docs)
    
    # save the dataframe
    path = "../data/docs_preprocessed_topicDistribution_match.csv"
    stemmed_docs_docs_map.to_csv(path)
    
    return path

