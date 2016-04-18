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

app = Flask(__name__)
engine = sqly.create_engine(config.psql)
meta = sqly.MetaData()
meta.reflect(engine)

@app.route('/', methods = ['GET', 'POST'])
def index():
    errors = []
    results = []
    sample_names = []
    print(list(meta.tables))
    all_tables = list(meta.tables)
    explained_variance = []
    counts_tables = [x for x in all_tables if "pipeline" not in x]



    if request.method == "POST":
        try:
            table = request.form['table']
            count_frame = pandas.read_sql_table(table, index_col = 'gene', con = engine)
            #count_frame = pandas.read_csv("/home/jake/Dropbox/rnavis/voom.csv", index_col = 'Gene')
            mat = count_frame.as_matrix()
            mat_cpm = mat / (mat.sum(axis = 0) / 1000000)
            row_del = (mat_cpm.sum(axis = 1) <= int(mat.shape[1] / 2)).nonzero()
            mat = (np.delete(mat, row_del[0], 0)) + 0.5
            norm_factors = (mat.sum(axis = 0) / tmm.calc_norm_factors(mat)) + 1
            #print(norm_factors)
            mat_normed = np.log2(mat / (norm_factors * 1e6))
            #print(mat_normed)
            sklearn_pca = sklearnPCA(n_components = 4)
            pca_points = sklearn_pca.fit_transform(mat_normed.T)
            explained_variance = sklearn_pca.explained_variance_ratio_
            #pca_points_df = pandas.DataFrame(pca_points.T, columns = count_frame.columns.values)
            #pca_points_df['pc'] = ['pc1', 'pc2', 'pc3', 'pc4']
            pca_points_df = pandas.DataFrame(pca_points, columns = ['pc1', 'pc2', 'pc3', 'pc4'])
            pca_points_df['sample'] = count_frame.columns.values
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
