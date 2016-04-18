from flask import Flask, render_template, request
import sqlalchemy as sqly
import os
import requests
import json
import config
import pandas
import numpy as np
from sklearn.decomposition import PCA as sklearnPCA
import tmm
import ge

app = Flask(__name__)
engine = sqly.create_engine(config.psql)
meta = sqly.MetaData()
meta.reflect(engine)

@app.route('/', methods = ['GET', 'POST'])
def index():
    errors = []
    results = []
    sample_names = []
    all_tables = list(meta.tables)
    explained_variance = []
    counts_tables = [x for x in all_tables if "pipeline" not in x]


    if request.method == "POST":
        try:
            table = request.form['table']
            rna_exp = ge.gene_expression(pandas.read_sql_table(table, index_col = 'gene', con = engine))
            mat_normed = ge.voom_out(rna_exp)
            sklearn_pca = sklearnPCA(n_components = 4)
            pca_points = sklearn_pca.fit_transform(mat_normed.T)
            explained_variance = sklearn_pca.explained_variance_ratio_
            #explained_variance = [x for x in explained_variance if x >+ .05]
            print(explained_variance)
            #pca_points = pca_points[:,0:len(explained_variance)]
            print(pca_points)
            #pca_points_df = pandas.DataFrame(pca_points, columns = ['pc%s' % x for x in range(len(explained_variance))])
            pca_points_df = pandas.DataFrame(pca_points, columns = ['pc1', 'pc2', 'pc3', 'pc4'])
            pca_points_df['sample'] = rna_exp.samples
            results = pca_points_df.to_dict(orient = 'records')


        except:
            errors.append(
                "Unable to get URL. PLease make sure it's valid and try again."
            )
    return render_template('index.html', results = json.dumps(results),
                            sample_names = sample_names, counts_tables = counts_tables,
                            explained_variance = explained_variance)


if __name__ == '__main__':
    app.run(debug = True)
