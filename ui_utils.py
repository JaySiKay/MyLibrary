import psycopg2
from PyQt6.QtWidgets import (
    QTableWidget, QAbstractItemView, QHeaderView, QDialog, QFormLayout,
    QLineEdit, QCheckBox, QDialogButtonBox, QTextEdit, QWidget, QMessageBox,
    QListWidget, QListWidgetItem, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt
from typing import List, Dict, Any, Optional
from psycopg2 import sql


def create_standard_table() -> QTableWidget:
    table = QTableWidget()
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.setSortingEnabled(True)
    table.setWordWrap(True)
    header = table.horizontalHeader()
    header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    return table


def _get_combobox_choices(provider_name: str, db_cursor: Optional[psycopg2.extensions.cursor]) -> List[str]:
    if not db_cursor or db_cursor.closed:
        QMessageBox.warning(None, "Помилка БД", f"Немає активного курсору для отримання значень {provider_name}.")
        return []
    choices = []
    query_str = ""
    try:
        if provider_name == 'get_enum_values_genre':
            query_str = "SELECT unnest(enum_range(NULL::genre_type)) AS val;"
        elif provider_name == 'get_enum_values_age_restriction':
            query_str = "SELECT unnest(enum_range(NULL::age_restriction_type)) AS val;"
        elif provider_name == 'get_enum_values_reading_status':
            query_str = "SELECT unnest(enum_range(NULL::reading_status_type)) AS val;"
        elif provider_name == 'get_enum_values_rating_type':
            query_str = "SELECT unnest(enum_range(NULL::rating_type)) AS val;"
        else:
            QMessageBox.warning(None, "Помилка конфігурації", f"Невідомий 'choices_provider': {provider_name}")
            return []
        db_cursor.execute(query_str)
        choices = [row['val'] for row in db_cursor.fetchall()]
    except psycopg2.Error as e:
        QMessageBox.critical(None, "Помилка запиту до БД",
                             f"Помилка отримання значень для {provider_name}: {e}\nЗапит: {query_str}")
    except Exception as e_gen:
        QMessageBox.critical(None, "Внутрішня помилка",
                             f"Неочікувана помилка отримання значень для {provider_name}: {e_gen}")
    return choices


def select_authors_dialog(parent: QWidget, db_cursor: Optional[psycopg2.extensions.cursor],
                          current_author_ids: Optional[List[int]] = None) -> Optional[List[int]]:
    if not db_cursor or db_cursor.closed:
        QMessageBox.warning(parent, "Помилка", "Немає активного курсору до БД для завантаження авторів.")
        return None

    dialog = QDialog(parent)
    dialog.setWindowTitle("Вибір авторів")
    dialog.setMinimumWidth(400)
    dialog.setMinimumHeight(300)

    main_layout = QVBoxLayout(dialog)

    search_input = QLineEdit(dialog)
    search_input.setPlaceholderText("Пошук авторів (прізвище, ім'я)...")
    main_layout.addWidget(search_input)

    author_list_widget = QListWidget(dialog)
    author_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
    main_layout.addWidget(author_list_widget)

    def load_and_display_authors(search_term=""):
        author_list_widget.clear()
        query_str_authors = sql.SQL('SELECT author_id, first_name, last_name FROM public.author')
        params_authors = []
        if search_term:
            query_str_authors += sql.SQL(" WHERE first_name ILIKE %s OR last_name ILIKE %s")
            like_term = f"%{search_term}%"
            params_authors.extend([like_term, like_term])
        query_str_authors += sql.SQL(" ORDER BY last_name, first_name")

        try:
            db_cursor.execute(query_str_authors, tuple(params_authors))
            fetched_authors = db_cursor.fetchall()
            if fetched_authors:
                for author_data in fetched_authors:
                    item_text = f"{author_data['first_name']} {author_data['last_name']}"
                    list_item = QListWidgetItem(item_text)
                    list_item.setData(Qt.ItemDataRole.UserRole, author_data['author_id'])
                    author_list_widget.addItem(list_item)
                    if current_author_ids and author_data['author_id'] in current_author_ids:
                        list_item.setSelected(True)
        except psycopg2.Error as e:
            QMessageBox.warning(dialog, "Помилка завантаження авторів", str(e))
        except Exception as e_general:
            QMessageBox.warning(dialog, "Загальна помилка", f"Не вдалося завантажити авторів: {e_general}")

    search_input.textChanged.connect(load_and_display_authors)
    load_and_display_authors()

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    main_layout.addWidget(buttons)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        selected_ids = []
        for item in author_list_widget.selectedItems():
            author_id = item.data(Qt.ItemDataRole.UserRole)
            if author_id is not None:
                selected_ids.append(int(author_id))
        return selected_ids
    return None


def _populate_parent_comment_combo_external(
        target_combo: QComboBox,
        book_id_value: Optional[int],
        field_conf_for_parent: Dict[str, Any],
        db_cursor: Optional[psycopg2.extensions.cursor],
        parent_dialog: QDialog
):
    target_combo.blockSignals(True)
    try:
        target_combo.clear()
        none_option_text = field_conf_for_parent.get('allow_none_text', "---")
        target_combo.addItem(none_option_text, None)

        if book_id_value is not None and db_cursor and not db_cursor.closed:
            try:
                query = sql.SQL("""
                                SELECT c.comment_id,
                                       COALESCE(u.username, 'Анонім') as commenter_name, 
                                       LEFT (c.comment_text, 50) as preview_text
                                FROM public.comment c
                                LEFT JOIN public."user" u ON c.user_id = u.user_id
                                WHERE c.book_id = %s
                                ORDER BY c.created_at DESC;
                                """)
                db_cursor.execute(query, (book_id_value,))
                comments_for_book = db_cursor.fetchall()

                for comment in comments_for_book:#
                    display_text = f"({comment['commenter_name']}): \"{comment['preview_text']}"
                    if len(comment['preview_text']) == 50:
                        display_text += "..."
                    display_text += "\""
                    target_combo.addItem(display_text, comment['comment_id'])
            except psycopg2.Error as e_sql:
                print(f"SQL Error loading parent comments for book_id {book_id_value}: {e_sql}")
                QMessageBox.warning(parent_dialog, "Помилка БД",
                                    f"Не вдалося завантажити список коментарів для відповіді: {e_sql}")
            except Exception as e_gen:
                print(f"General Error loading parent comments for book_id {book_id_value}: {e_gen}")
                QMessageBox.warning(parent_dialog, "Помилка", f"Не вдалося завантажити список коментарів: {e_gen}")
    finally:
        target_combo.blockSignals(False)


def _update_author_display_text_in_dialog(line_edit_widget: QLineEdit, db_cursor_for_names: Optional[psycopg2.extensions.cursor]):
    selected_ids = line_edit_widget.property("selected_author_ids")
    if not isinstance(selected_ids, list) or not selected_ids:
        line_edit_widget.setText("Автори не обрані")
        return

    if not db_cursor_for_names or db_cursor_for_names.closed:
        line_edit_widget.setText(f"Помилка: немає курсору БД (IDs: {selected_ids})")
        return
    try:
        placeholders = sql.SQL(', ').join(sql.Placeholder() * len(selected_ids))
        query_authors_str = sql.SQL(
            "SELECT first_name, last_name FROM public.author WHERE author_id IN ({}) ORDER BY last_name, first_name"
        ).format(placeholders)
        db_cursor_for_names.execute(query_authors_str, selected_ids)
        authors_records = db_cursor_for_names.fetchall()
        names = [f"{rec['first_name']} {rec['last_name']}" for rec in authors_records]
        line_edit_widget.setText(", ".join(names) if names else "Обрані автори не знайдені")
    except psycopg2.Error as e_load_authors:
        line_edit_widget.setText(f"Помилка завантаження імен: {e_load_authors}")
        print(f"Error fetching author names for display: {e_load_authors}")
    except Exception as e_gen:
        line_edit_widget.setText("Загальна помилка при завантаженні імен")
        print(f"General error fetching author names: {e_gen}")


def _on_author_select_button_clicked_in_dialog(
        line_edit_for_display: QLineEdit,
        parent_dialog_for_select: QDialog,
        db_cursor_for_select: Optional[psycopg2.extensions.cursor]):
    current_ids_from_property = line_edit_for_display.property("selected_author_ids")
    current_ids_list = current_ids_from_property if isinstance(current_ids_from_property, list) else []
    newly_selected_ids = select_authors_dialog(parent_dialog_for_select, db_cursor_for_select, current_ids_list)
    if newly_selected_ids is not None:
        line_edit_for_display.setProperty("selected_author_ids", newly_selected_ids)
        _update_author_display_text_in_dialog(line_edit_for_display, db_cursor_for_select)


def show_input_dialog(parent: QWidget, title: str, fields_config: List[Dict[str, Any]],
                      current_data: Optional[Dict[str, Any]] = None,
                      db_cursor: Optional[psycopg2.extensions.cursor] = None) -> Optional[Dict[str, Any]]:
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumWidth(600)

    form_layout = QFormLayout(dialog)
    input_widgets: Dict[str, QWidget] = {}

    try:
        for field_conf in fields_config:
            field_name = field_conf.get('name')
            label_text_original = field_conf.get('label')
            field_type = field_conf.get('type', 'line_edit')
            is_required = field_conf.get('required', False)

            if not field_name:
                QMessageBox.critical(parent, "Помилка конфігурації", f"Поле без 'name': {field_conf}")
                return None

            label_text_for_display = label_text_original
            if label_text_original and is_required and field_type != 'checkbox':
                label_text_for_display = f"{label_text_original} *"

            is_add_op = title.lower().startswith("додати")
            if field_conf.get('edit_only', False) and is_add_op:
                continue

            current_value_to_use = None
            if current_data and field_name in current_data:
                current_value_to_use = current_data[field_name]
            elif 'default' in field_conf:
                current_value_to_use = field_conf['default']

            widget: QWidget

            if field_type == 'line_edit':
                widget = QLineEdit(str(current_value_to_use) if current_value_to_use is not None else '')
                if field_conf.get('readonly', False): widget.setReadOnly(True)
            elif field_type == 'checkbox':
                widget = QCheckBox(label_text_original if label_text_original else field_name)
                widget.setChecked(bool(current_value_to_use) if current_value_to_use is not None else False)
                label_text_for_display = None
            elif field_type == 'text_edit':
                widget = QTextEdit(str(current_value_to_use) if current_value_to_use is not None else '')
                widget.setMinimumHeight(80)
                if field_conf.get('readonly', False): widget.setReadOnly(True)
            elif field_type == 'combobox':
                combo_widget = QComboBox()
                choices_list = field_conf.get('choices', [])
                if not choices_list and 'choices_provider' in field_conf:
                    choices_list = _get_combobox_choices(field_conf['choices_provider'], db_cursor) if db_cursor else []
                    if not db_cursor:
                         QMessageBox.warning(dialog, "Помилка БД", f"Для поля '{label_text_original}' потрібен курсор БД для choices_provider.")
                for choice in choices_list: combo_widget.addItem(str(choice))
                if current_value_to_use is not None:
                    idx = combo_widget.findText(str(current_value_to_use))
                    if idx != -1: combo_widget.setCurrentIndex(idx)
                widget = combo_widget
            elif field_type == 'combobox_db':
                combo_db_w = QComboBox()
                if db_cursor and not db_cursor.closed:
                    q_str = field_conf.get('query')
                    v_col = field_conf.get('value_col')
                    d_col = field_conf.get('display_col')
                    if q_str and v_col and d_col:
                        try:
                            combo_db_w.addItem("--- Оберіть ---", None)
                            db_cursor.execute(q_str)
                            for row in db_cursor.fetchall():
                                combo_db_w.addItem(str(row[d_col]), row[v_col])
                            if current_value_to_use is not None:
                                for i in range(combo_db_w.count()):
                                    if combo_db_w.itemData(i) == current_value_to_use:
                                        combo_db_w.setCurrentIndex(i); break
                        except psycopg2.Error as e_db_combo:
                            QMessageBox.critical(dialog, "Помилка БД", f"Завантаження для '{label_text_original}': {e_db_combo}")
                    else:
                        QMessageBox.critical(dialog, "Конфігурація", f"Неповна конфігурація combobox_db '{label_text_original}'.")
                else:
                    QMessageBox.warning(dialog, "Помилка БД", f"Для '{label_text_original}' потрібен активний курсор БД.")
                widget = combo_db_w
            elif field_type == 'dynamic_parent_comment_select':
                dynamic_combo = QComboBox()
                none_text = field_conf.get('allow_none_text', "---")
                dynamic_combo.addItem(none_text, None)
                widget = dynamic_combo
            elif field_type == 'author_select':
                author_container = QWidget()
                container_layout = QHBoxLayout(author_container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                line_edit_authors_display = QLineEdit()
                line_edit_authors_display.setReadOnly(True)
                line_edit_authors_display.setPlaceholderText("Автори не обрані")
                initial_author_ids_for_field = []
                if current_value_to_use and isinstance(current_value_to_use, list):
                    initial_author_ids_for_field = current_value_to_use
                line_edit_authors_display.setProperty("selected_author_ids", initial_author_ids_for_field)
                _update_author_display_text_in_dialog(line_edit_authors_display, db_cursor)
                select_authors_button = QPushButton("Обрати авторів...")
                select_authors_button.clicked.connect(
                    lambda checked=False, le=line_edit_authors_display, p_dialog=dialog, crs=db_cursor:
                    _on_author_select_button_clicked_in_dialog(le, p_dialog, crs)
                )
                container_layout.addWidget(line_edit_authors_display, 1)
                container_layout.addWidget(select_authors_button)
                widget = author_container
            else:
                widget = QLineEdit(f"Невідомий тип: {field_type}")
                widget.setReadOnly(True)

            input_widgets[field_name] = widget
            if label_text_for_display:
                form_layout.addRow(label_text_for_display, widget)
            else:
                form_layout.addRow(widget)
    except Exception as e_widget_creation:
        QMessageBox.critical(parent, "Помилка створення віджетів", f"{e_widget_creation}")
        import traceback; traceback.print_exc()
        return None

    for field_conf in fields_config:
        field_name = field_conf.get('name')
        field_type = field_conf.get('type')
        if field_type == 'dynamic_parent_comment_select':
            target_combo_widget = input_widgets.get(field_name)
            depends_on_field_name = field_conf.get('depends_on_field')
            source_combo_widget = input_widgets.get(depends_on_field_name)
            if isinstance(target_combo_widget, QComboBox) and isinstance(source_combo_widget, QComboBox):
                initial_book_id_val = None
                if current_data and depends_on_field_name in current_data:
                    initial_book_id_val = current_data[depends_on_field_name]
                    source_combo_widget.setEnabled(False)
                elif source_combo_widget.currentIndex() > 0 and source_combo_widget.currentData() is not None:
                     initial_book_id_val = source_combo_widget.currentData()
                _populate_parent_comment_combo_external(target_combo_widget, initial_book_id_val, field_conf, db_cursor, dialog)
                current_parent_val_to_set = None
                if current_data and field_name in current_data:
                    current_parent_val_to_set = current_data[field_name]
                if current_parent_val_to_set is not None:
                    for i in range(target_combo_widget.count()):
                        if target_combo_widget.itemData(i) == current_parent_val_to_set:
                            target_combo_widget.setCurrentIndex(i); break
                    else: target_combo_widget.setCurrentIndex(0)
                else: target_combo_widget.setCurrentIndex(0)
                try: source_combo_widget.currentIndexChanged.disconnect()
                except TypeError: pass
                source_combo_widget.currentIndexChanged.connect(
                    lambda _idx, target_c=target_combo_widget, source_c=source_combo_widget, f_c=field_conf:
                    _populate_parent_comment_combo_external(target_c, source_c.currentData(), f_c, db_cursor, dialog)
                )
            else:
                 if title.lower().startswith("додати в 'comment'"):
                    print(f"ERROR: Could not set up dependency for '{field_name}'. Widgets are not QComboBox or not found.")

    buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    form_layout.addRow(buttons)

    if dialog.exec() == QDialog.DialogCode.Accepted:
        results: Dict[str, Any] = {}
        for name_key, main_widget_val in input_widgets.items():
            f_conf_res_loop = next((f_cfg for f_cfg in fields_config if f_cfg['name'] == name_key), None)
            if not f_conf_res_loop: continue
            f_type_res_loop = f_conf_res_loop.get('type', 'line_edit')

            if f_type_res_loop == 'author_select':
                line_edit_authors_in_container = main_widget_val.findChild(QLineEdit)
                if line_edit_authors_in_container:
                    author_ids_prop = line_edit_authors_in_container.property("selected_author_ids")
                    results[name_key] = author_ids_prop if isinstance(author_ids_prop, list) else []
                else:
                    results[name_key] = []
            elif f_type_res_loop == 'dynamic_parent_comment_select' or f_type_res_loop == 'combobox_db':
                if isinstance(main_widget_val, QComboBox): results[name_key] = main_widget_val.currentData()
                else: results[name_key] = None
            elif f_type_res_loop == 'combobox':
                if isinstance(main_widget_val, QComboBox): results[name_key] = main_widget_val.currentText()
                else: results[name_key] = None
            elif isinstance(main_widget_val, QLineEdit):
                results[name_key] = main_widget_val.text().strip()
            elif isinstance(main_widget_val, QTextEdit):
                results[name_key] = main_widget_val.toPlainText().strip()
            elif isinstance(main_widget_val, QCheckBox):
                results[name_key] = main_widget_val.isChecked()
        return results
    return None