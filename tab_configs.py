
from psycopg2 import sql
from typing import Dict, Any, List, Callable, Union

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

user_book_lists_edit_fields: List[Dict[str, Any]] = [
    {'name': 'status', 'label': 'Статус читання:', 'required': True, 'db_col_name': 'status'}
]


user_book_lists_add_fields: List[Dict[str, Any]] = [
    {
        'name': 'user_id',
        'label': 'Користувач:',
        'type': 'combobox_db',
        'required': True,
        'query': "SELECT user_id, username FROM public.\"user\" ORDER BY username",#
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
        'value_col': 'book_id',
        'display_col': 'title',
        'db_col_name': 'book_id'
    },
    {
        'name': 'status',
        'label': 'Статус читання:',
        'type': 'combobox',
        'required': True,
        'choices_provider': 'get_enum_values_reading_status',
        'db_col_name': 'status'

    }
]

USER_BOOK_LISTS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Списки книг користувачів",
    "tab_object_name": "userBookListsTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_user_book_lists'),
    "search_cols_map": {"Користувач": "Ім'я користувача", "Книга": "Назва книги", "Статус": "Статус читання"},
    "pk_db_col_name": "book_list_id",
    "id_display_col_name_for_sort": "ID",


    "add_dialog_config": {
        'table_name': 'book_list',
        'pk_db_col_name': 'book_list_id',
        'fields': user_book_lists_add_fields
    },

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
    "delete_entity_db_name": "book_list"
}



comments_edit_fields: List[Dict[str, Any]] = [
    {'name': 'comment_text', 'label': 'Текст коментаря:', 'required': True, 'type': 'text_edit', 'db_col_name': 'comment_text'},
]




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
        'name': 'book_id',
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
        'type': 'dynamic_parent_comment_select',
        'depends_on_field': 'book_id',
        'allow_none_text': "— Не відповідати (кореневий коментар) —",
        'db_col_name': 'parent_comment_id',
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
        'fields': [
            {'name': 'comment_text', 'label': 'Текст коментаря:', 'type': 'text_edit', 'required': True, 'db_col_name': 'comment_text'},
        ]
    },
    "delete_entity_db_name": "comment"
}

evaluations_edit_fields: List[Dict[str, Any]] = [
     {'name': 'rate', 'label': 'Оцінка:', 'required': True, 'db_col_name': 'rate'}
]

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
        'value_col': 'book_id',
        'display_col': 'title',
        'db_col_name': 'book_id'
    },
    {
        'name': 'rate',
        'type': 'combobox',
        'required': True,
        'choices_provider': 'get_enum_values_rating_type',
        'db_col_name': 'rate'
    }

]

EVALUATIONS_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Оцінки",
    "tab_object_name": "evaluationsTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_evaluations'),
    "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача, що оцінив", "Оцінка": "Оцінка"},
    "pk_db_col_name": "evaluation_id",
    "id_display_col_name_for_sort": "ID",

    "add_dialog_config": {
        'table_name': 'evaluation',
        'fields': evaluations_add_fields,
        'pk_db_col_name': 'evaluation_id'
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
        'value_col': 'book_id',
        'display_col': 'title',
        'db_col_name': 'book_id'
    },
    {
        'name': 'quote_text',
        'label': 'Текст цитати:',
        'type': 'text_edit',
        'required': True,
        'db_col_name': 'quote_text'
    },
    {
        'name': 'page_reference',
        'label': 'Сторінка (необов\'язково):',
        'type': 'line_edit',
        'db_col_name': 'page_reference'
    }
]

QUOTES_TAB_CONFIG: Dict[str, Any] = {
    "tab_name_display": "Цитати",
    "tab_object_name": "quotesTab",
    "base_query_provider": lambda: sql.SQL('SELECT * FROM public.view_tab_quotes'),
    "search_cols_map": {"Книга": "Назва книги", "Користувач": "Ім'я користувача, що залишив цитату", "Цитата": "Текст цитати"},
    "pk_db_col_name": "quote_id",
    "id_display_col_name_for_sort": "ID",

    "add_dialog_config": {
        'table_name': 'quote',
        'fields': quotes_add_fields,
        'pk_db_col_name': 'quote_id'
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