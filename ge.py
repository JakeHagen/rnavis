import tmm
import numpy as np

class gene_expression:

    '''number_of_groups is a estimate based on uniqueness of non number characters
        in sample names
    '''

    def __init__(self, df):
        self.df = df
        self.matrix = df.as_matrix()
        self.genes = df.index.values
        self.samples = df.columns.values
        self.lib_size = self.matrix.sum(axis = 0)
        self.number_of_groups = len(set(
            [''.join([i for i in x if not i.isdigit()]) for x in self.samples]
                                        ))


def voom_out(ge):
    '''Takes gene_expression class, will eventually extend it to just take a matrix
    '''
    mat_cpm = ge.matrix / (ge.lib_size / 1e6)
    mat = ge.matrix[(mat_cpm > 1).sum(axis = 1) >= int(len(ge.samples) / ge.number_of_groups)]
    norm_factors = (ge.lib_size * tmm.calc_norm_factors(mat)) + 1
    mat_five = mat + .5
    return np.log2(mat_five / norm_factors * 1e6)
