## AUTOGLOSS

### Структура базы данных

**таблица** *basic_info*

inx | correct_morph | POS | lemma

**таблица** *correction*

id\_correct\_morph | written\_variants

**таблица** *glosses*

id\_correct\_morph | gloss\_variants

**таблица** *stripped*

id\_correct\_morph | stripped\_correct\_forms | stripped_variants
__________

### HOW TO USE

1. Зайти в папку с autogloss

2. Положить в нее .csv с конкордансом

3. Положить в папку SRCS .textgrid файлы

4. Запустить программу командой **python3 main.py** и следовать инструкциям

__________
### *TO DO:*
 

1. Сохранение оригинальных знаков препинания 

2. перезаполнять расшифровку с помощью слоя морф?

3. делать update базы данных при заливе дополненного конкорданса
