# Лучший гид

|   Cобытие   | Название | Категория | Сложность |
| :---------: | :------: | :-------: | :-------: |
| Student CTF 2024 |  Лучший гид  |  Pwn  |  Medium  |

## Описание

>Правда ли, что можно обойти все достопримечательности Питера всего за 3 дня? -Конечно, нет. Но, в любом случае, с гидом это будет куда быстрее и интереснее, особенно если вы написали его сами)

## Решение

>Скачиваем выданный бинарь, тестим функционал, проверяем с помощью checksec - видим NO PIE, открываем в IDA, видим любезно оставленную нам функцию win, сразу запоминаем адрес.
>Читая бинарь, видим что после освобождения памяти в free_landmark указатель на освобождённый объект в массиве остаётся без изменения => на лицо UAF
>Значит создаём landmark, удаляем его, создаём новый на том же месте, с прыжком на win, и освобождаем его.
>Читаем флажок

### Флаг

```
stctf{Th3_b3S7_gUiD3_1s_Y0UR_Gu1d3}
```
