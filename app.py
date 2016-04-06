from flask import Flask, render_template, request
import sqlalchemy as sqly
import os
import requests
import json
import config
import pandas
import numpy
from sklearn.decomposition import PCA as sklearnPCA

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

    try:
        counts_tables = all_tables#.remove('table_updates')
    except:
        pass

    if request.method == "POST":
        try:
            table = request.form['table']
            #count_frame = pandas.read_sql_table(table, index_col = 'gene', con = engine)
            count_frame = pandas.read_csv("~/Dropbox/don_scott_intron/protein_coding_genes.csv", index_col = 'Gene')
            mat = count_frame.as_matrix()
            sklearn_pca = sklearnPCA(n_components = 2)
            pca_points = sklearn_pca.fit_transform(mat.T)
            explained_variance = sklearn_pca.explained_variance_ratio_)
            pca_points_df = pandas.DataFrame(pca_points, columns = ['pc1', 'pc2'])
            pca_points_df['sample'] = count_frame.columns.values
            results = pca_points_df.to_dict(orient = 'records')


        except:
            errors.append(
                "Unable to get URL. PLease make sure it's valid and try again."
            )
    return render_template('index.html', results = json.dumps(results),
                            sample_names = sample_names, counts_tables = counts_tables,
                            explained_variance = explained_variance)

@app.route("/data")
def data():
    count_frame = pandas.read_csv("~/Dropbox/don_scott_intron/genes.csv", index_col = 'gene')
    mat = count_frame.as_matrix()

    sklearn_pca = sklearnPCA(n_components = 2)
    pca_points = sklearn_pca.fit_transform(mat.T)
    pca_points_df = pandas.DataFrame(pca_points, columns = ['pc1', 'pc2'])
    pca_points_df['group'] = [x[0] for x in count_frame.columns.values]
    results = pca_points_df.to_dict(orient = 'records')
    return json.dumps(results)

if __name__ == '__main__':
    app.run(debug = True)
