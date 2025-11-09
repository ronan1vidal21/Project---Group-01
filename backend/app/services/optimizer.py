# backend/app/services/optimizer.py
from typing import List, Tuple

def knapsack_0_1(values: List[int], costs: List[int], budget: int) -> Tuple[int, List[int]]:
    """
    Classic 0/1 knapsack dynamic programming.
    Returns (max_value, indices_of_selected_items)
    """
    n = len(values)
    if n == 0:
        return 0, []
    dp = [[0]*(budget+1) for _ in range(n+1)]
    for i in range(1, n+1):
        v = values[i-1]; c = costs[i-1]
        for b in range(budget+1):
            dp[i][b] = dp[i-1][b]
            if c <= b:
                val = dp[i-1][b-c] + v
                if val > dp[i][b]:
                    dp[i][b] = val
    # reconstruct selection
    res = []
    b = budget
    for i in range(n, 0, -1):
        if dp[i][b] != dp[i-1][b]:
            res.append(i-1)
            b -= costs[i-1]
    res.reverse()
    return dp[n][budget], res

