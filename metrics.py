def keyword_eval(ans: list, obj: list) -> float:
    hit = 0
    total_score = 0
    for id, w in enumerate(ans):
        if w == obj[id]:
            hit += 1
            total_score += hit / (id + 1)
    return total_score / len(ans)
