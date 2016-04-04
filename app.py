from flask import Flask, render_template, request
import sqlalchemy as sqly
import os
import requests
import json
import config
import pandas
import numpy

app = Flask(__name__)
engine = sqly.create_engine(config.psql)
meta = sqly.MetaData()
meta.reflect(engine)

@app.route('/', methods = ['GET', 'POST'])
def index():
    errors = []
    results = {}
    sample_names = []
    all_tables = list(meta.tables)

    try:
        counts_tables = all_tables#.remove('table_updates')
    except:
        pass

    if request.method == "POST":
        try:
            table = request.form['table']
            test = pandas.read_sql_table(table, index_col = 'gene', con = engine)
            ge = gene_expression(test)
            results = ge.z_df.to_dict(orient = 'records')
            sample_names = ge.samples.tolist()

        except:
            errors.append(
                "Unable to get URL. PLease make sure it's valid and try again."
            )
    return render_template('index_new.html', results = json.dumps(results),
                            sample_names = sample_names, counts_tables = counts_tables)

if __name__ == '__main__':
    app.run(debug = True)
