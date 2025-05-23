# tab_configs.py
from psycopg2 import sql
from typing import Dict, Any, List, Callable, Union

# --- Authors Tab ---
authors_add_edit_fields: List[Dict[str, Any]] = [
    {'name': 'first_name', 'label': "Ім'я:", 'required': True, 'db_col_name': 'first_name'},
    {'name': 'last_name', 'label': 'Прізвище:', 'required': True, 'db_col_name': 'last_name'}
]
AUTHORS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Автори",
    "tab_object_name": "authorsTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_authors'),
    "search_cols_map": {"Ім'я": "Ім'я Автора", "Прізвище": "Прізвище Автора"},
    "pk_db_col_name": "author_id",
    "id_display_col_name_for_sort": "ID",
    "add_dialog_config": {'table_name': 'author', 'pk_db_col_name': 'author_id', 'fields': authors_add_edit_fields},
    "edit_dialog_config": {'table_name': 'author', 'pk_db_col_name': 'author_id', 'fields': authors_add_edit_fields},
    "delete_entity_db_name": "author"
}



books_add_edit_fields: List[Dict[str, Any]] = [
    {'name': 'title', 'label': 'Назва книги:', 'required': True, 'db_col_name': 'title'},
    {'name': 'selected_authors', 'label': 'Автори:', 'type': 'author_select', 'required': True, 'db_col_name': None},
    {'name': 'isbn', 'label': 'ISBN:', 'db_col_name': 'isbn'},
    {'name': 'genre', 'label': 'Жанр:', 'type': 'combobox','choices_provider': 'get_enum_values_genre', 'required': True, 'db_col_name': 'genre'},
    {'name': 'year_publication', 'label': 'Рік публікації:', 'db_col_name': 'year_publication'},
    {'name': 'annotation', 'label': 'Анотація:', 'type':'text_edit', 'db_col_name': 'annotation'},
    {'name': 'page_number', 'label': 'Кількість сторінок:', 'required': True, 'db_col_name': 'page_number'},
    {'name': 'age_restriction', 'label': 'Вікові обмеження:', 'type': 'combobox',  'choices_provider': 'get_enum_values_age_restriction', 'db_col_name': 'age_restriction'},
    {'name': 'is_archived', 'label': 'Архівована', 'type': 'checkbox', 'required': True, 'db_col_name': 'is_archived'},
]
BOOKS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Книги",
    "tab_object_name": "booksTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_books'),
    "search_cols_map": {"Назва": "Назва книги", "ISBN": "ISBN", "Автор(и)": "Автор(и) книги", "Жанр": "Жанр"},
    "pk_db_col_name": "book_id",
    "id_display_col_name_for_sort": "ID",
    "add_dialog_config": {'table_name': 'book', 'pk_db_col_name': 'book_id', 'fields': books_add_edit_fields},
    "edit_dialog_config": {'table_name': 'book', 'pk_db_col_name': 'book_id', 'fields': books_add_edit_fields},
    "delete_entity_db_name": "book"
}


#
# --- Users Tab ---
users_fields_common_db: List[Dict[str, Any]] = [
    {'name': 'username', 'label': "Ім'я користувача:", 'required': True, 'db_col_name': 'username'},
    {'name': 'email', 'label': 'Пошта:', 'required': True, 'db_col_name': 'email'},
    {'name': 'is_admin', 'label': 'Адміністратор', 'type': 'checkbox', 'db_col_name': 'is_admin'}
]
users_add_fields_dialog: List[Dict[str, Any]] = users_fields_common_db + [
    {'name': 'password', 'label': 'Пароль:', 'required': True, 'db_col_name': 'password'}
]
users_edit_fields_dialog: List[Dict[str, Any]] = users_fields_common_db + [
    {'name': 'password_new', 'label': 'Новий пароль (залиште порожнім, щоб не змінювати):', 'edit_only': True}
]
USERS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Користувачі",
    "tab_object_name": "usersTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_users'),
    "search_cols_map": {"Ім'я": "Ім'я користувача", "Пошта": "Пошта користувача"},
    "pk_db_col_name": "user_id",
    "id_display_col_name_for_sort": "ID",
    "add_dialog_config": {'table_name': 'user', 'pk_db_col_name': 'user_id', 'fields': users_add_fields_dialog},
    "edit_dialog_config": {'table_name': 'user', 'pk_db_col_name': 'user_id', 'fields': users_edit_fields_dialog},
    "delete_entity_db_name": "user"
}

