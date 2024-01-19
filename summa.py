# -*- coding: utf-8 -*-

from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
# рерайтер
import torch
from transformers import FSMTModel, FSMTTokenizer, FSMTForConditionalGeneration
from transformers import T5ForConditionalGeneration, T5Tokenizer
# тональность
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from googletrans import Translator

text = '''
Губернатор Волгоградской области Андрей Бочаров сегодня, 10 января, лично проинспектировал ход строительства крупного в масштабах всей России молочного комплекса в Калачёвском районе. И с удовлетворением отметил, что стройка вошла в финальный этап. – Волгоградская область выходит на завершающий этап по реализации одного из крупнейших в России инвестпроектов по созданию мегафермы. Проект реализуется с господдержкой, и это требует внимательного к нему отношения. Все, что мы планировали, реализовали. Остаётся совсем немного: 2024 год станет завершающим, – сообщил глава региона. Уже сегодня в стаде будущей мегафермы насчитывается более 9 тысяч голов, более 38 тысяч тонн молока – уровень производства, что составляет треть от всего производства молока в коллективных хозяйствах области. – Одна ферма ежедневно может обеспечить молоком всех детей в области от нуля до семи лет, а это около 147 тысяч человек, – пояснил Андрей Бочаров. Молочный комплекс возводится на базе СП «Донское»: предприятие приступило к реализации амбициозного проекта в 2019 году. На сегодняшний день темпы работ почти на год опережают обозначенные ранее сроки. Как сообщили Volganet.net в пресс-службе администрации Волгоградской области, за 5 лет поэтапно здесь: В 2024 году планируется завершить заключительный этап: построить корпус для содержания нетелей, ветеринарный блок, дополнительные выгульные площадки и зоны хранения кормов. Примечательно, что будущая ферма активно внедряет не только современные инженерные, но и цифровые технологии. Каждая корова состоит на компьютерном учёте – это позволяет вовремя выявлять отклонения в физиологии животного, соблюдать технологии кормления и ухода. Карусели также оборудованы электронной системой, способной определять продуктивность стада, контролировать качество молока и др. К слову, ещё до завершения всего проекта предприятие вышло на уровень производства, в два раза превышающий показатели стартового периода: сегодня они составляют 38 тысяч тонн молока в год. По итогам реализации проекта планируется, что эта цифра возрастет до 40 тысяч тонн в год.
'''

#Суммаризатор
#--------------------------------------------------------------------------
def summarize_text(text):
    # задаем язык и предложения
    LANGUAGE = 'russian'
    SENTENCES_COUNT = 1

    # создаем парсер и суммаризатор
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))

    stemmer = Stemmer (LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    s = ''

    # выводим говно
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        s += str(sentence)

    return s

#---------------------------------------------------------------------------


# ------------------------рерайтер---------------------------------------------------

def paraphrase_text(text):
    MODEL_NAME = 'cointegrated/rut5-base-paraphraser'
    model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
    tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)

    model.eval();

    def paraphrase(text, beams=5, grams=4):
        x = tokenizer(text, return_tensors='pt', padding=True).to(model.device)
        max_size = int(x.input_ids.shape[1] * 1.5 + 10)
        out = model.generate(**x, encoder_no_repeat_ngram_size=grams, num_beams=beams, max_length=max_size)
        return tokenizer.decode(out[0], skip_special_tokens=True)

    return(paraphrase(text))



# --------------------------Тональность-------------------------------------------------
def analyze_sentiment(text):

    def translate_text(text):
        translator = Translator()
        translation = translator.translate(text)
        return translation.text

    translated_text = translate_text(text)

    # Инициализация анализатора тональности
    sia = SentimentIntensityAnalyzer()

    # Текст для анализа
    text = translated_text

    # Анализ тональности
    sentiment_scores = sia.polarity_scores(text)

    # Определение тональности
    if sentiment_scores['compound'] >= 0.05:
        sentiment = "Положительная"
    elif sentiment_scores['compound'] <= -0.05:
        sentiment = "Отрицательная"
    else:
        sentiment = "Нейтральная"

    s = "Тональность текста: " + sentiment

    return s
