def keyword_map_eval(ans: list, obj: list) -> float:
    hit = 0
    total_score = 0
    for id, w in enumerate(obj):
        if id + 1 > len(ans):
            break
        if w == ans[id]:
            hit += 1
            total_score += hit / (id + 1)
    return total_score / len(ans)


def keyword_precision_eval(ans: list, obj: list) -> float:
    hit = 0
    for kw in obj:
        if kw in ans:
            hit += 1
    return hit, hit / len(obj)


def summary_precision(output: str, human: str) -> float:
    hit = 0
    for w in output:
        if w in human:
            hit += 1

    return hit / len(output)


def summary_recall(output: str, human: str) -> float:
    hit = 0
    for w in human:
        if w in output:
            hit += 1
    return hit / len(human)


def summary_f1_eval(output: str, human: str) -> float:
    precision = summary_precision(output, human)
    recall = summary_recall(output, human)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1
