from flask import Flask, render_template, request
import sqlalchemy as sqly
import os
import requests
import json
import config
import pandas
import numpy as np

import tmm
import ge
import combat

app = Flask(__name__)
engine = sqly.create_engine(config.psql)
meta = sqly.MetaData()
meta.reflect(engine)

@app.route('/')
def index():
    all_tables = list(meta.tables)
    counts_tables = [x for x in all_tables if "pipeline" not in x]
    return render_template('index.html', counts_tables = counts_tables)                            #sample_names = sample_names, #explained_variance = explained_variance)

@app.route('/data', methods = ['GET', 'POST'])
def data():
    table = request.form.get("postgres_table", "don_scott_high_fat_gene_counts")
    rna_exp = ge.gene_expression(pandas.read_sql_table(table, index_col = 'gene',
                                    con = engine))
    results = ge.pca_json(rna_exp)
    return json.dumps(results)

@app.route('/batch', methods = ['GET', 'POST'])
def batch():
    batch_list = request.args.get(['batch'])
    #        print(batch_list)
    #        mat_combat = combat.combat(mat_normed, batch = [1,1,1,1,2,2,2,1,1,1,1,2,2,2],
    #            model = np.array([[1,1], [1,1], [1,1], [1,1], [1,1], [1,1], [1,1],
    #                            [1,0], [1,0], [1,0], [1,0], [1,0], [1,0], [1,0]]))
    #        sklearn_pca_combat = sklearnPCA(n_components = 4)
    #        pca_points_combat = sklearn_pca_combat.fit_transform(mat_combat.T)
    #        pca_points_df_combat = pandas.DataFrame(pca_points_combat, columns = ['pc1', 'pc2', 'pc3', 'pc4'])
    #        pca_points_df_combat['sample'] = rna_exp.samples
    #        print(pca_points_df_combat)
    #        results2 = pca_points_df_combat.to_dict(orient = 'records')
    data = json.loads(request.form['bat'])
    l = list(data)
    print(l)
    #return json.dumps(request.form['userName'])
    return render_template('test.html')

if __name__ == '__main__':
    app.run(debug = True)
