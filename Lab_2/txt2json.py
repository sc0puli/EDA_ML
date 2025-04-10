import json
import re

def txt_to_json(txt_file_path, json_file_path):
    # Словарь для хранения слов и их индексов
    words_in_titles = {}

    # Чтение .txt файла
    with open(txt_file_path, 'r') as file:
        article_names = [line.strip() for line in file]

    # Обработка каждого названия статьи
    for index, title in enumerate(article_names):
        # Разбиваем название на слова
        words = re.findall(r'\b\w+\b', title.lower())
        for word in words:
            if word not in words_in_titles:
                words_in_titles[word] = []
            words_in_titles[word].append(index)

    # Запись результата в .json файл
    with open(json_file_path, 'w') as json_file:
        json.dump(words_in_titles, json_file)

if __name__ == '__main__':
    txt_file_path = './data/wiki titles no special.txt'
    json_file_path = './data/custom.json'
    txt_to_json(txt_file_path, json_file_path)
