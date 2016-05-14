import rnavis.tmm as tmm
import numpy as np
import pandas
from sklearn.decomposition import PCA as sklearnPCA


class gene_expression:

    '''number_of_groups is a estimate based on uniqueness of
       non number characters in sample names
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
    mat = ge.df[(mat_cpm > 1).sum(axis=1) >=
                int(len(ge.samples) / ge.number_of_groups)]
    norm_factors = (ge.lib_size * tmm.calc_norm_factors(mat)) + 1
    mat_five = mat + .5
    return np.log2(mat_five / norm_factors * 1e6)


def pc_to_keep(exp_var_list, var):
    exp_var = [x for x in exp_var_list if x >= var]
    return exp_var, len(exp_var)


def trim_pc(pc_mat, pc_keep):
    pca_points = pc_mat[:, 0:pc_keep]
    col_names = ["pc%s" % str(x+1) for x in range(pc_keep)]
    return pandas.DataFrame(pca_points, columns=col_names)


def append_exp_var(pc_df, exp_var_list, num_pc=None):
    if not num_pc:
        num_pc = len(exp_var_list)
    for x in range(num_pc):
        pc_df['exp_var%s' % str(x+1)] = exp_var_list[x]
    return pc_df


def pca_json(ge, voom=True):
    if voom:
        mat_normed = voom_out(ge)
    else:
        mat_normed = ge.matrix
    sklearn_pca = sklearnPCA(n_components=4)
    pca_points = sklearn_pca.fit_transform(mat_normed.T)
    exp_var, num_pc = pc_to_keep(sklearn_pca.explained_variance_ratio_, .0001)
    pca_points_df = trim_pc(pca_points, num_pc)
    pca_points_df['sample'] = ge.samples
    pca_points_df = append_exp_var(pc_df=pca_points_df,
                                   exp_var_list=exp_var,
                                   num_pc=num_pc)
    return pca_points_df.to_dict(orient='records')
