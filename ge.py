import tmm
import numpy as np
import pandas
from sklearn.decomposition import PCA as sklearnPCA


class gene_expression:

    '''number_of_groups is a estimate based on uniqueness of non number characters
        in sample names
    '''

    def __init__(self, df):
        self.df = df
        self.matrix = df.as_matrix()
        self.genes = df.index.values
        self.samples = df.columns.values
        self.lib_size = self.matrix.sum(axis=0)
        self.number_of_groups = len(set(
            [''.join([i for i in x if not i.isdigit()]) for x in self.samples]
                                        ))


def voom_out(ge):
    mat_cpm = ge.df / (ge.lib_size / 1e6)
    mat = ge.df[(mat_cpm > 1).sum(axis=1) >= int(len(ge.samples) / ge.number_of_groups)]
    norm_factors = (ge.lib_size * tmm.calc_norm_factors(mat)) + 1
    mat_five = mat + .5
    return np.log2(mat_five / norm_factors * 1e6)


def pca_json(ge, voom=True):
    if voom:
        mat_normed = voom_out(ge)
    else:
        mat_normed = ge.matrix
    sklearn_pca = sklearnPCA(n_components=4)
    pca_points = sklearn_pca.fit_transform(mat_normed.T)
    explained_variance = sklearn_pca.explained_variance_ratio_
    exp_var = [x for x in explained_variance if x >= .0001]
    pca_points_df = pandas.DataFrame(pca_points[:,0:len(exp_var)],
                    columns=["pc%s" % str(x+1) for x in range(len(exp_var))])
    pca_points_df['sample'] = ge.samples
    for x in range(len(explained_variance)):
        pca_points_df['exp_var%s' % str(x+1)] = explained_variance[x]
    return pca_points_df.to_dict(orient='records')