# --- User Book Lists Tab ---
user_book_lists_edit_fields: List[Dict[str, Any]] = [
    {'name': 'status', 'label': 'Статус читання:', 'required': True, 'db_col_name': 'status'}
    # Для QComboBox тут треба буде передати 'choices': ['Планую', 'Читаю', 'Прочитано'] або з БД
]
# USER_BOOK_LISTS_TAB_CONFIG: Dict[str, Any] = {
#     "tab_name_display": "Списки книг користувачів",
#     "tab_object_name": "userBookListsTab",
#     "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_user_book_lists'),
#     "search_cols_map": {"Користувач": "Ім'я користувача", "Книга": "Назва книги", "Статус": "Статус читання"},
#     "pk_db_col_name": "book_list_id",
#     "id_display_col_name_for_sort": "ID",
#     "add_dialog_config": None,
#     "edit_dialog_config": {'table_name': 'book_list', 'pk_db_col_name': 'book_list_id', 'fields': user_book_lists_edit_fields},
#     "delete_entity_db_name": "book_list"
# }
# tab_configs.py
# ... (другие импорты и конфигурации) ...

# --- Вкладка Списки книг користувачів (User Book Lists Tab) ---

# Поля для диалога добавления новой записи в список книг пользователя
user_book_lists_add_fields: List[Dict[str, Any]] = [
    {
        'name': 'user_id',  # Имя поля в диалоге и для data_from_dialog
        'label': 'Користувач:',
        'type': 'combobox_db',  # Тип: выпадающий список, данные из БД
        'required': True,
        # Запрос для получения списка пользователей: ID и имя пользователя
        'query': "SELECT user_id, username FROM public.\"user\" ORDER BY username",#
        'value_col': 'user_id',  # Столбец, значение которого будет реальным ID (хранится в itemData)
        'display_col': 'username',  # Столбец, значение которого будет отображаться пользователю
        'db_col_name': 'user_id'  # Имя столбца в таблице 'book_list' для этого значения
    },
    {
        'name': 'book_id',
        'label': 'Книга:',
        'type': 'combobox_db',
        'required': True,
        # Запрос для получения списка книг: ID и название (только неархивированные)
        'query': "SELECT book_id, title FROM public.book WHERE is_archived = false ORDER BY title",
        'value_col': 'book_id',
        'display_col': 'title',
        'db_col_name': 'book_id'
    },
    {
        'name': 'status',
        'label': 'Статус читання:',
        'type': 'combobox',  # Обычный combobox, варианты из ENUM
        'required': True,
        'choices_provider': 'get_enum_values_reading_status',  # Функция для получения статусов
        'db_col_name': 'status'
        # Поле 'date_added' в таблице 'book_list' имеет DEFAULT CURRENT_DATE,
        # поэтому его не нужно добавлять в форму.
    }
]

USER_BOOK_LISTS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Списки книг користувачів",
    "tab_object_name": "userBookListsTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_user_book_lists'),
    "search_cols_map": {"Користувач": "Ім'я користувача", "Книга": "Назва книги", "Статус": "Статус читання"},
    "pk_db_col_name": "book_list_id",  # Первичный ключ для редактирования/удаления существующих записей
    "id_display_col_name_for_sort": "ID",  # Имя столбца с ID в view_tab_user_book_lists для сортировки

    # Конфигурация для диалога добавления
    "add_dialog_config": {
        'table_name': 'book_list',  # Целевая таблица в БД
        'pk_db_col_name': 'book_list_id',  # Имя первичного ключа (не критично для INSERT, если автоинкремент)
        'fields': user_book_lists_add_fields  # Список полей для диалога
    },

    # Конфигурация для диалога редактирования (можно редактировать только статус существующей записи)
    "edit_dialog_config": {
        'table_name': 'book_list',
        'pk_db_col_name': 'book_list_id',
        'fields': [
            {
                'name': 'status', 'label': 'Статус читання:', 'type': 'combobox', 'required': True,
                'choices_provider': 'get_enum_values_reading_status', 'db_col_name': 'status'
            }
        ]
    },
    "delete_entity_db_name": "book_list"  # Имя таблицы для операции удаления
}

# ... (остальная часть файла tab_configs.py) ...
# USER_BOOK_LISTS_TAB_CONFIG: Dict[str, Any] = {
#     "tab_name_display": "Списки книг користувачів",
#     "tab_object_name": "userBookListsTab",
#     "base_query_provider": lambda: 'SELECT * FROM public.view_tab_user_book_lists',
#     "search_cols_map": {"Користувач": "Ім'я користувача", "Книга": "Назва книги", "Статус": "Статус читання"},
#     "pk_db_col_name": "book_list_id",
#     "id_display_col_name_for_sort": "ID",
#     "add_dialog_config": None,
#     "edit_dialog_config": {'table_name': 'book_list', 'pk_db_col_name': 'book_list_id', 'fields': user_book_lists_edit_fields},
#     "delete_entity_db_name": "book_list"
# }



