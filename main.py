import csv
import io

from fasthtml.common import *
from fastsql import *
import sqlite3 
from sqlite_minutils.db import NotFoundError
from logging import get_logger


app, route = fast_app()
logger = get_logger("fasthtml","INFO")

def init_db():
    conn = sqlite3.connect("todo.db")
    conn.execute("CREATE TABLE IF NOT EXISTS todo (id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, status TEXT NOT NULL)")
    conn.close()

init_db()



@route('/')
def index():
    return Div(P('Hello World!'), hx_get="/change")

serve()