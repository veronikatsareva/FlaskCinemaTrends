# импорт и установка необходимых модулей

from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
import nltk
from nltk.collocations import *

nltk.download("stopwords")
from nltk.corpus import stopwords

russian_stopwords = set(stopwords.words("russian"))


# функция для препроцессинга текста: удаление стоп-слов и не слов
def preprocess(text):
    preprocessed_text = []
    for word in text:
        if word.isalpha() and word not in russian_stopwords:
            preprocessed_text.append(word)
    return preprocessed_text


# функция для лемматизации текста
def lemmatizer(text):
    mystem = Mystem()
    lemmatized_text = mystem.lemmatize(text)

    preprocessed_text = []
    for word in lemmatized_text:
        if word.isalpha() and word not in russian_stopwords:
            preprocessed_text.append(word)
    return preprocessed_text


# функция для подсчета статистики частей речи
def pos(data):
    pos_dict = {}
    morph = MorphAnalyzer()

    for token in data:
        pos_ = str(morph.parse(token)[0].tag.POS)
        if pos_ not in pos_dict:
            pos_dict[pos_] = 0
        pos_dict[pos_] += 1

    return pos_dict


# функция для поиска биграмм
def bigramms(data):
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(data)

    # топ-10 самых частотных биграмм
    return sorted(finder.nbest(bigram_measures.raw_freq, 10))


# функция для поиска триграмм
def trigramms(data):
    trigram_measures = nltk.collocations.TrigramAssocMeasures()
    finder = TrigramCollocationFinder.from_words(data)

    # топ-10 самых частотных триграмм
    return sorted(finder.nbest(trigram_measures.raw_freq, 10))
