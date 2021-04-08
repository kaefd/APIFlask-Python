# import flask
# import json
# from flask import request, jsonify
# import sqlite3
# import controller
# import db
# from db import create_tables

# app = flask.Flask(__name__)
# app.config["DEBUG"] = True


# @app.route('/api/v1/resources/books/all', methods=["GET"])
# def get_books():
#     books = controller.get_books()

#     return jsonify(books)


# @app.route("/api/v1/resources/books", methods=["POST"])
# def insert_book():
#     bookz = request.get_json()
#     author = bookz["author"]
#     published = bookz["published"]
#     first_sentence = bookz["first_sentence"]
#     title = bookz["title"]
#     result = controller.insert_book(author, published, first_sentence, title)
#     return jsonify(result)


# @app.route("/api/v1/resources/books", methods=["PUT"])
# def update_book():
#     bookz = request.get_json()
#     id = bookz["id"]
#     author = bookz["author"]
#     published = bookz["published"]
#     first_sentence = bookz["first_sentence"]
#     title = bookz["title"]
#     result = controller.update_book(
#         id, author, published, first_sentence, title)
#     return jsonify(result)


# @app.route("/api/v1/resources/books/<id>", methods=["DELETE"])
# def delete_book(id):
#     result = controller.delete_book(id)
#     return jsonify(result)


# @app.route("/api/v1/resources/books/<id>", methods=["GET"])
# def get_book_by_id(id):
#     book = controller.get_by_id(id)
#     return jsonify(book)


# """
# Enable CORS. Disable it if you don't need CORS
# """


# @app.after_request
# def after_request(response):
#     response.headers["Access-Control-Allow-Origin"] = "127.0.0.1:5000"
#     response.headers["Access-Control-Allow-Credentials"] = "true"
#     response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS, PUT, DELETE"
#     response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
#     return response


# if __name__ == "__api__":
#     create_tables()
#     """
#     Here you can change debug and port
#     Remember that, in order to make this API functional, you must set debug in False
#     """
#     app.run()
import json
import sqlite3
from sqlite3 import Error

from flask import abort, Flask, jsonify, redirect, request, url_for


def create_connection():
    """
    Fungsi untuk terhubung dengan database SQLite.
    """
    try:
        return sqlite3.connect('books.db')
    except:
        print('Error! cannot create the database connection.')
        return None


def create_table():
    """
    Fungsi untuk membuat table 'books' di database, apabila tidak ada.
    """
    try:
        with create_connection() as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS books(
                    id primary key,
                    published INT,
                    author VARCHAR,
                    title VARCHAR,       
                    first_sentence VARCHAR
                );
            ''')
    except Error as e:
        print(e)


def get(id=None, is_set=False):
    """
    Fungsi untuk mendapatkan data dari table 'books'.
    Key parameter id adalah integer dan tidak mandatory.
    Key parameter is_set adalah boolean dengan default nilai False.
    """
    with create_connection() as conn:
        c = conn.cursor()

        if id:
            c.execute(
                '''
                    SELECT *
                    FROM books
                    WHERE id = ?;
                ''',
                (id,)
            )

            row = c.fetchall()

            if row:
                row = row[0]
                data = {
                    'id': row[0],
                    'published': row[1],
                    'author': row[2],
                    'title': row[3],
                    'first_sentence': row[4]
                }
            else:
                data = []
        else:
            c.execute(
                '''
                    SELECT *
                    FROM books;
                ''',
            )

            data = [
                {
                    'id': row[0],
                    'published': row[1],
                    'author': row[2],
                    'title': row[3],
                    'first_sentence': row[4]
                } for row in c.fetchall()
            ]

    if data:
        data = {
            'code': 200,
            'message': 'buku berhasil ditemukan.',
            'data': data
        }

        if is_set:
            data['code'] = 201
            data['message'] = 'Data barhasil tersimpan.'
    else:
        abort(404)

    return data


def post():
    """
    Fungsi untuk menambahkan data ke table 'books'.
    Key parameter name adalah string dan mandatory.
    """
    with create_connection() as conn:
        c = conn.cursor()

        if request.json:
            add = json.loads(request.data).get(
                'author, first_sentence, published, title')
        else:
            add = request.form.get('author, first_sentence, published, title')

        if add:
            c.execute(
                '''
                    INSERT INTO books(author, first_sentence, published, title)
                                VALUES(?, ?, ?, ?, ?);
                ''',
                (author, first_sentence, published, title)
            )

            id = c.lastrowid
        else:
            abort(400)

    return get(id, True)


def put(id):
    """
    Fungsi untuk mengubah salah satu data di table 'books'.
    Key parameter id adalah integer dan tidak mandatory.
    Key parameter name adalah string dan mandatory.
    """
    with create_connection() as conn:
        c = conn.cursor()

        if request.json:
            add = json.loads(
                request.data
            ).get('author, first_sentence, published, title')
        else:
            add = request.form.get('author, first_sentence, published, title')

        if add:
            c.execute(
                '''
                    UPDATE books
                    SET author = ?
                    published = ?
                    first_sentence = ?
                    title = ?
                    WHERE author = ?;
                ''',
                (author, first_sentence, published, title, id)
            )
        else:
            abort(400)

    return get(id, True)


def delete(id):
    """
    Fungsi untuk menghapus salah satu data di table 'books'.
    Key parameter id adalah integer dan tidak mandatory.
    """
    with create_connection() as conn:
        c = conn.cursor()

        c.execute(
            '''
                DELETE
                FROM books
                WHERE id = ?;
            ''',
            (id,)
        )

    return {
        'code': 200,
        'message': 'Data berhasil dihapus.',
        'data': None
    }


def response_api(data):
    """
    Fungsi untuk menampilkan data kedalam format Json.
    Key parameter data adalah dictionary dan mandatory.
    Berikut ini adalah contoh pengisian key parameter data:
    data = {
        'code': 200,
        'message': 'berhasil ditemukan.',
        'data': [
            {
                'id': 1,
                'name': 'Kuda'
            }
        ]
    }
    """
    return (
        jsonify(**data),
        data['code']
    )


app = Flask(__name__)


@app.errorhandler(400)
def bad_request(e):
    return response_api({
        'code': 400,
        'message': 'Ada kekeliruan input saat melakukan request.',
        'data': None
    })


@app.errorhandler(404)
def not_found(e):
    return response_api({
        'code': 404,
        'message': ' tidak berhasil ditemukan.',
        'data': None
    })


@app.errorhandler(405)
def method_not_allowed(e):
    return response_api({
        'code': 405,
        'message': 'tidak berhasil ditemukan.',
        'data': None
    })


@app.errorhandler(500)
def internal_server_error(e):
    return response_api({
        'code': 500,
        'message': 'Mohon maaf, ada gangguan pada server kami.',
        'data': None
    })


@app.route('/')
def root():
    return 'RESTful API Sederhana Menggunakan Flask'


@app.route('/books', methods=['GET', 'POST'])
@app.route('/books/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def books(id=None):
    """
    RESTful API /books.
    """
    if request.method == 'GET':
        data = get(id)
    if request.method == 'POST':
        data = post()
    elif request.method == 'PUT':
        data = put(id)
    elif request.method == 'DELETE':
        data = delete(id)

    return response_api(data)


if __name__ == '__main__':
    create_table()
    app.run(debug=True)
