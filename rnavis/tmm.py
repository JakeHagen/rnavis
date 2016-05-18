# Port of edgeR's implementation of the TMM RNAseq normalization method
# https://github.com/Bioconductor-mirror/edgeR/blob/master/R/calcNormFactors.R
# TMM method from paper:
# https://genomebiology.biomedcentral.com/articles/10.1186/gb-2010-11-3-r25

import numpy as np


def calc_factor_weighted(obs, ref, libsize_obs=None, libsize_ref=None,
                         log_ratio_trim=0.3, sum_trim=0.05,
                         do_weighting=True, A_cut_off=-1e10):

    if not libsize_obs:
        n_o = np.sum(obs)
    else:
        n_o = libsize_obs
    if not libsize_ref:
        n_r = np.sum(ref)
    else:
        n_r = libsize_ref

    if n_o == n_r:
        return 1

    log_r = np.log2((obs / n_o) / (ref / n_r))
    abs_e = (np.log2(obs / n_o) + np.log2(ref / n_r)) / 2
    v = (n_o - obs) / n_o / obs + (n_r - ref) / n_r / ref

    len_array = log_r.shape[0]
    fin = np.array([np.isfinite(log_r[i]) and np.isfinite(abs_e[i]) and
                    (abs_e[i] > A_cut_off) for i in range(len_array)])

    log_r = log_r[fin]
    abs_e = abs_e[fin]
    v = v[fin]

    n = float(len(log_r))
    lol = int(n * log_ratio_trim) + 1
    hil = n + 1 - lol
    los = int(n * sum_trim) + 1
    his = n + 1 - los

    log_r_temp = log_r.argsort()
    log_r_rank = np.empty(len(log_r), int)
    log_r_rank[log_r_temp] = np.arange(len(log_r))

    abs_e_temp = abs_e.argsort()
    abs_e_rank = np.empty(len(abs_e), int)
    abs_e_rank[abs_e_temp] = np.arange(len(abs_e))

    keep = np.array([(lol <= log_r_rank[i] <= hil) and
                    (los <= abs_e_rank[i] <= his)
                    for i in range(len(abs_e_rank))])

    if do_weighting:
        return 2**(np.nansum(log_r[keep] / v[keep]) / np.nansum(1/v[keep]))
    else:
        return 2**(np.nanmean(log_r[keep]))


def calc_factor_quantile(data, lib_size, p=75):
    y = data / lib_size
    return np.percentile(y, q=p, axis=0)


def calc_norm_factors(obj, lib_size=None, ref_col=None,
                      log_ratio_trim=.3, sum_trim=.05,
                      do_weighting=True, A_cut_off=-1e10, p=75):
    try:
        x = obj.as_matrix()
    except AttributeError:
        x = obj

    if np.isnan(np.sum(x)):
        raise Exception("NaN counts not permitted")

    if not lib_size:
        lib_size = x.sum(axis=0)
    if np.isnan(np.sum(lib_size)):
        raise Exception("NaN lib_sizes not permitted")

    x = np.delete(x, np.where(x.sum(axis=1) == 0), 0)

    f75 = calc_factor_quantile(data=x, lib_size=lib_size, p=75)
    if not ref_col:
        ref_col = np.argmin(np.absolute(f75 - np.mean(f75)))
    f_array = []
    for i in range(x.shape[1]):
        f_array.append(calc_factor_weighted(obs=x[:, i], ref=x[:, ref_col],
                                            libsize_obs=lib_size[i],
                                            libsize_ref=lib_size[ref_col],
                                            log_ratio_trim=log_ratio_trim,
                                            sum_trim=sum_trim,
                                            do_weighting=do_weighting,
                                            A_cut_off=A_cut_off))

    f = np.array(f_array)
    f = f / np.exp(np.mean(np.log(f)))
    return f
