def calculate_ktu_total(part_a_scores, part_b_scores):
    """
    part_a_scores = list of 10 values
    part_b_scores = {
        "module1": (q11_score, q12_score),
        "module2": (q13_score, q14_score),
        ...
    }
    """

    part_a_total = sum(part_a_scores)

    part_b_total = 0
    for module in part_b_scores:
        part_b_total += max(part_b_scores[module])

    grand_total = part_a_total + part_b_total

    return {
        "part_a_total": part_a_total,
        "part_b_total": part_b_total,
        "grand_total": grand_total
    }