# --- Comments Tab ---
comments_edit_fields: List[Dict[str, Any]] = [
    {'name': 'comment_text', 'label': 'Текст коментаря:', 'required': True, 'type': 'text_edit', 'db_col_name': 'comment_text'},
]

# comments_add_fields: List[Dict[str, Any]] = [
#     {
#         'name': 'user_id',
#         'label': 'Користувач (автор коментаря):',
#         'type': 'combobox_db',
#         'required': True, # Комментарий должен иметь автора (если не разрешены анонимные)
#         'query': "SELECT user_id, username FROM public.\"user\" ORDER BY username",
#         'value_col': 'user_id',
#         'display_col': 'username',
#         'db_col_name': 'user_id'
#         # Если разрешены анонимные комментарии, 'required': False, и нужно обрабатывать NULL для user_id
#     },
#     {
#         'name': 'book_id',
#         'label': 'Книга:',
#         'type': 'combobox_db',
#         'required': True,
#         'query': "SELECT book_id, title FROM public.book WHERE is_archived = false ORDER BY title", # Комментарии к неархивированным книгам
#         'value_col': 'book_id',
#         'display_col': 'title',
#         'db_col_name': 'book_id'
#     },
#     {
#         'name': 'comment_text',
#         'label': 'Текст коментаря:',
#         'type': 'text_edit', # Многострочное поле для текста комментария
#         'required': True,
#         'db_col_name': 'comment_text'
#     },
#     {
#         # 'name': 'parent_comment_id',
#         # 'label': 'ID батьківського коментаря (до цієї ж книги):',
#         # 'type': 'line_edit', # Пользователь вводит ID числом
#         # 'db_col_name': 'parent_comment_id'
#         'name': 'parent_comment_id',
#         'label': 'Відповідь на коментар (необов\'язково):',
#         'type': 'dynamic_combobox_parent_comment',  # Новый специальный тип
#         'depends_on': 'book_id',  # Указывает, от какого поля зависит этот combobox
#         # 'choices_provider_dynamic' : 'get_parent_comments_for_book' - можно было бы так, но логику встроим в show_input_dialog
#         'db_col_name': 'parent_comment_id',
#         'allow_none': True,  # Разрешить "нет родительского комментария"
#         'none_display_text': "— Не відповідати (кореневий коментар) —"
#         # Для более продвинутого UI здесь мог бы быть поиск/выбор комментария из существующих для данной книги.
#         # Пока что - простое текстовое поле для ввода ID.
#         # Валидацию, что такой parent_comment_id существует и относится к той же книге, можно добавить.
#     }
#     # Поля 'created_at', 'updated_at', 'is_edited' обычно управляются БД (DEFAULT, триггеры)
# ]


# COMMENTS_TAB_CONFIG: Dict[str, Any] = {
#     "tab_name_display": "Коментарі",
#     "tab_object_name": "commentsTab",
#     "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_comments'),
#     "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача коментаря", "Текст": "Текст коментаря"},
#     "pk_db_col_name": "comment_id",
#     "id_display_col_name_for_sort": "ID",
#     "add_dialog_config": None,
#     "edit_dialog_config": {'table_name': 'comment', 'pk_db_col_name': 'comment_id', 'fields': comments_edit_fields},
#     "delete_entity_db_name": "comment"
# }
#
# COMMENTS_TAB_CONFIG: Dict[str, Any] = {
#     "tab_name_display": "Коментарі",
#     "tab_object_name": "commentsTab",
#     "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_comments'),
#     "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача коментаря", "Текст": "Текст коментаря"},
#     "pk_db_col_name": "comment_id", # Это имя для операций редактирования/удаления И ДЛЯ RETURNING
#     "id_display_col_name_for_sort": "ID",
#
#     "add_dialog_config": {
#         'table_name': 'comment',
#         'fields': comments_add_fields,
#         'pk_db_col_name': 'comment_id' # <-- ДОБАВЛЕНО ЗДЕСЬ: Явно указываем имя ПК для RETURNING
#     },
#     "edit_dialog_config": {
#         'table_name': 'comment',
#         'pk_db_col_name': 'comment_id',
#         'fields': [
#             {'name': 'comment_text', 'label': 'Текст коментаря:', 'type': 'text_edit', 'required': True, 'db_col_name': 'comment_text'},
#         ]
#     },
#     "delete_entity_db_name": "comment"
# }

