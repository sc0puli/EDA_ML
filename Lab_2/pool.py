import math
from functools import reduce
from multiprocessing import Pool
import itertools as it
import os
import sys
import json


from timer import Time
from distance.levenshtein import levenshtein


# путь к файлу с названиями статей Википедии без специальных символов
article_names_path = os.path.join(os.path.dirname(__file__), 'data', 'wiki titles no special.txt')


# сравнение запроса (word) с названием статьи (ref)
def mapper(word, ref):
    # Проверяем разность длин строк
    if abs(len(word) - len(ref)) > 2:
        return ref, 10

    # Сравниваем наборы букв
    word_set = set(word.lower())
    ref_set = set(ref.lower())
    if len(word_set - ref_set) + len(ref_set - word_set) > 2:
        return ref, 10

    # Если оба условия не выполнены, вычисляем редакционное расстояние
    return ref, levenshtein(word, ref, lowercase=True)

# выбор лучшего результата из двух
def reducer(current_ref, new_ref):
    if new_ref[1] < current_ref[1]:
        return new_ref
    return current_ref


# разбиение набора данных на N блоков
def chunkify(refs, N):
    step = int(math.ceil(len(refs) / N))
    inds = list(range(0, len(refs) + step, step))
    for i1, i2 in zip(inds, inds[1:]):
        yield refs[i1:i2]


# обработка одного блока
def chunk_processer(word, refs):
    mapped = map(mapper, it.repeat(word), refs)
    reduced = reduce(reducer, mapped)
    return reduced

# Загрузка данных из файла `words in titles.json`
file_path = os.path.join(os.path.dirname(__file__), 'data', 'words in titles.json')
with open(file_path, 'r') as file:
    words_in_titles = json.load(file)

# основная часть скрипта
# Pool должен использоваться здесь
if __name__ == '__main__':

    # получаем список названий статей без пробельных символов в начале и конце
    with open(article_names_path, 'r') as f:
        article_names = [line.strip() for line in f]

    # задаем слово для поиска или читаем его из командной строки (если передан аргумент)
    word = 'AAAA'
    if len(sys.argv) > 1:
        word = sys.argv[1]

    print(f'Request: {word}\n')

    # ищем ближайшее совпадение последовательно
    # при последующих запусках эту часть лучше закомментировать, чтобы не тратить время
    with Time('Последовательные вычисления'):
        all_words = list(words_in_titles.keys())
        mapped = map(mapper, it.repeat(word), all_words)
        reduced = reduce(reducer, mapped)
    print(reduced)

    # Time считает время выполнения следующего блока и выводит его с комментарием, переданным в качестве аргумента
    # постарался сделать его похожим на директиву %time в Jupyter, это удобнее, чем модуль timeit

    if reduced[0] in words_in_titles:
        # Получаем названия статей, содержащие ближайшее слово
        article_indices = words_in_titles[reduced[0]]
        matching_articles = [article_names[i] for i in article_indices if i < len(article_names)]
        print(f"Статьи, содержащие ближайшее слово: {matching_articles}")
    else:
        print("Ближайшее слово не найдено в словаре.")

    N = 32

    with Time('Параллельные вычисления'):
        # ищем ближайшее совпадение параллельно в N процессах
        # фактически количество одновременно работающих процессов ограничено возможностями процессора
        with Pool(processes=N) as pool:
            name_chunks = list(chunkify(article_names, N))
            mapped = pool.starmap(chunk_processer, zip(it.repeat(word), name_chunks))
            reduced = reduce(reducer, mapped)
    print(reduced)

    if reduced[0] in words_in_titles:
        # Получаем названия статей, содержащие ближайшее слово (параллельный поиск)
        article_indices_parallel = words_in_titles[reduced[0]]
        matching_articles_parallel = [article_names[i] for i in article_indices_parallel if i < len(article_names)]
        print(f"Статьи, содержащие ближайшее слово (параллельный поиск): {matching_articles_parallel}")
    else:
        print("Ближайшее слово не найдено в словаре (параллельный поиск).")