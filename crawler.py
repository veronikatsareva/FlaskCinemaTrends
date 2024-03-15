# импорт и установка необходимых модулей

from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json
import nltk
from nltk import word_tokenize

nltk.download("punkt")


# парсинг одной новости
def post_parsing(post_url, data):
    # делаем запрос по url новости
    req = requests.get(post_url)

    # получаем распарсенный текст запроса
    post = req.text
    post_soup = BeautifulSoup(post, "html.parser")

    # заполняем словарь data данными по новости, проверяя, что они не None

    # заголовок новости
    if post_soup.find("title") != None:
        data["title"].append(post_soup.find("title").text)
    else:
        data["title"].append("None")

    # текст новости
    if post_soup.find("div", {"class": "textart"}) != None:
        data["text"].append(post_soup.find("div", {"class": "textart"}).text)
        data["tokenized_text"].append(
            word_tokenize(post_soup.find("div", {"class": "textart"}).text)
        )
    else:
        data["text"].append("None")
        data["tokenized_text"].append([])

    # url новости
    data["url"].append(post_url)

    # дата и время публикации
    post_date = post_soup.find("div", {"class": "datem"})
    if post_date != None:
        data["year"].append(int(post_date.text.split(" ")[0].split(".")[2]))
        data["month"].append(int(post_date.text.split(" ")[0].split(".")[1]))
        data["day"].append(int(post_date.text.split(" ")[0].split(".")[0]))
        data["hour"].append(int(post_date.text.split(" ")[1].split(":")[0]))
        data["minute"].append(int(post_date.text.split(" ")[1].split(":")[1]))
    else:
        data["year"].append("None")
        data["month"].append("None")
        data["day"].append("None")
        data["hour"].append("None")
        data["minute"].append("None")

    # автор новости
    post_author = post_soup.find("div", {"class": "txtright"})
    if post_author != None:
        data["author"].append(post_author.text)
    else:
        data["author"].append("None")

    # тэги новости
    # (они хранились в мета-данных в json словаре, поэтому пришлось
    # преобразовать суп из мета-данных в словарь и потом уже вытащить
    # оттуда тэги)
    meta = post_soup.find("script", type="application/ld+json")
    if meta != None:
        meta_d = {}
        for elem in meta:
            # strict нужен затем, чтобы код не падал с ошибкой, если
            # попадутся в строке стрёмные спецсимволы
            meta_d.update(json.loads(str(elem), strict=False))
        # с помощью get код не упадет, если ключа не окажется в словаре
        if len(meta_d) != 0:
            data["tags"].append(word_tokenize(" ".join(meta_d.get("about"))))
        else:
            data["tags"].append([])
    else:
        data["tags"].append([])
    return data


# обработка страницы с новостями
def page_parsing(page_number, data, file):
    # создаем url страницы
    # (проблемы только с первой страницей, так как в ссылке на нее
    # не указывается номер, поэтому обрабатываем этот случай отдельно)
    page_url = ""
    if page_number == 1:
        page_url = f"https://www.kinonews.ru/news/"
    elif page_number > 1:
        page_url = f"https://www.kinonews.ru/news_p{page_number}/"

    # делаем запрос по url
    req = requests.get(page_url)

    # получаем распарщенный текст запроса
    page = req.text
    page_soup = BeautifulSoup(page, "html.parser")

    # ищем информацию по новостным постам
    news = page_soup.find_all("div", {"class": "dopblock"})

    # в цикле стоит ограничение на 20, так как на одной
    # странице отображается 20 новостных постов, но помимо
    # них могут дублироваться некоторые внизу в качестве
    # рекламы
    for i in range(20):
        # получаем заголовок одной новости
        title_html = news[i].a

        # создаем url новости
        post_url = "https://www.kinonews.ru" + title_html.get("href")

        # вызываем функцию, которая парсит новость
        try:
            post_parsing(post_url, data)
        except Exception:
            file.write(f"{datetime.now()} error while parsing {post_url}\n")

    return data


# запуск сбора данных, в качестве параметра передаем номер последней
# спарщенной страницы + 1 (так как мы будем постепенно докачивать новости)
def main(page_begin, file):
    # создаем словарь, где будем хранить информацию о всех собранных
    # новостных постах
    data = {
        "title": [],
        "text": [],
        "url": [],
        "year": [],
        "month": [],
        "day": [],
        "hour": [],
        "minute": [],
        "author": [],
        "tags": [],
        "tokenized_text": [],
    }

    # проходимся циклом по страницам
    # будем за раз парсить 5 страниц, что даст нам +100 постов
    for i in range(page_begin, page_begin + 5):
        # вызываем функцию, которая парсит страницу
        try:
            page_parsing(i, data, file)
        except Exception:
            file.write(f"error while parsing page number {i}\n")

    return data
