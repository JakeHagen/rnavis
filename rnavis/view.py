from rnavis import app
from flask import render_template
import sqlalchemy as sql
from json import dumps
import rnavis.config as config


engine = sql.create_engine(config.psql)


@app.route('/')
def index():
    insp = sql.engine.reflection.Inspector.from_engine(engine)
    schemas = insp.get_schema_names()
    table_dict = {s: insp.get_table_names(schema=s) for s in schemas}
    table_dict = {s: [x for x in t if "voom" not in x]
                  for s, t in table_dict.items()}
    return render_template('index.html', counts_tables=dumps(table_dict))
