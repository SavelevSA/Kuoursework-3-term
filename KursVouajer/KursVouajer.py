
import itertools
def solve_tsp_bellman_held_karp(distance_matrix):
    n = len(distance_matrix)
    
    # dp[(subset, i)] - ����������� ����� ����, ������� ��� ������ � subset � ���������� � ������ i
    dp = {}
    # parent[(subset, i)] - ���������� �����, �� �������� �� ������ � ����� i
    parent = {}

    # ������������� ��������� ���������: �� ������ 0 �� ���� ���������
    print("��� 1: ������������� ��������� ��������� (����� �� ������ 0 �� ���� ���������):")
    for i in range(1, n):
        if distance_matrix[0][i] != float('inf'):
            dp[(frozenset([i]), i)] = distance_matrix[0][i]
            parent[(frozenset([i]), i)] = 0
            print(f"  ��������� ���������: �� ������ 0 �� ������ {i}: ���������� = {distance_matrix[0][i]}")

    # ������� ���� ����������� ������� > 1
    print("\n��� 2: ������� ����������� �������:")
    for r in range(2, n):
        print(f"  ������������ ������������ �������� {r}:")
        for subset in itertools.combinations(range(1, n), r):
            subset_set = frozenset(subset)
            print(f"    ������� ������������: {subset}")
            for j in subset:
                prev_subset = subset_set - {j}
                best_cost = float('inf')
                best_prev_city = None
                for k in subset:
                    if k == j:
                        continue
                    if distance_matrix[k][j] != float('inf'):
                        cost = dp.get((prev_subset, k), float('inf')) + distance_matrix[k][j]
                        if cost < best_cost:
                            best_cost = cost
                            best_prev_city = k
                dp[(subset_set, j)] = best_cost
                parent[(subset_set, j)] = best_prev_city
                print(f"      ���� ��� ������ {j}, ������ �� ������ {best_prev_city}:"
                      f" ����� ��������� = {best_cost}")
        print()

    # ����������: ����������� � ��������� ����� (0)
    print("\n��� 3: ��������� ������� ������������ � ��������� ����� (����� 0):")
    final_subset = frozenset(range(1, n))  # ��� ������, ����� 0
    best_cost = float('inf')
    last_city = None
    for i in range(1, n):
        if distance_matrix[i][0] != float('inf'):
            cost = dp.get((final_subset, i)) + distance_matrix[i][0]
            print(f"  ���� �� ������ {i} ������� � ����� 0: ����� ��������� = {cost}")
            if cost < best_cost:
                best_cost = cost
                last_city = i
                print(f"  --> ��� ������ ���� �� ������ ������, ����������� �� ������ {i}: ����� ��������� = {best_cost}")

    # �������������� ��������
    print("\n��� 4: �������������� �������� � ����� �������� �����������:")
    route = [0]  # �������� � ������ 0
    subset_set = final_subset
    city = last_city
    print(f"  �������� � ������ 0, ��������� ����� ����� ������������: {last_city}")
    while city is not None:
        route.append(city)  # ��������� ������� ����� � �������
        next_city = parent.get((subset_set, city), None)
        subset_set = subset_set - {city}

        # ������� ������� ������������ � �����, ������� ��� �������� � �������� �������
        print(f"  ������������ {sorted(list(subset_set | {city}))} �������� � �������� �������, �������� ����� {city}")
        city = next_city

    return best_cost, route

distance_matrix = [
	[0, 23, float('inf'), 4, 2, 16],
	[23, 0, 12, 19, float('inf'), float('inf')],
	[float('inf'), 12, 0, 14, 6, 9],
	[4, 19, 14, 0, float('inf'), 11],
	[2, float('inf'), 6, float('inf'), 0, 9],
	[16, float('inf'), 9, 11, 9, 0]
]

# ������� ������
best_cost, best_route = solve_tsp_bellman_held_karp(distance_matrix)

print(f"\n����������� ����� ��������: {best_cost}")
print(f"�������: {best_route}")
