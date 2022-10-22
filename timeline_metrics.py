from metrics import summary_f1_eval


def time_penalty(d1, d2):
    """
    Calculate the time penalty of two dates
    :param d1: the first date - <datetime>
    :param d2: the second date - <datetime>
    """
    return 1 / (abs(d1 - d2) + 1)


def cnt(r, s, g):
    if type(r) is not str:
        r = " ".join(r)

    if type(s) is not str:
        s = " ".join(s)

    return min(r.count(g), s.count(g))


def alignment_rouge(reference, system):
    """
    Alignment-based ROUGE recall evaluation.

    :param reference: ground truth - [(d1, s1), (d2, s2), (d3, s3)]
    :param system: ground truth - [(d1, s1), (d2, s2), (d3, s3)]
    """

    # 1. find a element in reference that can get the lowest cost for each element in system
    y_test = []
    for s_d, s_s in system:
        best_pair = []
        min_cost = int(1e6)
        for r_d, r_s in reference:
            cost = (1 - 1 / (abs(r_d - s_d) + 1)) * \
                (1 - summary_f1_eval(r_s, s_s))
            if cost < min_cost:
                min_cost = cost
                best_pair = (r_d, r_s)
        y_test.append(best_pair)

    # 2. calculate the recall
    n = len(y_test)
    numerator = sum((len(g[1]) for g in y_test))
    denom = sum((time_penalty(y_test[i][0], system[i][0]) * (sum(
        (cnt(y_test[i][1], system[i][1], g) for g in y_test[i][1]))) for i in range(n)))

    return numerator / denom
