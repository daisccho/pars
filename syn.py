from ru_synonyms import AntonymsGraph, SynonymsGraph
from itertools import islice

# Инициализация графов синонимов и антонимов
sg = SynonymsGraph()
ag = AntonymsGraph()

def find_syn(slovo, text):
    # Получение ввода пользователя
    user_word = slovo

    # Проверяем, есть ли слово в графе
    assert sg.is_in_dictionary(user_word)

    # Получаем список синонимов
    synonyms_list = sg.get_list(user_word)

    # Создаем пустой список для хранения синонимов
    synonyms_result = []

    # Добавляем первые 5 синонимов в список
    for synonym in islice(synonyms_list, 5):
        synonyms_result.append(synonym)

    # Читаем содержимое файла
    content = text

    # Разбиваем текст на слова
    words = content.split()

    # Перебираем синонимы и введенное слово
    for target_word in [user_word] + synonyms_result:
        # Ищем индекс искомого слова
        if target_word in words:
            index = words.index(target_word)

            # Выводим часть текста вокруг искомого слова (например, 10 слов до и 10 слов после)
            start_index = max(0, index - 1)
            end_index = min(len(words), index + 2)

            result_text = ' '.join(words[start_index:end_index])
            return(f'Слово "{target_word}": {result_text}')
        else:
            return(f'Слово "{target_word}" не найдено в тексте.')