import rnavis.tmm as tmm
import numpy as np
import pandas
from sklearn.decomposition import PCA as sklearnPCA
from rnavis.combat import combat


def counts_per_million(mat):
    lib_size = mat.sum(axis=0)
    return mat / (lib_size / 1e6)


def get_samples_per_group(df):
    try:
        samples = df.columns.values
        number_of_groups = len(set([''.join([i for i in x if not i.isdigit()])
                                    for x in samples]))
        return int(len(samples) / number_of_groups)
    except AttributeError:
        return int(df.shape[1]/2)


def rm_low_counts(mat):
    mat_cpm = counts_per_million(mat)
    samples_per_group = get_samples_per_group(mat)
    # remove genes that do not have at least 1 cpm in at n samples
    # where n is the number of samples in smallest group
    to_rm = (mat_cpm > 1).sum(axis=1) >= samples_per_group
    return mat[to_rm]


def norm_gene_matrix(mat):
    mat = rm_low_counts(mat=mat)
    lib_size = mat.sum(axis=0)
    norm_factors = (lib_size * tmm.calc_norm_factors(mat)) + 1
    mat = mat + .5
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


class matrix_manipulation:

    def __init__(self, counts_dict=None, norm_dict=None):
        self.counts_dict = counts_dict or dict()
        self.norm_dict = norm_dict or dict()
        self.batch_dict = dict()

    def add_counts_matrix(self, name, counts_matrix):
        self.counts_dict[name] = counts_matrix

    def get_counts_matrix(self, name):
        return self.counts_dict[name]

    def add_batch_matrix(self, name, batch_matrix):
        self.batch_dict[name] = batch_matrix

    def get_batch_matrix(self, name):
        return self.batch_dict[name]

    def add_norm_matrix(self, name, norm_matrix):
        self.norm_dict[name] = norm_matrix

    def get_norm_matrix(self, name):
        try:
            return self.norm_dict[name]
        except KeyError:
            self.norm_counts_matrix(name)
            return self.norm_dict[name]

    def norm_counts_matrix(self, name):
        try:
            self.norm_dict[name] = norm_gene_matrix(self.counts_dict[name])
        except KeyError as e:
            raise KeyError(
                'need counts_matrix before we can normalize'
                ).with_traceback(e.__traceback__)

    def make_batch_matrix(self, batch_list, name=None, matrix=None):
        if name and matrix is None:
            try:
                self.batch_dict[name] = combat(self.norm_dict[name],
                                               batch=list(batch_list))
            except KeyError:
                try:
                    self.norm_counts_matrix(name=name)
                    self.batch_matrix = combat(self.norm_matrix,
                                               batch=list(batch_list))
                except KeyError as e:
                    raise KeyError(
                        'need a norm_matrix before it can be batch' +
                        'corrected, also couldnt create norm matrix'
                        ).with_traceback(e.__traceback__)
        else:
            corrected_matrix = combat(matrix, batch=list(batch_list))
            return corrected_matrix
