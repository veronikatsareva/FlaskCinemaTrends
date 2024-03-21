# импорт необходимых модулей и файлов

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_apscheduler import APScheduler
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import crawler
import data_analysis
import random

# источник -- https://matplotlib.org/stable/users/explain/figure/backends.html
# без этого код падает при сохранении графиков в png
matplotlib.use("Agg")

app = Flask(__name__)

# источник -- https://docs-python.ru/packages/veb-frejmvork-flask-python/rasshirenie-flask-apscheduler/
# вызов конструктора, который позволит сделать "расписание" по скачиванию
# данных с сайта
scheduler = APScheduler()


# источник -- https://amueller.github.io/word_cloud/auto_examples/a_new_hope.html
# функция для генерации своей палитры цветов в wordcloud
def strawberry_colour_func(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    return "hsl(339, 80%%, %d%%)" % (random.randint(20, 60))


# рендер главной страницы
@app.route("/")
def main():
    return render_template("main.html")


# рендер страницы со статистикой
@app.route("/stats")
def stats():
    try:
        # получение мета-данных из файла
        meta = open("meta.txt", "r").readlines()
        news_amount = meta[0]
        token_amount = meta[1]
        median = meta[2]

        # так как все было записано в файл как строка, в том числе и список
        # из кортежей, функция eval позволяет превратить эти строки
        # обратно в контейнеры
        bigramms = eval(meta[3])
        trigramms = eval(meta[4])
        ner_entities = eval(meta[5])

        content = [news_amount, token_amount, median, bigramms, trigramms, ner_entities]

        return render_template("stats.html", content=content)
    except FileNotFoundError:
        return render_template("error.html")


# функция для подсчета статистики
def data_processing():
    try:
        df = pd.read_csv("data.csv")

        # количество собранных новостей
        news_amount = df.shape[0]

        if news_amount == 0:
            return redirect(url_for("error"))

        # количество собранных токенов
        token_amount = 0
        for text in df["tokenized_text"]:
            token_amount += len(text)

        # создание облака слов из тэгов
        tags_list = []
        for tag in df["tags"]:
            tags_list.append(tag)

        # лемматизация тэгов
        lemmas_tags = data_analysis.lemmatizer(" ".join(tags_list))

        # создание и описание графика
        wordcloud = WordCloud(
            background_color="white",
            width=800,
            height=800,
            color_func=strawberry_colour_func,
        ).generate(" ".join(lemmas_tags))
        plt.figure(figsize=(8, 8), facecolor=None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.title("Облако слов. Тэги")
        plt.savefig("static/wordcloud_tags.png", dpi=300)
        plt.close()

        # массив для хранения длин токенов
        token_avg = []

        # создание облака слов из лемм
        token_list = []
        for token in df["tokenized_text"]:
            token_list.append(token)
            # сбор данных о длинах токенов
            for word in token.split():
                token_avg.append(len(word))

        lemmas_list = data_analysis.lemmatizer(" ".join(token_list))

        # создание и описание графика
        wordcloud = WordCloud(
            background_color="white",
            width=800,
            height=800,
            color_func=strawberry_colour_func,
        ).generate(" ".join(lemmas_list))
        plt.figure(figsize=(8, 8), facecolor=None)
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.title("Облако слов. Леммы")
        plt.savefig("static/wordcloud_lemmas.png", dpi=300)
        plt.close()

        # вызов функции для сбора данных по частеречной разметке
        pos_dict = data_analysis.pos(lemmas_list)

        # отбираем топ-5 частотных частей речи (5 -- это будет other)
        labels = [""] * 5
        sizes = [0] * 5
        idx = 0
        for pos in sorted(pos_dict, key=lambda x: pos_dict[x], reverse=True):
            if idx < 4 and pos != "None":
                labels[idx] = pos
                sizes[idx] = pos_dict[pos]
                idx += 1
            elif idx >= 4 or pos == "None":
                labels[idx] = "Other"
                sizes[idx] += pos_dict[pos]
        plt.pie(
            sizes,
            labels=labels,
            colors=["#e83b4e", "#c60e36", "#a50020", "#840009", "#650000"],
            autopct="%1.1f%%",
        )
        plt.savefig("static/pie_pos.png", dpi=300)
        plt.close()

        # вызов функции для поиска биграмм
        bigramms = data_analysis.bigramms(lemmas_list)

        # вызов функции для поиска триграмм
        trigramms = data_analysis.trigramms(lemmas_list)

        # вызов функции для поиска NER в текстах
        stats = data_analysis.ner_stats(df["text"])
        sorted_ner = []
        for ner in sorted(stats, key=lambda x : stats[x], reverse=True):
            sorted_ner.append(ner)

        # все собранные метаданные
        content = [news_amount, token_amount, np.median(token_avg), bigramms, trigramms, sorted_ner[:20]]

        # запись полученных статистических данных в файл
        meta = open("meta.txt", "w")
        for record in content:
            meta.write(f"{record}\n")
        meta.close()

        return 0

    except FileNotFoundError:
        return 1


# рендер страницы для сбора отзывов о сайте
@app.route("/feedback")
def feedback():
    return render_template("feedback.html")


# функция для сбора отзывов
@app.route("/feedback_collection")
def feedback_collection():
    # открываем файл с отзывами на дозапись
    with open("feedback.txt", "a") as file:
        # записываем сам отзыв + по приколу время, в которое он был отправлен
        file.write(f"{datetime.now()} {request.args['Feedback']}\n")

    # после сбора отзывов рендерим страницу с благодарностью за отзыв
    return render_template("gratitude_feedback.html")


# рендер страницы на случай технических ошибок
@app.route("/error")
def error():
    return render_template("error.html")


# функция для сбора данных с сайта
def data_collection():
    # файл для хранения ошибок
    file = open("errorlog.txt", "a")

    # вызов основной функции для запуска краулера из crawler.py
    df = pd.read_csv("data.csv")
    cinema_news = crawler.main(df.shape[0] // 20 + 1, file)

    # создание датафрейма из полученных данных
    new_df = pd.DataFrame(cinema_news)
    new_df.to_csv("data.csv", mode="a", index=False, header=False)

    # пересчет статистики в связи с новыми данными
    data_processing()

    return 0


if __name__ == "__main__":
    scheduler.add_job(
        id="Data Collection", func=data_collection, trigger="interval", days=2
    )
    scheduler.start()
    app.run()