comments_add_fields: List[Dict[str, Any]] = [
    {
        'name': 'user_id',
        'label': 'Користувач (автор коментаря):',
        'type': 'combobox_db',
        'required': True,
        'query': "SELECT user_id, username FROM public.\"user\" ORDER BY username",
        'value_col': 'user_id',
        'display_col': 'username',
        'db_col_name': 'user_id'
    },
    {
        'name': 'book_id', # Это поле будет "ведущим" для parent_comment_id
        'label': 'Книга:',
        'type': 'combobox_db',
        'required': True,
        'query': "SELECT book_id, title FROM public.book WHERE is_archived = false ORDER BY title",
        'value_col': 'book_id',
        'display_col': 'title',
        'db_col_name': 'book_id'
    },
    {
        'name': 'comment_text',
        'label': 'Текст коментаря:',
        'type': 'text_edit',
        'required': True,
        'db_col_name': 'comment_text'
    },
    {
        'name': 'parent_comment_id',
        'label': 'Відповідь на коментар (необов\'язково):',
        'type': 'dynamic_parent_comment_select', # Новый уникальный тип для этого поля
        'depends_on_field': 'book_id',         # Указываем, от какого поля зависит этот QComboBox
        'allow_none_text': "— Не відповідати (кореневий коментар) —", # Текст для опции "без родителя"
        'db_col_name': 'parent_comment_id',
        # 'required': False - поле не обязательное
    }
]

COMMENTS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Коментарі",
    "tab_object_name": "commentsTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_comments'),
    "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача коментаря", "Текст": "Текст коментаря"},
    "pk_db_col_name": "comment_id",
    "id_display_col_name_for_sort": "ID",
    "add_dialog_config": {
        'table_name': 'comment',
        'fields': comments_add_fields,
        'pk_db_col_name': 'comment_id'
    },
    "edit_dialog_config": {
        'table_name': 'comment',
        'pk_db_col_name': 'comment_id',
        'fields': [ # При редактировании комментария, родителя обычно не меняют, только текст
            {'name': 'comment_text', 'label': 'Текст коментаря:', 'type': 'text_edit', 'required': True, 'db_col_name': 'comment_text'},
            # Можно добавить поле для parent_comment_id и в редактирование, если это нужно,
            # но это усложнит логику, т.к. нужно будет подгружать комментарии для той же книги.
            # Пока оставим редактирование только текста.
        ]
    },
    "delete_entity_db_name": "comment"
}

# --- Evaluations Tab ---
evaluations_edit_fields: List[Dict[str, Any]] = [
     {'name': 'rate', 'label': 'Оцінка:', 'required': True, 'db_col_name': 'rate'}
     # Для QComboBox тут треба буде передати 'choices': ['OneStar', 'TwoStars', ...] або з БД
]
# EVALUATIONS_TAB_CONFIG: Dict[str, Any] = {
#     "tab_name_display": "Оцінки",
#     "tab_object_name": "evaluationsTab",
#     "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_evaluations'),
#     "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача, що оцінив", "Оцінка": "Оцінка"},
#     "pk_db_col_name": "evaluation_id",
#     "id_display_col_name_for_sort": "ID",
#     "add_dialog_config": None,
#     "edit_dialog_config": {'table_name': 'evaluation', 'pk_db_col_name': 'evaluation_id', 'fields': evaluations_edit_fields},
#     "delete_entity_db_name": "evaluation"
# }
evaluations_add_fields: List[Dict[str, Any]] = [
    {
        'name': 'user_id',
        'label': 'Користувач (хто оцінює):',
        'type': 'combobox_db',
        'required': True,
        'query': "SELECT user_id, username FROM public.\"user\" ORDER BY username",
        'value_col': 'user_id',
        'display_col': 'username',
        'db_col_name': 'user_id'
    },
    {
        'name': 'book_id',
        'label': 'Книга:',
        'type': 'combobox_db',
        'required': True,
        'query': "SELECT book_id, title FROM public.book WHERE is_archived = false ORDER BY title",
        # Оценки к неархивированным книгам
        'value_col': 'book_id',
        'display_col': 'title',
        'db_col_name': 'book_id'
    },
    {
        'name': 'rate',  # Имя поля соответствует столбцу 'rate' в таблице 'evaluation'
        'label': 'Оцінка:',
        'type': 'combobox',
        'required': True,
        'choices_provider': 'get_enum_values_rating_type',  # Загрузка вариантов из ENUM rating_type
        'db_col_name': 'rate'
    }
    # Поле 'date_rated' имеет DEFAULT CURRENT_DATE в таблице 'evaluation'
]

