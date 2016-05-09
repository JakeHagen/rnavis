from flask import Flask, render_template, request
import sqlalchemy as sqly
import json
import config
import pandas
import ge
import combat

app = Flask(__name__)
engine = sqly.create_engine(config.psql)
# meta = sqly.MetaData()
# meta.reflect(engine)


@app.route('/')
def index():
    insp = sqly.engine.reflection.Inspector.from_engine(engine)
    all_tables = insp.get_table_names()
    # get_schema_names()
    # all_tables = list(meta.tables)
    counts_tables = [x for x in all_tables if "voom" not in x]
    return render_template('index.html', counts_tables=counts_tables)


@app.route('/data', methods=['GET', 'POST'])
def data():
    table = request.form.get("postgres_table", None)
    try:
        rna_exp = ge.gene_expression(pandas.read_sql_table(table + "_voom", index_col='gene', con=engine))
        results = ge.pca_json(rna_exp, voom=False)
    except:
        rna_exp = ge.gene_expression(pandas.read_sql_table(table, index_col='gene', con=engine))
        voom_df = ge.voom_out(rna_exp)
        voom_df.to_sql(table + "_voom", con=engine)
        results = ge.pca_json(rna_exp, voom=True)
    return json.dumps(results)


@app.route('/batch', methods=['GET', 'POST'])
def batch():
    j = request.get_json('j')
    table = j['table']
    rna_exp = ge.gene_expression(pandas.read_sql_table(table + "_voom", index_col='gene', con=engine))
    batch_list = list(j['batch'])
    rna_exp_batch = ge.gene_expression(combat.combat(rna_exp.df, batch=batch_list))
    combat_results = ge.pca_json(rna_exp_batch, voom=False)
    return json.dumps(combat_results)

if __name__ == '__main__':
    app.run(debug=True)
