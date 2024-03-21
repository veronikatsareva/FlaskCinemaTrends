# FlaskCinemaTrends

## Описание проекта
Данный репозиторий –– созданный с использованием Flask сайт, который собирает тексты [новостей про кино](https://www.kinonews.ru/) и предоставляет статистику по собранным текстам.

Сайт доступен по постоянной [ссылке](https://cinematrends.pythonanywhere.com/).

## Структура репозитория
- **app.py** –– файл с основным кодом

- **crawler.py** –– файл с кодом краулера

- **data_analysis.py** –– файл с функциями, которые
    - лемматизируют тексты
    - очищают тексты от стоп-слов
    - собирают статистику по частям речи
    - составляют 2-граммы и 3-граммы

- **data.csv** –– файл с собранными новостями

- **feedback.txt** –– файл с отзывами на сайт

- **error.txt** –– файл для сохранения ошибок, возникших во время работы краулера

- **meta.txt** –– файл для сохранения статистических данных по текстам

- директория **templates** –– папка с html-шаблонами для рендера страниц
    - **base.html** –– шаблон для всех страниц

    - **main.html** –– главная страница

    - **stats.html**  –– страница со собранной статистикой

    - **feedback.html** –– страница для сбора отзывов на сайт

    - **gratitude_feedback.html** – страница с благодарностью за отзыв

    - **error.html** - страница для перенаправление в случае появления каких-то ошибок

- директория **static** –– папка, в которой хранятся изображения графиков

## Установка

Для корректной работы необходимо установить следующие модули:

```bash
pip3 install flask
pip3 install flask_apscheduler
pip3 install pandas
pip3 install matplotlib
pip3 install wordcloud
pip3 install requests
pip3 install bs4
pip3 install nltk
pip3 install pymystem3
pip3 install pymorphy2
pip3 install numpy
pip3 install torch
pip3 install transformers
```
