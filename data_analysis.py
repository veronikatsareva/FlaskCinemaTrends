# импорт и установка необходимых модулей

from pymystem3 import Mystem
from pymorphy2 import MorphAnalyzer
import nltk
from nltk.collocations import *
from transformers import pipeline

nltk.download("stopwords")
from nltk.corpus import stopwords

russian_stopwords = set(stopwords.words("russian"))
english_stopwords = set(stopwords.words("english"))


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


# функция для подсчета статистики по NER
def ner_stats(data):
    # модель для классификации именованных сущностей
    ner_classifier = pipeline("ner", model="Babelscape/wikineural-multilingual-ner")

    # словарь для статистики
    ner_stats = {}

    for text in data:
        # нахождение именнованных сущностей в тексте
        ner_entities = ner_classifier(text)

        # сбор индексов NER-токенов
        ner_tokens = []
        for ner in ner_entities:
            ner_tokens.append([ner["entity"], ner["start"], ner["end"]])

        # нахождение именнованных сущностей в тексте по индексам токенов
        i = 0
        while i < len(ner_tokens) - 1:
            left = ner_tokens[i][1]
            right = ner_tokens[i][2]
            # поиск границ слова, состоящего из индексов NER-токнов
            while i < len(ner_tokens) - 1 and ner_tokens[i + 1][1] == ner_tokens[i][2]:
                right = ner_tokens[i + 1][2]
                i += 1
            # добавление NER в stats, если оно не входит в стоп-слова
            # русского или английского языков
            ner_word = text[left:right]
            if (
                ner_word.isalpha()
                and ner_word.lower() not in russian_stopwords
                and ner_word.lower() not in english_stopwords
            ):
                if ner_word not in ner_stats:
                    ner_stats[ner_word] = 0
                ner_stats[ner_word] += 1
            i += 1

    return ner_stats
