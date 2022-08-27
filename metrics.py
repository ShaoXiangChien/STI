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
