)
def calc_factor_weighted(obs, ref, libsize_obs = None, libsize_ref = None,
                            log_ratio_trim = .3, sum_trim = .05,
                            do_weighting = True, A_cut_off = -10000000000):

    if libsize_obs == None:
        n0 = np.sum(obs)
    else:
        n0 = libsize_obs

    if libsize_ref == None:
        nR = np.sum(ref)
    else:
        nR = libsize_ref

    log_r = np.log2((obs / n0)/(ref / nR))
    abs_e = (np.log2(obs/nO) + np.log2(ref/nR)) / 2
    v = (n0 - obs)/n0/obs + (nR - ref)/nR/ref

    fin = np.array([
                    np.isfinite(log_r[index])
                    and np.isfinite(abs_e[index])
                    and (abs_e[index] > A_cut_off)
                    for index, value in enumerate(log_r)
                    ])

    log_r = log_r[fin]
    abs_e = abs_e[fin]
    v = v[fin]

    # Rcode check, will implement later
    # if(max(abs(logR)) < 1e-6) return(1)

    n = len(log_r)
    lol = int(n * log_ratio_trim) + 1
    hil = n + 1 - lol
    los = int(n* sum_trim) + 1
    his = n + 1 - los