EVALUATIONS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Оцінки",
    "tab_object_name": "evaluationsTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_evaluations'),
    "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача, що оцінив", "Оцінка": "Оцінка"},
    "pk_db_col_name": "evaluation_id", # Это имя для операций редактирования/удаления И ДЛЯ RETURNING
    "id_display_col_name_for_sort": "ID",

    "add_dialog_config": {
        'table_name': 'evaluation',
        'fields': evaluations_add_fields,
        'pk_db_col_name': 'evaluation_id' # <-- ДОБАВЛЕНО ЗДЕСЬ: Явно указываем имя ПК для RETURNING
    },
    "edit_dialog_config": {
        'table_name': 'evaluation',
        'pk_db_col_name': 'evaluation_id',
        'fields': [
            {'name': 'rate', 'label': 'Оцінка:', 'type': 'combobox', 'required': True, 'choices_provider': 'get_enum_values_rating_type', 'db_col_name': 'rate'}
        ]
    },
    "delete_entity_db_name": "evaluation"
}

# --- Quotes Tab ---
quotes_edit_fields: List[Dict[str, Any]] = [
    {'name': 'quote_text', 'label': 'Текст цитати:', 'required': True, 'type': 'text_edit', 'db_col_name': 'quote_text'},
    {'name': 'page_reference', 'label': 'Сторінка:', 'db_col_name': 'page_reference'},
]
# QUOTES_TAB_CONFIG: Dict[str, Any] = {
#     "tab_name_display": "Цитати",
#     "tab_object_name": "quotesTab",
#     "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_quotes'),
#     "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача, що залишив цитату", "Цитата": "Текст цитати"},
#     "pk_db_col_name": "quote_id",
#     "id_display_col_name_for_sort": "ID",
#     "add_dialog_config": None,
#     "edit_dialog_config": {'table_name': 'quote', 'pk_db_col_name': 'quote_id', 'fields': quotes_edit_fields},
#     "delete_entity_db_name": "quote"
# }
# tab_configs.py
# ...

# --- Вкладка Цитати (Quotes Tab) ---

# Поля для диалога добавления новой цитаты
quotes_add_fields: List[Dict[str, Any]] = [
    {
        'name': 'user_id',
        'label': 'Користувач (хто додав цитату):',
        'type': 'combobox_db',
        'required': True,
        'query': "SELECT user_id, username FROM public.\"user\" ORDER BY username",
        'value_col': 'user_id',
        'display_col': 'username',
        'db_col_name': 'user_id'
    },
    {
        'name': 'book_id',
        'label': 'Книга:',
        'type': 'combobox_db',
        'required': True,
        'query': "SELECT book_id, title FROM public.book WHERE is_archived = false ORDER BY title",
        # Цитаты к неархивированным книгам
        'value_col': 'book_id',
        'display_col': 'title',
        'db_col_name': 'book_id'
    },
    {
        'name': 'quote_text',
        'label': 'Текст цитати:',
        'type': 'text_edit',  # Многострочное поле
        'required': True,
        'db_col_name': 'quote_text'
    },
    {
        'name': 'page_reference',
        'label': 'Сторінка (необов\'язково):',
        'type': 'line_edit',  # Однострочное поле для номера/описания страницы
        'db_col_name': 'page_reference'
    }
    # Поле 'created_at' имеет DEFAULT CURRENT_TIMESTAMP в таблице 'quote'
]

QUOTES_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Цитати",
    "tab_object_name": "quotesTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_quotes'),
    "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача, що залишив цитату", "Цитата": "Текст цитати"},
    "pk_db_col_name": "quote_id", # Это имя для операций редактирования/удаления И ДЛЯ RETURNING
    "id_display_col_name_for_sort": "ID",

    "add_dialog_config": {
        'table_name': 'quote',
        'fields': quotes_add_fields,
        'pk_db_col_name': 'quote_id' # <-- ДОБАВЛЕНО ЗДЕСЬ: Явно указываем имя ПК для RETURNING
    },
    "edit_dialog_config": {
        'table_name': 'quote',
        'pk_db_col_name': 'quote_id',
        'fields': [
            {'name': 'quote_text', 'label': 'Текст цитати:', 'type': 'text_edit', 'required': True, 'db_col_name': 'quote_text'},
            {'name': 'page_reference', 'label': 'Сторінка:', 'type': 'line_edit', 'db_col_name': 'page_reference'}
        ]
    },
    "delete_entity_db_name": "quote"
}