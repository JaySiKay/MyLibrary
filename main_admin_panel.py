# main_admin_panel.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QLabel, QStatusBar, QMessageBox,
    QLineEdit, QDialogButtonBox, QSplitter, QListWidget, QTextEdit, QListWidgetItem,
    QFormLayout, QAbstractItemView, QHeaderView, QCheckBox, QDateEdit
)
from PyQt6.QtCore import Qt, QTimer, QDate
from PyQt6.QtGui import QFont
import psycopg2
from psycopg2 import sql, extras
from typing import List, Dict, Any, Callable, Optional, Union

from db_config import DB_CONFIG, SPECIAL_QUERIES
from ui_utils import create_standard_table, show_input_dialog
from tab_configs import (
    AUTHORS_TAB_CONFIG, BOOKS_TAB_CONFIG, USERS_TAB_CONFIG,
    USER_BOOK_LISTS_TAB_CONFIG, COMMENTS_TAB_CONFIG,
    EVALUATIONS_TAB_CONFIG, QUOTES_TAB_CONFIG
)


class AdminPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Панель Адміністратора")
        self.setGeometry(50, 50, 1400, 900)

        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cur: Optional[psycopg2.extensions.cursor] = None

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Не підключено")
        self.status_label.setObjectName("StatusLabel")
        self.status_bar.addWidget(self.status_label)

        self.search_timers: Dict[str, QTimer] = {}

        self.connect_to_db()

        if self.conn and self.cur:
            self.init_ui_tabs()

        self.apply_styles()

    def apply_styles(self):
        try:
            with open("styles.qss", "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Файл styles.qss не знайдено. Використовуються стилі за замовчуванням.")
        except Exception as e:
            print(f"Помилка завантаження стилів: {e}")

    def connect_to_db(self):
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            if self.conn:
                self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                print(f"DEBUG: Cursor created: {self.cur}, closed: {self.cur.closed if self.cur else 'N/A'}")
            self.status_label.setText(f"Підключено: {DB_CONFIG['user']}@{DB_CONFIG['dbname']}")
            self.status_label.setStyleSheet("color: darkgreen; font-weight: bold;")
        except psycopg2.Error as e:
            self.conn = None
            self.cur = None
            self.status_label.setText(f"Помилка підключення: {e}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            QMessageBox.critical(self, "Помилка підключення", str(e))

    def _execute_query(self, query: Union[sql.SQL, str], params: Optional[tuple] = None,
                       fetch_one: bool = False, fetch_all: bool = False, commit: bool = False) -> Any:
        if not self.cur or self.cur.closed:  # Додано перевірку self.cur.closed
            QMessageBox.warning(self, "Помилка", "Немає активного курсору до БД або курсор закрито.")
            return None if fetch_one or fetch_all else False
        try:
            self.cur.execute(query, params or ())
            if commit:
                if self.conn: self.conn.commit()
                return True
            if fetch_one:
                return self.cur.fetchone()
            if fetch_all:
                return self.cur.fetchall()
            return True
        except psycopg2.Error as e:
            if self.conn: self.conn.rollback()
            error_query_str = ""
            if self.cur and hasattr(self.cur, 'query') and self.cur.query:
                query_bytes_or_str = self.cur.query
                error_query_str = query_bytes_or_str.decode('utf-8', errors='replace') if isinstance(query_bytes_or_str,
                                                                                                     bytes) else str(
                    query_bytes_or_str)
            elif isinstance(query, sql.SQL) and self.conn:
                try:
                    error_query_str = query.as_string(self.conn)
                except:
                    error_query_str = str(query)
            else:
                error_query_str = str(query)
            QMessageBox.critical(self, "Помилка SQL", f"Помилка: {e}\nЗапит: {error_query_str}")
            return None if fetch_one or fetch_all else False

#     def _load_data_to_table(self, table_widget: QTableWidget, query: Union[sql.SQL, str],
#                             params: Optional[tuple] = None):
#         header = table_widget.horizontalHeader()
#         current_sort_column = header.sortIndicatorSection()
#         current_sort_order = header.sortIndicatorOrder()
#         table_widget.setSortingEnabled(False)
#         records = self._execute_query(query, params, fetch_all=True)
#         table_widget.setRowCount(0)
#         table_widget.setColumnCount(0)
#         if records and self.cur and self.cur.description:
#             headers_desc = [desc[0] for desc in self.cur.description]
#             table_widget.setColumnCount(len(headers_desc))
#             table_widget.setHorizontalHeaderLabels(headers_desc)
#             table_widget.setRowCount(len(records))
#             for row_idx, record_dict in enumerate(records):
#                 for col_idx, col_name in enumerate(headers_desc):
#                     value = record_dict[col_name]
#                     item = QTableWidgetItem(str(value) if value is not None else "")
#                     if col_idx == 0:
#                         item.setData(Qt.ItemDataRole.UserRole, value)
#                     table_widget.setItem(row_idx, col_idx, item)
#             # table_widget.resizeColumnsToContents()
#             # table_widget.resizeRowsToContents()
# #
#         elif records is None:
#             pass
#         table_widget.setSortingEnabled(True)
#         if current_sort_column != -1:
#             table_widget.sortByColumn(current_sort_column, current_sort_order)
#             if not (current_sort_column == 0 and table_widget.isColumnHidden(0)):
#                 table_widget.sortByColumn(current_sort_column, current_sort_order)

    def _load_data_to_table(self, table_widget: QTableWidget, query: Union[sql.SQL, str],
                            params: Optional[tuple] = None):
        header = table_widget.horizontalHeader()
        current_sort_column = header.sortIndicatorSection()
        current_sort_order = header.sortIndicatorOrder()
        table_widget.setSortingEnabled(False)
        records = self._execute_query(query, params, fetch_all=True)
        table_widget.setRowCount(0)
        table_widget.setColumnCount(0)
        if records and self.cur and self.cur.description:
            headers_desc = [desc[0] for desc in self.cur.description]
            table_widget.setColumnCount(len(headers_desc))
            table_widget.setHorizontalHeaderLabels(headers_desc)
            table_widget.setRowCount(len(records))
            for row_idx, record_dict in enumerate(records):
                for col_idx, col_name in enumerate(headers_desc):
                    value = record_dict[col_name]
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if col_idx == 0:  # Сохраняем ID в UserRole для первого столбца
                        item.setData(Qt.ItemDataRole.UserRole, value)
                    table_widget.setItem(row_idx, col_idx, item)

            # Скрываем первый столбец (предполагается, что это столбец ID)
            if headers_desc and headers_desc[0].lower() == 'id':
                table_widget.setColumnHidden(0, True)

            # Альтернативно: можно использовать id_display_col_name_for_sort из tab_config
            # tab_config = ... # Нужно получить конфигурацию текущей вкладки
            # id_col_name = tab_config.get("id_display_col_name_for_sort", "ID").lower()
            # for col_idx, col_name in enumerate(headers_desc):
            #     if col_name.lower() == id_col_name:
            #         table_widget.setColumnHidden(col_idx, True)
            #         break

        elif records is None:
            pass
        table_widget.setSortingEnabled(True)
        if current_sort_column != -1:
            # Если скрыт столбец ID, сортировка по нему может быть нежелательной,
            # но мы оставляем возможность сортировки по другим столбцам
            if not table_widget.isColumnHidden(current_sort_column):
                table_widget.sortByColumn(current_sort_column, current_sort_order)

    def _create_search_and_crud_bar(self,
                                    parent_tab_widget_for_timer: QWidget,
                                    table: QTableWidget,
                                    base_query_provider: Callable[[], Union[sql.SQL, str]],
                                    search_columns_map: Dict[str, str],
                                    pk_column_name_db: str,
                                    id_column_display_name_for_sort: str,
                                    add_dialog_config: Optional[Dict[str, Any]] = None,
                                    edit_dialog_config: Optional[Dict[str, Any]] = None,
                                    delete_entity_name_db: Optional[str] = None) -> QHBoxLayout:
        # ... (код _create_search_and_crud_bar - з моєї ПОПЕРЕДНЬОЇ відповіді, де він ПОВЕРТАВ QHBoxLayout) ...
        control_bar_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText(f"Пошук по {', '.join(search_columns_map.keys())}...")
        control_bar_layout.addWidget(search_input, 1)
        refresh_button = QPushButton("Оновити")
        timer_key = parent_tab_widget_for_timer.objectName() if parent_tab_widget_for_timer.objectName() else str(
            id(parent_tab_widget_for_timer))
        if timer_key not in self.search_timers:
            self.search_timers[timer_key] = QTimer(self)
            self.search_timers[timer_key].setSingleShot(True)
            self.search_timers[timer_key].setInterval(500)
        current_search_timer = self.search_timers[timer_key]

        def perform_search_and_refresh():
            search_term = search_input.text().strip()
            base_query_obj = base_query_provider()
            final_query_parts: List[sql.Composable] = []
            if isinstance(base_query_obj, str):
                final_query_parts.append(sql.SQL(base_query_obj))
            elif isinstance(base_query_obj, sql.Composable):
                final_query_parts.append(base_query_obj)
            else:
                QMessageBox.critical(self, "Помилка конфігурації",
                                     "base_query_provider має повертати рядок або sql.SQL об'єкт."); return

            current_params: List[Any] = []
            base_query_already_has_where = False
            if self.conn:
                try:
                    base_query_str_for_check = base_query_obj.as_string(self.conn).lower() if isinstance(base_query_obj,
                                                                                                         sql.Composable) else str(
                        base_query_obj).lower()
                    if "where" in base_query_str_for_check:
                        base_query_already_has_where = True
                except:
                    pass

            if search_term:
                term_for_like = f"%{search_term}%"
                or_conditions: List[sql.Composable] = []
                for view_col_alias_for_search in search_columns_map.values():
                    condition = sql.SQL("{} ILIKE %s").format(sql.Identifier(view_col_alias_for_search))
                    or_conditions.append(condition)
                    current_params.append(term_for_like)
                if or_conditions:
                    if base_query_already_has_where:
                        final_query_parts.append(sql.SQL(" AND ("))
                    else:
                        final_query_parts.append(sql.SQL(" WHERE ("))
                    final_query_parts.append(sql.SQL(" OR ").join(or_conditions))
                    final_query_parts.append(sql.SQL(")"))

            header = table.horizontalHeader()
            sort_section, sort_order_qt = header.sortIndicatorSection(), header.sortIndicatorOrder()
            default_sort_order_sql = sql.SQL("DESC")

            if sort_section != -1:
                sort_col_data = header.model().headerData(sort_section, Qt.Orientation.Horizontal,
                                                          Qt.ItemDataRole.DisplayRole)
                if isinstance(sort_col_data, str) and sort_col_data:
                    order_by_sql_col = sql.Identifier(sort_col_data)
                    order_sql = sql.SQL("ASC") if sort_order_qt == Qt.SortOrder.AscendingOrder else sql.SQL("DESC")
                    final_query_parts.append(sql.SQL(" ORDER BY {} {}").format(order_by_sql_col, order_sql))
                else:
                    final_query_parts.append(
                        sql.SQL(" ORDER BY {} {}").format(sql.Identifier(id_column_display_name_for_sort),
                                                          default_sort_order_sql))
            else:
                final_query_parts.append(
                    sql.SQL(" ORDER BY {} {}").format(sql.Identifier(id_column_display_name_for_sort),
                                                      default_sort_order_sql))

            final_query = sql.SQL(" ").join(final_query_parts)
            self._load_data_to_table(table, final_query, tuple(current_params))

        current_search_timer.timeout.connect(perform_search_and_refresh)
        search_input.textChanged.connect(lambda: current_search_timer.start())
        buttons_crud_layout = QHBoxLayout()
        refresh_button = QPushButton("Оновити")
        refresh_button.clicked.connect(perform_search_and_refresh)
        buttons_crud_layout.addWidget(refresh_button)
        if add_dialog_config:
            add_button = QPushButton("Додати")
            add_button.clicked.connect(lambda: self._handle_add_action(add_dialog_config, perform_search_and_refresh))
            buttons_crud_layout.addWidget(add_button)
        if edit_dialog_config:
            edit_button = QPushButton("Редагувати")
            edit_button.clicked.connect(
                lambda: self._handle_edit_action(table, edit_dialog_config, perform_search_and_refresh))
            buttons_crud_layout.addWidget(edit_button)
        if delete_entity_name_db:
            delete_button = QPushButton("Видалити")
            delete_button.clicked.connect(
                lambda: self._handle_simple_delete(table, delete_entity_name_db, pk_column_name_db,
                                                   perform_search_and_refresh))
            buttons_crud_layout.addWidget(delete_button)
        control_bar_layout.addStretch(0)
        control_bar_layout.addLayout(buttons_crud_layout)
        perform_search_and_refresh()
        return control_bar_layout

    def _create_generic_tab(self, tab_config: Dict[str, Any]):
        tab = QWidget()
        tab.setObjectName(tab_config["tab_object_name"])
        main_tab_layout = QVBoxLayout(tab)
        table = create_standard_table()
        control_bar_panel_layout = self._create_search_and_crud_bar(
            tab, table,
            tab_config["base_query_provider"],
            tab_config["search_cols_map"],
            tab_config["pk_db_col_name"],
            tab_config["id_display_col_name_for_sort"],
            tab_config.get("add_dialog_config"),
            tab_config.get("edit_dialog_config"),
            tab_config.get("delete_entity_db_name")
        )
        if control_bar_panel_layout:
            main_tab_layout.addLayout(control_bar_panel_layout)
        main_tab_layout.addWidget(table)
        self.tab_widget.addTab(tab, tab_config["tab_name_display"])


    def _handle_add_action(self, dialog_config: Dict[str, Any], refresh_func: Callable[[], None]):
        table_name = dialog_config['table_name']
        fields_info = dialog_config['fields']
        dialog_title = f"Додати в '{table_name}'"

        # Завжди передаємо self.cur, оскільки він може бути потрібен для combobox_db або choices_provider
        data_from_dialog = show_input_dialog(self, dialog_title, fields_info, db_cursor=self.cur)

        if data_from_dialog:
            actual_data_to_insert = {}
            # --- НАЧАЛО БЛОКА ОБРАБОТКИ ДАННЫХ (оновлено для більшої ясності) ---
            for field_conf_iter in fields_info:
                field_name_iter = field_conf_iter.get('name')
                db_col_name = field_conf_iter.get('db_col_name')  # Використовуємо db_col_name якщо є

                if not field_name_iter or not db_col_name:  # Пропускаємо поля без імені або без db_col_name
                    continue

                if field_conf_iter.get('edit_only', False) and dialog_title.lower().startswith("додати"):
                    continue  # Пропускаємо поля 'edit_only' при додаванні

                if field_name_iter in data_from_dialog:
                    value_from_dialog_iter = data_from_dialog[field_name_iter]

                    # Спеціальна обробка для числових полів (year_publication, page_number)
                    # І для parent_comment_id, який також може бути числовим або None
                    if db_col_name in ['year_publication', 'page_number'] or \
                            (table_name == 'comment' and db_col_name == 'parent_comment_id'):
                        if isinstance(value_from_dialog_iter, str) and value_from_dialog_iter.strip() == '':
                            actual_data_to_insert[db_col_name] = None  # Пустий рядок -> NULL
                        elif value_from_dialog_iter is None:  # Якщо currentData() повернуло None
                            actual_data_to_insert[db_col_name] = None
                        else:
                            try:
                                actual_data_to_insert[db_col_name] = int(value_from_dialog_iter)
                            except (ValueError, TypeError):
                                if db_col_name == 'parent_comment_id':  # Для parent_comment_id це нормально, якщо не обрано
                                    actual_data_to_insert[db_col_name] = None
                                else:
                                    QMessageBox.warning(self, "Помилка даних",
                                                        f"Значення для поля '{field_conf_iter.get('label', field_name_iter)}' має бути цілим числом або порожнім.")
                                    if self.conn and not self.conn.closed: self.conn.rollback()
                                    refresh_func()
                                    return
                    elif db_col_name == 'is_archived':  # Обробка boolean
                        actual_data_to_insert[db_col_name] = bool(value_from_dialog_iter)
                    else:  # Для інших полів (рядки, ENUM з combobox)
                        if isinstance(value_from_dialog_iter, str) and value_from_dialog_iter.strip() == '' and \
                                not field_conf_iter.get('required', False) and \
                                field_conf_iter.get('type') != 'checkbox':
                            actual_data_to_insert[db_col_name] = None  # Необов'язковий порожній рядок -> NULL
                        else:
                            actual_data_to_insert[db_col_name] = value_from_dialog_iter
            # --- КІНЕЦЬ БЛОКА ОБРАБОТКИ ДАННИХ ---

            # Перевірка на повністю порожні дані (після виключення selected_authors, якщо є)
            # Ця перевірка може бути більш специфічною для кожної таблиці
            if not actual_data_to_insert and not (table_name == 'book' and data_from_dialog.get('selected_authors')):
                QMessageBox.information(self, "Інформація", "Немає даних для додавання.")
                # refresh_func() тут не потрібен, бо нічого не змінилося
                return

            # Перевірка обов'язкових полів
            # for field_conf_check in fields_info:
            #     db_col_check = field_conf_check.get('db_col_name')
            #     if field_conf_check.get('required', False) and db_col_check and \
            #             (db_col_check not in actual_data_to_insert or actual_data_to_insert[db_col_check] is None):
            #
            #         # Пропускаємо selected_authors, бо він обробляється окремо
            #         if field_conf_check.get('type') == 'author_select' and table_name == 'book':
            #             if not data_from_dialog.get('selected_authors'):  # Якщо автори обов'язкові і не обрані
            #                 QMessageBox.warning(self, "Помилка даних",
            #                                     f"Поле '{field_conf_check.get('label')}' є обов'язковим (не обрано авторів).")
            #                 if self.conn and not self.conn.closed: self.conn.rollback()
            #                 refresh_func()
            #                 return
            #             continue  # Переходимо до наступного поля
            #
            #         QMessageBox.warning(self, "Помилка даних",
            #                             f"Обов'язкове поле '{field_conf_check.get('label')}' не заповнено.")
            #         if self.conn and not self.conn.closed: self.conn.rollback()
            #         refresh_func()  # Оновлюємо, щоб користувач бачив поточний стан (нічого не додано)
            #         return

            for field_conf_check in fields_info:
                db_col_check = field_conf_check.get('db_col_name')
                field_label_for_msg = field_conf_check.get('label', field_conf_check.get('name', 'Невідоме поле'))

                if field_conf_check.get('required', False) and db_col_check:
                    # Поточне значення поля з actual_data_to_insert або з data_from_dialog, якщо воно ще не оброблене
                    current_field_value = actual_data_to_insert.get(db_col_check)

                    # Особлива перевірка для текстових полів, як comment_text
                    is_empty_text = False
                    if table_name == 'comment' and db_col_check == 'comment_text':
                        if isinstance(current_field_value, str) and not current_field_value.strip():
                            is_empty_text = True

                    if current_field_value is None or is_empty_text:
                        # Пропускаємо selected_authors, бо він обробляється окремо (або може бути не required)
                        if field_conf_check.get('type') == 'author_select' and table_name == 'book':
                            # Якщо поле selected_authors required і воно відсутнє або порожнє
                            # Ця логіка вже має бути частково реалізована вище, але для повноти:
                            if not data_from_dialog.get('selected_authors'):
                                QMessageBox.warning(self, "Помилка даних",
                                                    f"Поле '{field_label_for_msg}' є обов'язковим (не обрано авторів).")
                                if self.conn and not self.conn.closed: self.conn.rollback()
                                refresh_func()
                                return
                            continue

                        QMessageBox.warning(self, "Помилка даних",
                                            f"Обов'язкове поле '{field_label_for_msg}' не заповнено або містить лише пробіли.")
                        if self.conn and not self.conn.closed: self.conn.rollback()
                        refresh_func()
                        return

            inserted_pk_value = None
            if actual_data_to_insert:  # Тільки якщо є що вставляти в основну таблицю
                # Формування запиту INSERT
                columns = sql.SQL(', ').join(map(sql.Identifier, actual_data_to_insert.keys()))
                placeholders = sql.SQL(', ').join(sql.SQL('%s') * len(actual_data_to_insert))

                # `pk_db_col_name` має бути в dialog_config, інакше RETURNING не спрацює або буде помилка
                pk_col_for_returning_name = dialog_config.get('pk_db_col_name')
                if not pk_col_for_returning_name:
                    QMessageBox.critical(self, "Помилка конфігурації",
                                         f"Не вказано 'pk_db_col_name' для таблиці '{table_name}' в add_dialog_config.")
                    if self.conn and not self.conn.closed: self.conn.rollback()
                    refresh_func()
                    return

                pk_col_for_returning = sql.Identifier(pk_col_for_returning_name)

                # Використовуємо public явно, якщо схема не в search_path або для однозначності
                insert_query = sql.SQL("INSERT INTO public.{} ({}) VALUES ({}) RETURNING {}").format(
                    sql.Identifier(table_name),
                    columns,
                    placeholders,
                    pk_col_for_returning
                )



                inserted_record_pk_row = self._execute_query(insert_query,
                                                             list(actual_data_to_insert.values()),
                                                             fetch_one=True,
                                                             commit=False)  # commit=False, бо транзакція керується нижче

                if inserted_record_pk_row:
                    inserted_pk_value = inserted_record_pk_row[0]
                else:
                    # Повідомлення про помилку вже було показано в _execute_query,
                    # і там же мав бути rollback.
                    refresh_func()  # Оновити, щоб показати стан після невдалої спроби
                    return  # Вихід, якщо основний запис не вдалося вставити

            # --- СПЕЦИФІЧНА ЛОГІКА ДЛЯ РІЗНИХ ТАБЛИЦЬ (наприклад, book_author) ---
            commit_successful = False
            if table_name == 'book':
                author_ids_to_link = data_from_dialog.get('selected_authors')
                if author_ids_to_link and inserted_pk_value is not None:
                    all_author_links_successful = True
                    for author_id in author_ids_to_link:
                        ba_query = sql.SQL("INSERT INTO public.book_author (book_id, author_id) VALUES (%s, %s)")
                        if not self._execute_query(ba_query, (inserted_pk_value, author_id), commit=False):
                            all_author_links_successful = False
                            break
                    if all_author_links_successful:
                        commit_successful = True
                    else:
                        QMessageBox.critical(self, "Помилка", "Помилка при додаванні зв'язків з авторами.")
                elif inserted_pk_value is not None:  # Книга додана, але без авторів (якщо вони не обов'язкові)
                    commit_successful = True

            elif table_name == 'comment':  # Для коментарів, основний запис вже додано, якщо є inserted_pk_value
                if inserted_pk_value is not None:
                    commit_successful = True
                # Тут може бути інша специфічна логіка для коментарів, якщо потрібно

            # ... (інші специфічні обробки для інших таблиць) ...

            else:  # Для інших таблиць, якщо немає специфічної логіки після основного INSERT
                if inserted_pk_value is not None or not actual_data_to_insert:
                    # Якщо щось було вставлено, АБО якщо actual_data_to_insert було порожнім
                    # (наприклад, лише selected_authors для нової книги - хоча це оброблено вище)
                    # але цей сценарій треба переглянути, бо якщо actual_data_to_insert порожнє, inserted_pk_value буде None
                    commit_successful = True  # Припускаємо успіх, якщо немає додаткових кроків
                # Якщо actual_data_to_insert було порожнє і нічого не вставлялося, inserted_pk_value буде None.
                # У такому випадку, якщо немає специфічної логіки (як book_author), то commit_successful має залишитися False,
                # інакше буде спроба зробити commit без операцій.
                # Краще явно:
                if inserted_pk_value is not None:
                    commit_successful = True

            # Завершення транзакції
            if commit_successful:
                if self.conn and not self.conn.closed:
                    self.conn.commit()
                    QMessageBox.information(self, "Успіх", f"Запис в '{table_name}' успішно додано.")
            else:
                # Якщо ми дійшли сюди і commit_successful == False, значить щось пішло не так
                # або не було що додавати (крім випадків, коли _execute_query вже обробив помилку і зробив rollback).
                # Потрібно переконатися, що rollback викликається у всіх гілках помилок.
                if self.conn and not self.conn.closed:
                    self.conn.rollback()
                # QMessageBox.warning(self, "Скасовано", "Додавання запису було скасовано або сталася помилка.") # Можливо, це повідомлення зайве, якщо помилка вже була показана

            refresh_func()


    def _handle_edit_action(self, table: QTableWidget, dialog_config: Dict[str, Any], refresh_func: Callable[[], None]):
        # ... (код _handle_edit_action - з моєї ПОПЕРЕДНЬОЇ повної відповіді, з виправленнями для dialog_initial_data) ...
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows: QMessageBox.warning(self, "Помилка", "Оберіть запис для редагування."); return
        row_index = selected_rows[0].row()
        pk_value_item = table.item(row_index, 0)
        if not pk_value_item: QMessageBox.warning(self, "Помилка", "Не вдалося отримати ID."); return
        pk_value = pk_value_item.data(Qt.ItemDataRole.UserRole)
        table_name = dialog_config['table_name']
        pk_db_col_name = dialog_config['pk_db_col_name']
        fields_info_for_dialog = dialog_config['fields']

        if not self.cur or self.cur.closed:  # Додаткова перевірка курсору
            QMessageBox.critical(self, "Помилка БД", "З'єднання з БД втрачено або курсор закрито перед редагуванням.")
            return

        dialog_initial_data = {}
        db_cols_for_select = [f_info.get('db_col_name', f_info['name']) for f_info in fields_info_for_dialog if
                              not f_info.get('edit_only', False) and f_info.get('db_col_name') is not None]
        if db_cols_for_select:
            select_cols_sql = sql.SQL(", ").join(map(sql.Identifier, db_cols_for_select))
            select_query = sql.SQL("SELECT {} FROM public.{} WHERE {} = %s").format(select_cols_sql,
                                                                                    sql.Identifier(table_name),
                                                                                    sql.Identifier(pk_db_col_name))
            current_data_from_db = self._execute_query(select_query, (pk_value,), fetch_one=True)
            if not current_data_from_db: QMessageBox.warning(self, "Помилка",
                                                             "Не вдалося завантажити дані для редагування (запис не знайдено)."); return
            for f_info in fields_info_for_dialog:
                if not f_info.get('edit_only', False) and f_info.get('db_col_name') is not None:
                    db_col = f_info.get('db_col_name', f_info['name'])
                    if db_col in current_data_from_db: dialog_initial_data[f_info['name']] = current_data_from_db[
                        db_col]

        if table_name == 'book':
            current_author_ids_query = sql.SQL("SELECT author_id FROM public.book_author WHERE book_id = %s")
            author_id_rows = self._execute_query(current_author_ids_query, (pk_value,), fetch_all=True)
            dialog_initial_data['selected_authors'] = [row['author_id'] for row in
                                                       author_id_rows] if author_id_rows else []

        updated_data_from_dialog = show_input_dialog(self, f"Редагувати в '{table_name}' (ID: {pk_value})",
                                                     fields_info_for_dialog, dialog_initial_data, db_cursor=self.cur)
#
        if updated_data_from_dialog:
            data_for_sql_update = {}
            new_author_ids: Optional[List[int]] = None
            if table_name == 'book' and 'selected_authors' in updated_data_from_dialog:
                new_author_ids = updated_data_from_dialog.pop('selected_authors')

            if table_name == 'user' and 'password_new' in updated_data_from_dialog:
                new_password = updated_data_from_dialog.pop('password_new', None)
                if new_password: data_for_sql_update['password'] = new_password

            if table_name == 'book' and 'is_archived' in updated_data_from_dialog:
                is_archived_new_val = updated_data_from_dialog['is_archived']
                current_book_db_state = self._execute_query(
                    sql.SQL("SELECT is_archived, archived_at FROM public.book WHERE book_id = %s"), (pk_value,),
                    fetch_one=True)
                if current_book_db_state:
                    archived_at_val = None
                    if is_archived_new_val:
                        if not current_book_db_state["is_archived"] or current_book_db_state["archived_at"] is None:
                            archived_at_val = psycopg2.extensions.AsIs('NOW()')
                        else:
                            archived_at_val = current_book_db_state["archived_at"]
                    data_for_sql_update['archived_at'] = archived_at_val

            for key_in_dialog, new_value in updated_data_from_dialog.items():
                field_config_for_key = next(
                    (f_cfg for f_cfg in fields_info_for_dialog if f_cfg['name'] == key_in_dialog), None)
                if field_config_for_key and not field_config_for_key.get('edit_only', False):
                    db_col_to_update = field_config_for_key.get('db_col_name', key_in_dialog)
                    original_value_for_compare = dialog_initial_data.get(key_in_dialog)
                    changed = False
                    if isinstance(new_value, bool):
                        if bool(new_value) != bool(original_value_for_compare): changed = True
                    elif str(new_value) != str(
                        original_value_for_compare if original_value_for_compare is not None else ''):
                        changed = True
                    if changed and db_col_to_update not in data_for_sql_update:
                        data_for_sql_update[db_col_to_update] = new_value

            update_successful = True
            if data_for_sql_update:
                set_clauses = sql.SQL(', ').join(
                    [sql.SQL("{} = %s").format(sql.Identifier(key)) for key in data_for_sql_update.keys()])
                update_query = sql.SQL("UPDATE public.{} SET {} WHERE {} = %s").format(sql.Identifier(table_name),
                                                                                       set_clauses,
                                                                                       sql.Identifier(pk_db_col_name))
                update_params = list(data_for_sql_update.values()) + [pk_value]
                if not self._execute_query(update_query, update_params, commit=False): update_successful = False

            if table_name == 'book' and new_author_ids is not None and update_successful:
                delete_ba_query = sql.SQL("DELETE FROM public.book_author WHERE book_id = %s")
                if not self._execute_query(delete_ba_query, (pk_value,), commit=False):
                    update_successful = False
                else:
                    for author_id in new_author_ids:
                        insert_ba_query = sql.SQL("INSERT INTO public.book_author (book_id, author_id) VALUES (%s, %s)")
                        if not self._execute_query(insert_ba_query, (pk_value, author_id), commit=False):
                            update_successful = False;
                            break

            if update_successful:
                if self.conn: self.conn.commit()
                QMessageBox.information(self, "Успіх", "Запис оновлено.")
            else:
                if self.conn: self.conn.rollback()
                QMessageBox.critical(self, "Помилка", "Помилка при оновленні запису або зв'язків.")
            refresh_func()

    def _handle_simple_delete(self, table: QTableWidget, table_name_db: str, pk_column_name_db: str,
                              refresh_func: Callable[[], None]):
        # ... (код з попередньої відповіді) ...
        selected_rows = table.selectionModel().selectedRows()
        if not selected_rows: QMessageBox.warning(self, "Помилка", "Оберіть рядок для видалення."); return
        row_index = selected_rows[0].row()
        pk_value_item = table.item(row_index, 0)
        if not pk_value_item: QMessageBox.warning(self, "Помилка", "Не вдалося отримати ID."); return
        pk_value = pk_value_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Підтвердження",
                                     f"Видалити запис з ID {pk_value} з таблиці '{table_name_db}'?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Спочатку видаляємо залежності, якщо вони не видаляються каскадно
            if table_name_db == "book":
                self._execute_query(sql.SQL("DELETE FROM public.book_author WHERE book_id = %s"), (pk_value,),
                                    commit=True)
                self._execute_query(sql.SQL("DELETE FROM public.book_list WHERE book_id = %s"), (pk_value,),
                                    commit=True)
                self._execute_query(sql.SQL("DELETE FROM public.comment WHERE book_id = %s"), (pk_value,), commit=True)
                self._execute_query(sql.SQL("DELETE FROM public.evaluation WHERE book_id = %s"), (pk_value,),
                                    commit=True)
                self._execute_query(sql.SQL("DELETE FROM public.quote WHERE book_id = %s"), (pk_value,), commit=True)
            elif table_name_db == "author":
                # Якщо автор видаляється, потрібно спочатку видалити його з book_author
                self._execute_query(sql.SQL("DELETE FROM public.book_author WHERE author_id = %s"), (pk_value,),
                                    commit=True)
                # І можливо, з інших таблиць, якщо автор там використовується як зовнішній ключ з RESTRICT
            elif table_name_db == "user":
                self._execute_query(sql.SQL("DELETE FROM public.book_list WHERE user_id = %s"), (pk_value,),
                                    commit=True)
                # ... і так далі для comment, evaluation, quote, якщо user_id там з RESTRICT

            # Потім видаляємо основний запис
            query = sql.SQL("DELETE FROM public.{} WHERE {} = %s").format(sql.Identifier(table_name_db),
                                                                          sql.Identifier(pk_column_name_db))
            if self._execute_query(query, (pk_value,), commit=True):
                QMessageBox.information(self, "Успіх", "Запис видалено.")
            refresh_func()  # Оновлюємо в будь-якому випадку, щоб побачити результат або помилку

    def init_ui_tabs(self):
        print("DEBUG: Entered init_ui_tabs()")
        self._create_generic_tab(AUTHORS_TAB_CONFIG)
        self._create_generic_tab(BOOKS_TAB_CONFIG)
        self._create_generic_tab(USERS_TAB_CONFIG)
        self._create_generic_tab(USER_BOOK_LISTS_TAB_CONFIG)
        self._create_generic_tab(COMMENTS_TAB_CONFIG)
        self._create_generic_tab(EVALUATIONS_TAB_CONFIG)
        self._create_generic_tab(QUOTES_TAB_CONFIG)
        self.create_special_queries_tab()

    def create_special_queries_tab(self):
        # ... (код create_special_queries_tab - без змін) ...
        tab = QWidget()
        self.tab_widget.addTab(tab, "Спеціальні запити")
        main_layout = QHBoxLayout(tab)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left_panel_widget = QWidget()
        left_layout = QVBoxLayout(left_panel_widget)
        self.query_list_widget = QListWidget()
        for query_info in SPECIAL_QUERIES: self.query_list_widget.addItem(query_info["name"])
        self.query_list_widget.currentItemChanged.connect(self.display_selected_query_info)
        self.sql_display = QTextEdit()
        self.sql_display.setObjectName("SqlQueryDisplay")
        self.sql_display.setReadOnly(True)
        self.sql_display.setFont(QFont("Courier New", 10))
        self.params_input_area = QWidget()
        self.params_input_area.setObjectName("ParamsInputWidget")
        self.params_form_layout = QFormLayout(self.params_input_area)
        execute_button = QPushButton("Виконати запит")
        execute_button.clicked.connect(self.execute_current_special_query)
        left_layout.addWidget(QLabel("Оберіть запит:"))
        left_layout.addWidget(self.query_list_widget)
        left_layout.addWidget(QLabel("SQL код запиту:"))
        left_layout.addWidget(self.sql_display)
        left_layout.addWidget(QLabel("Параметри запиту:"))
        left_layout.addWidget(self.params_input_area)
        left_layout.addWidget(execute_button)
        left_layout.addStretch(1)
        splitter.addWidget(left_panel_widget)
        self.results_table = create_standard_table()
        splitter.addWidget(self.results_table)
        main_layout.addWidget(splitter)
        splitter.setSizes([self.width() // 3, 2 * self.width() // 3])
        if self.query_list_widget.count() > 0: self.query_list_widget.setCurrentRow(0)



    def display_selected_query_info(self, current_item: Optional[QListWidgetItem],
                                    _previous_item: Optional[QListWidgetItem]):
        if not current_item:
            self.sql_display.clear()
            # Очищення старих параметрів
            while self.params_form_layout.count():
                child = self.params_form_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.current_special_query_params_config = []  # Очищаємо конфіг
            return

        query_name = current_item.text()
        query_data = next((q for q in SPECIAL_QUERIES if q["name"] == query_name), None)

        if not query_data:
            self.sql_display.setText(f"Конфігурація для запиту '{query_name}' не знайдена.")
            # Очищення старих параметрів
            while self.params_form_layout.count():
                child = self.params_form_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            self.current_special_query_params_config = []
            return

        self.sql_display.setText(query_data["sql"])

        # Очищення старих параметрів перед додаванням нових
        while self.params_form_layout.count():
            child = self.params_form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.current_special_query_params_config = query_data.get("params", [])

        for param_info in self.current_special_query_params_config:
            label = QLabel(param_info["label"])
            param_type = param_info.get("type", "line_edit")
            param_name = param_info["name"]  # Отримуємо ім'я параметра для objectName
            widget: QWidget

            if param_type == "line_edit":
                widget = QLineEdit()
            elif param_type == "date_edit":
                widget = QDateEdit()
                widget.setCalendarPopup(True)
                widget.setDisplayFormat("yyyy-MM-dd")  # Стандартний формат для SQL
                widget.setDate(QDate.currentDate())

            else:
                widget = QLineEdit()
                print(f"Warning: Unknown param type '{param_type}' for '{param_name}'. Defaulting to QLineEdit.")

            widget.setObjectName(f"param_input_{param_name}")  # <--- ВАЖЛИВО: Встановлюємо objectName
            self.params_form_layout.addRow(label, widget)



    def execute_current_special_query(self):
        current_query_item = self.query_list_widget.currentItem()
        if not current_query_item:
            QMessageBox.warning(self, "Помилка", "Запит не обрано.")
            return

        query_name = current_query_item.text()
        query_data = next((q for q in SPECIAL_QUERIES if q["name"] == query_name), None)

        if not query_data:
            QMessageBox.warning(self, "Помилка", f"Конфігурація для запиту '{query_name}' не знайдена.")
            return

        sql_to_execute_str = query_data["sql"]
        params_values: List[Any] = []  # Може містити рядки або числа

        try:
            for param_info in query_data.get("params", []):
                param_name = param_info["name"]
                param_type = param_info.get("type", "line_edit")
                param_actual_type = param_info.get("param_type")  # Для розрізнення string/integer/float

                input_widget: Optional[QWidget] = None  # Ініціалізуємо

                if param_type == "date_edit":
                    input_widget = self.params_input_area.findChild(QDateEdit, f"param_input_{param_name}")
                elif param_type == "line_edit":  # Або будь-який інший тип, що використовує QLineEdit
                    input_widget = self.params_input_area.findChild(QLineEdit, f"param_input_{param_name}")
                # Додайте сюди інші типи віджетів, якщо вони будуть використовуватися для параметрів

                if input_widget:
                    value_str = ""
                    if isinstance(input_widget, QDateEdit):
                        value_str = input_widget.date().toString("yyyy-MM-dd")
                        params_values.append(value_str)  # Дати зазвичай передаються як рядки в SQL
                    elif isinstance(input_widget, QLineEdit):
                        value_str = input_widget.text()
                        if param_actual_type == "integer":
                            try:
                                params_values.append(int(value_str))
                            except ValueError:
                                QMessageBox.critical(self, "Помилка параметра",
                                                     f"Значення '{value_str}' для '{param_info['label']}' має бути цілим числом.")
                                return
                        elif param_actual_type == "float":
                            try:
                                params_values.append(float(value_str.replace(',', '.')))
                            except ValueError:
                                QMessageBox.critical(self, "Помилка параметра",
                                                     f"Значення '{value_str}' для '{param_info['label']}' має бути дійсним числом.")
                                return
                        # Для ILIKE обробка '%'
                        elif "ILIKE" in sql_to_execute_str.upper() and "%" not in value_str:
                            params_values.append(f"%{value_str}%")
                        else:
                            params_values.append(value_str)
                    else:
                        # Якщо у вас є інші типи віджетів для параметрів, додайте їх обробку
                        QMessageBox.critical(self, "Внутрішня помилка",
                                             f"Невідомий тип віджету для параметра {param_name}")
                        return
                else:
                    QMessageBox.critical(self, "Внутрішня помилка", f"Не знайдено поле для параметра {param_name}")
                    return
        except Exception as e:
            QMessageBox.critical(self, "Помилка параметрів", f"Не вдалося обробити параметри: {e}")
            import traceback
            traceback.print_exc()
            return

        self._load_data_to_table(self.results_table, sql.SQL(sql_to_execute_str), tuple(params_values))

    def closeEvent(self, event: Any):
        if self.cur: self.cur.close()
        if self.conn: self.conn.close()
        event.accept()


# --- __main__ ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    admin_window = AdminPanel()
    admin_window.show()
    sys.exit(app.exec())
    locale = QLocale(QLocale.Language.English, QLocale.Country.UnitedStates)
    assert isinstance(locale, English)
    QLocale.setDefault(locale)


