import sqlite3
from logging import get_logger

from fasthtml.common import Div, P, fast_app, serve
from fastsql import *

app, route = fast_app()
logger = get_logger("fasthtml", "INFO")


def init_db():
    conn = sqlite3.connect("todo.db")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS todo (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, status TEXT NOT NULL)"
    )
    conn.close()


init_db()


@route("/")
def index():
    return Div(P("Hello World!"), hx_get="/change")


serve()
