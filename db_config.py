# db_config.py
from typing import List, Dict, Any

DB_CONFIG: Dict[str, str] = {
    'dbname': 'library_db_2',
    'user': 'postgres',
    'password': '9155',
    'host': 'localhost',
    'port': '5432'
}

SPECIAL_QUERIES: List[Dict[str, Any]] = [
    {
        "name": "Знайти книги користувача за ім'ям",
        "sql": """
               SELECT b.title AS "Назва книги", b.isbn AS "ISBN", bl.status AS "Статус читання"
               FROM public.book b
                        JOIN public.book_list bl ON b.book_id = bl.book_id
                        JOIN public."user" u ON bl.user_id = u.user_id
               WHERE u.username ILIKE %s;
               """,
        "params": [{"name": "username", "label": "Ім'я користувача (частково):", "type": "line_edit"}]
    },
    # db_config.py, SPECIAL_QUERIES (змінений запит)
    {
        "name": "Показати всіх авторів та кількість їхніх книг",
        "sql":
            """
            SELECT a.first_name      AS "Ім'я",
                   a.last_name       AS "Прізвище",
                   COUNT(ba.book_id) AS "К-сть книг"
            FROM public.author a
                     LEFT JOIN public.book_author ba ON a.author_id = ba.author_id
            GROUP BY a.author_id, a.first_name, a.last_name
            ORDER BY "К-сть книг" DESC, a.last_name;
            """,
        "params": []
    },#
    {
        "name": "TOP-N книг за найвищим середнім рейтингом",
        "sql": """
            SELECT
                b.title AS "Назва книги",
                STRING_AGG(DISTINCT (auth.first_name || ' ' || auth.last_name), ', ') AS "Автори",
                ROUND(
                    COALESCE(AVG(
                        CASE e.rate
                            WHEN 'OneStar' THEN 1.0
                            WHEN 'TwoStars' THEN 2.0
                            WHEN 'ThreeStars' THEN 3.0
                            WHEN 'FourStars' THEN 4.0
                            WHEN 'FiveStars' THEN 5.0
                            ELSE 0.0 -- Або NULL, якщо оцінки без зірок не повинні враховуватися
                        END
                    ), 0.0),2) AS "Середній рейтинг",
                COUNT(e.evaluation_id) AS "Кількість оцінок"
            FROM
                public.book b
            LEFT JOIN
                public.evaluation e ON b.book_id = e.book_id
            LEFT JOIN
                public.book_author ba ON b.book_id = ba.book_id
            LEFT JOIN
                public.author auth ON ba.author_id = auth.author_id
            WHERE b.is_archived = false
            GROUP BY
                b.book_id, b.title
            ORDER BY
                "Середній рейтинг" DESC, "Кількість оцінок" DESC
            LIMIT %s;
        """,
        "params": [{"name": "limit_n", "label": "Кількість книг (N):", "type": "line_edit"}]
    },
    {
        "name": "Найактивніші користувачі (за кількістю коментарів)",
        "sql": """
            SELECT
                u.username AS "Ім'я користувача",
                COUNT(c.comment_id) AS "Кількість коментарів"
            FROM
                public."user" u
            LEFT JOIN
                public.comment c ON u.user_id = c.user_id
            GROUP BY
                u.user_id, u.username
            ORDER BY
                "Кількість коментарів" DESC, u.username
            LIMIT 20; -- Обмежимо для прикладу
        """,
        "params": []
    },

    {
        "name": "Книги зі статусом 'Планую' для користувача",
        "sql": """
               SELECT u.username    AS "Користувач",
                      b.title       AS "Назва книги",
                      bl.date_added AS "Дата додавання до списку"
               FROM public.book_list bl
                        JOIN
                    public."user" u ON bl.user_id = u.user_id
                        JOIN
                    public.book b ON bl.book_id = b.book_id
               WHERE u.username ILIKE %s
                 AND bl.status = 'Хочу прочитати' -- Або ваш відповідний ENUM 'Planning'/'WantToRead'
                 AND b.is_archived = false
               ORDER BY
                   bl.date_added DESC;
               """,
        "params": [{"name": "username_plan", "label": "Ім'я користувача:", "type": "line_edit"}]
    },
    {
        "name": "Користувачі без оцінок, але з > N книг у списках",
        "sql": """
               SELECT u.username                 AS "Користувач",
                      COUNT(DISTINCT bl.book_id) AS "Кількість книг у списках"
               FROM public."user" u
                        JOIN
                    public.book_list bl ON u.user_id = bl.user_id
                        LEFT JOIN
                    public.evaluation e ON u.user_id = e.user_id -- Перевіряємо, чи є хоч одна оцінка від користувача
               WHERE e.evaluation_id IS NULL -- Користувач не має жодної оцінки
               GROUP BY u.user_id, u.username
               HAVING COUNT(DISTINCT bl.book_id) > %s
               ORDER BY "Кількість книг у списках" DESC, u.username;
               """,
        "params": [{"name": "min_books_in_list", "label": "Мін. кількість книг у списках (N):", "type": "line_edit"}]
    },
    {
        "name": "Детальна історія читання та оцінок для книги",
        "sql": """
               SELECT b.title         AS "Книга",
                      u_list.username AS "Хто додав до списку",
                      bl.status       AS "Статус у списку",
                      bl.date_added   AS "Дата додавання до списку",
                      u_eval.username AS "Хто оцінив",
                      e.rate          AS "Оцінка",
                      e.date_rated    AS "Дата оцінки"
               FROM public.book b
                        LEFT JOIN
                    public.book_list bl ON b.book_id = bl.book_id
                        LEFT JOIN
                    public."user" u_list ON bl.user_id = u_list.user_id
                        LEFT JOIN
                    public.evaluation e ON b.book_id = e.book_id AND (bl.user_id = e.user_id OR bl.user_id IS NULL)
                        -- Показуємо оцінку, якщо вона від того ж користувача, що й запис у book_list, 
                        -- або всі оцінки, якщо книга не в чиємусь списку (але це менш логічно для "історії читання")
                        -- Можливо, краще окремий JOIN для всіх оцінок книги, якщо потрібно.
                        LEFT JOIN
                    public."user" u_eval ON e.user_id = u_eval.user_id
               WHERE b.title ILIKE %s -- Пошук книги за назвою
                 AND b.is_archived = false
               ORDER BY
                   bl.date_added, e.date_rated;
               """,
        "params": [{"name": "book_title_history", "label": "Назва книги (частково):", "type": "line_edit"}]
    },
    {
        "name": "Статистика за жанрами (к-сть книг, сер. сторінок, сер. рейтинг)",
        "sql": """
               SELECT b.genre::text AS "Жанр", COUNT(DISTINCT b.book_id) AS "Кількість книг",
                      TRUNC(AVG(b.page_number), 0) AS "Сер. к-сть сторінок", 
                      ROUND(
                          COALESCE(AVG(
                                           CASE e.rate
                                               WHEN 'OneStar' THEN 1.0
                                               WHEN 'TwoStars' THEN 2.0
                                               WHEN 'ThreeStars' THEN 3.0
                                               WHEN 'FourStars' THEN 4.0
                                               WHEN 'FiveStars' THEN 5.0
                                               ELSE NULL
                                               END
                                   ), 0.0),2) AS "Середній рейтинг жанру"
               FROM public.book b
                        LEFT JOIN
                    public.evaluation e ON b.book_id = e.book_id
               WHERE b.is_archived = false
               GROUP BY b.genre
               ORDER BY "Кількість книг" DESC, "Жанр";
               """,
        "params": []
    },
# db_config.py
# ... (попередні запити, включаючи виправлені 3, 5 та 10) ...
    {
        "name": "Книги без оцінок, але в списках користувачів",
        "sql": """
            SELECT DISTINCT
                b.title AS "Назва книги",
                b.genre::text AS "Жанр"
            FROM
                public.book b
            JOIN
                public.book_list bl ON b.book_id = bl.book_id -- Книга має бути хоча б в одному списку
            LEFT JOIN
                public.evaluation e ON b.book_id = e.book_id
            WHERE
                b.is_archived = false
                AND e.evaluation_id IS NULL -- Для книги немає жодної оцінки
            ORDER BY
                b.title;
        """,
        "params": []
    },
    {
        "name": "Рейтинг книги vs Середній рейтинг її жанру",
        "sql": """
               WITH BookRatings AS ( -- Розрахунок середнього рейтингу для кожної книги
                   SELECT b.book_id,
                          b.title,
                          b.genre,
                          ROUND(COALESCE(AVG(
                                                 CASE e.rate
                                                     WHEN 'OneStar' THEN 1.0
                                                     WHEN 'TwoStars' THEN 2.0
                                                     WHEN 'ThreeStars' THEN 3.0
                                                     WHEN 'FourStars' THEN 4.0
                                                     WHEN 'FiveStars' THEN 5.0
                                                     ELSE NULL
                                                     END
                                         ), 0.0), 2) AS avg_book_rating
                   FROM public.book b
                            LEFT JOIN public.evaluation e ON b.book_id = e.book_id
                   WHERE b.is_archived = false
                   GROUP BY b.book_id, b.title, b.genre),
                    GenreAvgRatings AS ( -- Розрахунок середнього рейтингу для кожного жанру
                        SELECT br.genre,
                               ROUND(AVG(br.avg_book_rating), 2) AS avg_genre_rating
                        FROM BookRatings br
                        GROUP BY br.genre)
               SELECT br.title                                              AS "Назва книги",
                      br.genre::text AS "Жанр", br.avg_book_rating AS "Рейтинг книги",
                      gar.avg_genre_rating                                  AS "Сер. рейтинг жанру",
                      ROUND((br.avg_book_rating - gar.avg_genre_rating), 2) AS "Різниця"
               FROM BookRatings br
                        JOIN
                    GenreAvgRatings gar ON br.genre = gar.genre
               WHERE br.title ILIKE %s
               ORDER BY
                   "Різниця" DESC, br.title;
               """,
        "params": [{"name": "book_title_compare", "label": "Назва книги (частково):", "type": "line_edit"}]
    },
    # db_config.py
    # db_confi
    {
        "name": "Прочитано, але не оцінено користувачем", # Запит 16
        "sql": """
            SELECT
                u.username AS "Користувач",
                b.title AS "Назва книги",
                (SELECT STRING_AGG(DISTINCT (auth.first_name || ' ' || auth.last_name), ', ')
                 FROM public.book_author ba_inner
                 JOIN public.author auth ON ba_inner.author_id = auth.author_id
                 WHERE ba_inner.book_id = b.book_id) AS "Автори",
                bl.date_added AS "Дата позначки 'Прочитано'"
            FROM
                public.book_list bl
            JOIN
                public."user" u ON bl.user_id = u.user_id
            JOIN
                public.book b ON bl.book_id = b.book_id
            WHERE
                u.username ILIKE %s
                AND bl.status = 'Хочу прочитати' -- АБО ВАШЕ ЗНАЧЕННЯ ДЛЯ "ПРОЧИТАНО"
                AND b.is_archived = false
                AND NOT EXISTS ( -- Перевірка, що для цієї книги та користувача немає оцінки
                    SELECT 1
                    FROM public.evaluation e
                    WHERE e.user_id = u.user_id AND e.book_id = b.book_id
                )
            ORDER BY
                bl.date_added DESC, b.title;
        """,
        "params": [
            {"name": "username_completed_no_eval", "label": "Ім'я користувача:", "type": "line_edit"}
        ]
    },

    {
        "name": "Книги з 'поляризуючими' оцінками", # Новий Запит 15
        "sql": """
            WITH BookEvaluationStats AS (
                SELECT
                    e.book_id,
                    MIN(CASE e.rate 
                        WHEN 'OneStar' THEN 1 WHEN 'TwoStars' THEN 2 WHEN 'ThreeStars' THEN 3 
                        WHEN 'FourStars' THEN 4 WHEN 'FiveStars' THEN 5 ELSE NULL END) as min_numeric_rate,
                    MAX(CASE e.rate 
                        WHEN 'OneStar' THEN 1 WHEN 'TwoStars' THEN 2 WHEN 'ThreeStars' THEN 3 
                        WHEN 'FourStars' THEN 4 WHEN 'FiveStars' THEN 5 ELSE NULL END) as max_numeric_rate,
                    COUNT(e.evaluation_id) as num_evaluations
                FROM public.evaluation e
                GROUP BY e.book_id
                HAVING COUNT(e.evaluation_id) >= %s -- Книга повинна мати хоча б N оцінок
            )
            SELECT
                b.title AS "Назва книги",
                (SELECT STRING_AGG(DISTINCT (auth.first_name || ' ' || auth.last_name), ', ')
                 FROM public.book_author ba_inner
                 JOIN public.author auth ON ba_inner.author_id = auth.author_id
                 WHERE ba_inner.book_id = b.book_id) AS "Автори",
                b.genre::text AS "Жанр",
                bes.min_numeric_rate AS "Мін. оцінка",
                bes.max_numeric_rate AS "Макс. оцінка",
                bes.num_evaluations AS "К-сть оцінок"
            FROM public.book b
            JOIN BookEvaluationStats bes ON b.book_id = bes.book_id
            WHERE b.is_archived = false
              AND bes.min_numeric_rate <= %s -- Є низькі оцінки (наприклад, <= 2)
              AND bes.max_numeric_rate >= %s -- Є високі оцінки (наприклад, >= 4)
            ORDER BY bes.num_evaluations DESC, b.title;
        """,
        "params": [
            {"name": "min_evals_for_polarizing", "label": "Мін. к-сть оцінок для аналізу:", "type": "line_edit", "param_type": "integer"},
            {"name": "low_rate_threshold", "label": "Поріг низької оцінки (<=):", "type": "line_edit", "param_type": "integer"},
            {"name": "high_rate_threshold", "label": "Поріг високої оцінки (>=):", "type": "line_edit", "param_type": "integer"}
        ]
    },
# db_config.py
# ... (попередні запити, включаючи Запит 17) ...
    # --- НОВІ ЗАПИТИ (18-21) ---
    {
        "name": "Детальний список книг користувача з оцінками", # Запит 18
        "sql": """
            SELECT
                u.username AS "Користувач",
                b.title AS "Назва книги",
                (SELECT STRING_AGG(DISTINCT (auth.first_name || ' ' || auth.last_name), ', ')
                 FROM public.book_author ba_inner
                 JOIN public.author auth ON ba_inner.author_id = auth.author_id
                 WHERE ba_inner.book_id = b.book_id) AS "Автори",
                bl.status AS "Статус читання",
                bl.date_added AS "Дата додавання до списку",
                b.average_rating AS "Сер. рейтинг книги (загальний)",
                CASE e_user.rate -- Оцінка саме цього користувача
                    WHEN 'OneStar' THEN 1 WHEN 'TwoStars' THEN 2 WHEN 'ThreeStars' THEN 3
                    WHEN 'FourStars' THEN 4 WHEN 'FiveStars' THEN 5 ELSE NULL
                END AS "Оцінка користувача",
                e_user.date_rated AS "Дата оцінки користувачем"
            FROM public.book_list bl
            JOIN public."user" u ON bl.user_id = u.user_id
            JOIN public.book b ON bl.book_id = b.book_id
            LEFT JOIN public.evaluation e_user ON e_user.book_id = b.book_id AND e_user.user_id = u.user_id
            WHERE u.username ILIKE %s AND b.is_archived = false
            ORDER BY bl.date_added DESC, b.title;
        """,
        "params": [{"name": "username_detailed_list", "label": "Ім'я користувача (частково):", "type": "line_edit"}]
    },
    {
        "name": "Книги користувача в статусі X з оцінкою > Y", # Запит 19
        "sql": """
            SELECT
                u.username AS "Користувач",
                b.title AS "Назва книги",
                bl.status AS "Статус",
                CASE e.rate
                    WHEN 'OneStar' THEN 1 WHEN 'TwoStars' THEN 2 WHEN 'ThreeStars' THEN 3
                    WHEN 'FourStars' THEN 4 WHEN 'FiveStars' THEN 5 ELSE NULL
                END AS "Оцінка користувача"
            FROM public.book_list bl
            JOIN public."user" u ON bl.user_id = u.user_id
            JOIN public.book b ON bl.book_id = b.book_id
            JOIN public.evaluation e ON e.book_id = b.book_id AND e.user_id = u.user_id -- JOIN, бо потрібна оцінка
            WHERE 
                u.username ILIKE %s
                AND bl.status = %s -- Параметр для статусу (точне значення ENUM)
                AND CASE e.rate 
                        WHEN 'OneStar' THEN 1.0 WHEN 'TwoStars' THEN 2.0 
                        WHEN 'ThreeStars' THEN 3.0 WHEN 'FourStars' THEN 4.0 
                        WHEN 'FiveStars' THEN 5.0 ELSE 0.0 
                    END > %s          -- Параметр для мінімальної оцінки
                AND b.is_archived = false
            ORDER BY b.title;
        """,
        "params": [
            {"name": "username_status_rating", "label": "Ім'я користувача (частково):", "type": "line_edit"},
            {"name": "reading_status_filter", "label": "Статус (точне значення ENUM):", "type": "line_edit"},
            {"name": "min_user_rating_filter", "label": "Мін. оцінка користувача (1-5):", "type": "line_edit", "param_type": "float"}
        ]
    },
    {
        "name": "Автори та середня к-сть сторінок їхніх книг", # Запит 20
        "sql": """
            SELECT
                a.first_name || ' ' || a.last_name AS "Автор",
                COUNT(b.book_id) AS "Кількість книг",
                TRUNC(AVG(b.page_number), 0) AS "Сер. к-сть сторінок"
            FROM public.author a
            JOIN public.book_author ba ON a.author_id = ba.author_id
            JOIN public.book b ON ba.book_id = b.book_id
            WHERE b.is_archived = false AND b.page_number IS NOT NULL
            GROUP BY a.author_id, a.first_name, a.last_name
            HAVING COUNT(b.book_id) > 0 -- Показувати авторів, у яких є хоча б одна неархівована книга з кількістю сторінок
            ORDER BY "Кількість книг" DESC, "Автор";
        """,
        "params": []
    },
    {
        "name": "Автори, чиї книги найчастіше планують прочитати", # Запит 21
        "sql": """
            SELECT
                a.first_name || ' ' || a.last_name AS "Автор",
                COUNT(bl.book_list_id) AS "К-сть додавань до 'Планую'"
            FROM public.author a
            JOIN public.book_author ba ON a.author_id = ba.author_id
            JOIN public.book b ON ba.book_id = b.book_id
            JOIN public.book_list bl ON b.book_id = bl.book_id
            WHERE bl.status = 'Хочу прочитати' -- ЗАМІНІТЬ 'Planning' НА ВАШЕ КОРЕКТНЕ ENUM ЗНАЧЕННЯ ДЛЯ "ПЛАНУЮ"
              AND b.is_archived = false
            GROUP BY a.author_id, a.first_name, a.last_name
            ORDER BY "К-сть додавань до 'Планую'" DESC, "Автор"
            LIMIT 20; -- Показати топ-20
        """,
        "params": []
    },
    {
        "name": "Книги, що довго 'читаються' (довше N місяців)",  # Запит 22
        "sql": """
               SELECT u.username                          AS "Користувач",
                      b.title                             AS "Назва книги",
                      bl.date_added                       AS "Дата додавання як 'Читаю'",
                      (CURRENT_DATE - bl.date_added) / 30 AS "Приблизно місяців у статусі"
               FROM public.book_list bl
                        JOIN public."user" u ON bl.user_id = u.user_id
                        JOIN public.book b ON bl.book_id = b.book_id
               WHERE bl.status = 'Читаю' -- ЗАМІНІТЬ 'Читаю' НА ВАШЕ КОРЕКТНЕ ENUM ЗНАЧЕННЯ
                 AND b.is_archived = false
                 AND bl.date_added <= (CURRENT_DATE - CAST((%s || ' months') AS INTERVAL))
               ORDER BY "Приблизно місяців у статусі" DESC, u.username, b.title;
               """,
        "params": [
            {"name": "months_stuck_reading", "label": "К-сть місяців у статусі 'Читаю':", "type": "line_edit",
             "param_type": "integer"}
        ]
    },
    {
        "name": "Автори, що пишуть у >= N жанрах",  # Запит 28
        "sql": """
               WITH AuthorGenreCounts AS (SELECT a.author_id,
                                                 a.first_name || ' ' || a.last_name AS author_name,
                                                 COUNT(DISTINCT b.genre)            as genre_count
                                          FROM public.author a
                                                   JOIN public.book_author ba ON a.author_id = ba.author_id
                                                   JOIN public.book b ON ba.book_id = b.book_id
                                          WHERE b.is_archived = false
                                            AND b.genre IS NOT NULL
                                          GROUP BY a.author_id, a.first_name, a.last_name
                                          HAVING COUNT(DISTINCT b.genre) >= %s)
               SELECT agc.author_name                                                                 AS "Автор",
                      agc.genre_count                                                                 AS "Кількість різних жанрів",
                      STRING_AGG(DISTINCT b_details.genre::text, ', ' ORDER BY b_details.genre::text) AS "Жанри",
                      COUNT(DISTINCT b_details.book_id)                                               AS "Всього книг автора (неархівованих)"
               FROM AuthorGenreCounts agc
                        JOIN public.book_author ba_details ON agc.author_id = ba_details.author_id
                        JOIN public.book b_details ON ba_details.book_id = b_details.book_id
               WHERE b_details.is_archived = false
               GROUP BY agc.author_id, agc.author_name, agc.genre_count
               ORDER BY agc.genre_count DESC, "Всього книг автора (неархівованих)" DESC, agc.author_name;
               """,
        "params": [
            {"name": "min_genres_for_author", "label": "Мін. жанрів для автора:", "type": "line_edit",
             "param_type": "integer"}
        ]
    },
    {
        "name": "Топ користувачів за кількістю прочитаних сторінок",  # Запит 29
        "sql": """
               SELECT u.username         AS "Користувач",
                      SUM(b.page_number) AS "Всього сторінок прочитано"
               FROM public."user" u
                        JOIN public.book_list bl ON u.user_id = bl.user_id
                        JOIN public.book b ON bl.book_id = b.book_id
               WHERE bl.status = 'Прочитано'   -- ЗАМІНІТЬ 'Прочитано' НА ВАШЕ КОРЕКТНЕ ENUM ЗНАЧЕННЯ
                 AND b.is_archived = false
                 AND b.page_number IS NOT NULL -- Враховувати тільки книги з вказаною кількістю сторінок
               GROUP BY u.user_id, u.username
               HAVING SUM(b.page_number) > 0
               ORDER BY "Всього сторінок прочитано" DESC LIMIT 5; -- Показати топ-20
               """,
        "params": []
    },
    {
        "name": "Жанри з найбільшою сер. к-стю коментарів на книгу",  # Запит 30
        "sql": """
               WITH BookCommentCounts AS (SELECT b.book_id,
                                                 b.genre,
                                                 COUNT(c.comment_id) as comment_count_for_book
                                          FROM public.book b
                                                   LEFT JOIN public.comment c ON b.book_id = c.book_id
                                          WHERE b.is_archived = false
                                          GROUP BY b.book_id, b.genre)
               SELECT bcc.genre::text AS "Жанр", COUNT(DISTINCT bcc.book_id) AS "Кількість книг в жанрі",
                      ROUND(AVG(bcc.comment_count_for_book), 2) AS "Сер. к-сть коментарів на книгу"
               FROM BookCommentCounts bcc
               GROUP BY bcc.genre
               HAVING COUNT(DISTINCT bcc.book_id) >= %s -- Враховувати жанри з хоча б N книгами
               ORDER BY "Сер. к-сть коментарів на книгу" DESC, "Жанр";
               """,
        "params": [
            {"name": "min_books_for_genre_comment_avg", "label": "Мін. книг в жанрі:", "type": "line_edit",
             "param_type": "integer"}
        ]
    }

]

