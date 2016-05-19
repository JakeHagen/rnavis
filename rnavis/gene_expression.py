import rnavis.tmm as tmm
import numpy as np
import pandas
from sklearn.decomposition import PCA as sklearnPCA

"""
Most likely will be removed as info can just be extracted from pandas DF

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
"""


def counts_per_million(mat):
    lib_size = mat.sum(axis=0)
    return mat / (lib_size / 1e6)


def rm_low_counts(mat, samples_per_group=None):
    mat_cpm = counts_per_million(mat)
    if not samples_per_group:
        samples_per_group = int(mat.shape[1]/2)
    # remove genes that do not have at least 1 cpm in at n samples
    # where n is the number of samples in smallest group
    to_rm = (mat_cpm > 1).sum(axis=1) >= samples_per_group
    return mat[to_rm]


def norm_gene_matrix(mat):
    try:
        samples_per_group = mat.columns.values
        mat = rm_low_counts(mat=mat, samples_per_group=samples_per_group)
    except AttributeError:
        mat = rm_low_counts(mat)
    lib_size = mat.sum(axis=0)
    norm_factors = (lib_size * tmm.calc_norm_factors(mat)) + 1
    # mat_five = mat + .5
    return np.log2(mat / norm_factors * 1e6)


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


def pca_json(df, n_components=4, exp_var_min=.05):
    sklearn_pca = sklearnPCA(n_components=n_components)
    pca_points = sklearn_pca.fit_transform(df.T)
    exp_var, num_pc = pc_to_keep(sklearn_pca.explained_variance_ratio_,
                                 exp_var_min)
    pca_points_df = trim_pc(pca_points, num_pc)
    pca_points_df['sample'] = df.columns.values
    pca_points_df = append_exp_var(pc_df=pca_points_df,
                                   exp_var_list=exp_var,
                                   num_pc=num_pc)
    return pca_points_df
