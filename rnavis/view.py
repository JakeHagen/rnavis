from rnavis import app
from flask import render_template
import sqlalchemy as sql
from json import dumps
import os

engine = os.environ.get("ENGINE")
engine = sql.create_engine(engine)


@app.route('/')
def index():
    insp = sql.engine.reflection.Inspector.from_engine(engine)
    schemas = [s for s in insp.get_schema_names()
               if s not in ["information_schema", "public"]]
    schemas = [s for s in schemas if 'test' not in s]
    table_dict = {s: ['gene counts', 'nascent counts'] for s in schemas}
    # table_dict = {s: insp.get_table_names(schema=s) for s in schemas}
    # table_dict = {s: [x for x in t] for s, t in table_dict.items()}
    return render_template('index.html', counts_tables=dumps(table_dict))
