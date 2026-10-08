\# HDL\_Help



Персональная база справочных статей по HDL (Hardware Description Language).

Учебный проект на Python: работа с SQLite, модульная архитектура,

разделение секрета, Windows DPAPI.



\## Идея



Проект собран из независимых модулей-«кубов». Каждый модуль:



\- запускается самостоятельно (`python module.py`);

\- имеет собственный self-test в `if \_\_name\_\_ == "\_\_main\_\_"`;

\- не знает о существовании других модулей;

\- добавляется/удаляется без правки остальных.



Ядро (`hdl\_help\_cli.py`) только склеивает кубы.



\## Модули



| Модуль | Роль |

|---|---|

| `hdl\_db\_store.py`     | хранилище статей и служебных слотов (SQLite) |

| `hdl\_db\_codec.py`     | шифрование и разделение секрета (Fernet + XOR-split) |

| `hdl\_db\_access.py`    | контроль доступа: DPAPI, Windows Hello, HTTP-фактор |

| `hdl\_db\_fallback.py`  | резервный фактор (пароль) |

| `hdl\_db\_hash.py`      | PBKDF2-хеш резервного пароля |

| `hdl\_db\_admin.py`     | добавление / изменение / удаление записей |

| `hdl\_help\_cli.py`     | CLI: список тем, статьи, работа с записями |

| `hdl\_help\_serve.py`   | мини-сервер для отдачи доли по HTTP |



\## Использование



&#x20;   # установка

&#x20;   pip install cryptography winsdk pywin32



&#x20;   # наполнить базу из текстового файла (один раз)

&#x20;   python hdl\_help\_cli.py init secrets.txt



&#x20;   # открытые режимы (справочник)

&#x20;   python hdl\_help\_cli.py list

&#x20;   python hdl\_help\_cli.py show entity



&#x20;   # закрытые режимы (требуют резервный пароль)

&#x20;   python hdl\_help\_cli.py entries

&#x20;   python hdl\_help\_cli.py get github\_token



&#x20;   # администрирование

&#x20;   python hdl\_db\_admin.py add gmail

&#x20;   python hdl\_db\_admin.py set github\_token

&#x20;   python hdl\_db\_admin.py remove test



&#x20;   # сервер доли (в отдельном окне)

&#x20;   python hdl\_help\_serve.py



\## Схема секрета



Ключ шифрования базы разделён на три доли:



&#x20;   S1 → отдаётся HTTP-сервером (vault\_server)

&#x20;   S2 → хранится в SQLite (в слоте help\_metadata)

&#x20;   S3 → хранится в DPAPI-защищённом файле



Только все три вместе восстанавливают ключ. Любые две —

информационно бесполезны (XOR-схема 3-из-3).



\## Что не в репозитории



Файлы `hdl\_help.db`, `hdl\_settings.\*`, `server\_share.bin`,

`server\_token.txt` содержат рабочие секреты и в git не попадают.

См. `.gitignore`.



\## Лицензия



MIT.

