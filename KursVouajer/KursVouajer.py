
import itertools
def solve_tsp_bellman_held_karp(distance_matrix):
    n = len(distance_matrix)
    
    # dp[(subset, i)] - минимальная длина пути, посещая все города в subset и заканчивая в городе i
    dp = {}
    # parent[(subset, i)] - предыдущий город, из которого мы пришли в город i
    parent = {}

    # Инициализация начальных состояний: от города 0 ко всем остальным
    print("ШАГ 1: Инициализация начальных состояний (путей от города 0 ко всем остальным):")
    for i in range(1, n):
        if distance_matrix[0][i] != float('inf'):
            dp[(frozenset([i]), i)] = distance_matrix[0][i]
            parent[(frozenset([i]), i)] = 0
            print(f"  Начальное состояние: от города 0 до города {i}: расстояние = {distance_matrix[0][i]}")

    # Перебор всех подмножеств городов > 1
    print("\nШАГ 2: Перебор подмножеств городов:")
    for r in range(2, n):
        print(f"  Обрабатываем подмножества размером {r}:")
        for subset in itertools.combinations(range(1, n), r):
            subset_set = frozenset(subset)
            print(f"    Текущее подмножество: {subset}")
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
                print(f"      Путь для города {j}, пришли из города {best_prev_city}:"
                      f" общая стоимость = {best_cost}")
        print()

    # Завершение: возвращение в начальный город (0)
    print("\nШАГ 3: Завершаем маршрут возвращением в начальный город (город 0):")
    final_subset = frozenset(range(1, n))  # Все города, кроме 0
    best_cost = float('inf')
    last_city = None
    for i in range(1, n):
        if distance_matrix[i][0] != float('inf'):
            cost = dp.get((final_subset, i)) + distance_matrix[i][0]
            print(f"  Путь из города {i} обратно в город 0: общая стоимость = {cost}")
            if cost < best_cost:
                best_cost = cost
                last_city = i
                print(f"  --> Это лучший путь на данный момент, возвращаясь из города {i}: общая стоимость = {best_cost}")

    # Восстановление маршрута
    print("\nШАГ 4: Восстановление маршрута и вывод ключевых подмножеств:")
    route = [0]  # Начинаем с города 0
    subset_set = final_subset
    city = last_city
    print(f"  Начинаем с города 0, последний город перед возвращением: {last_city}")
    while city is not None:
        route.append(city)  # Добавляем текущий город в маршрут
        next_city = parent.get((subset_set, city), None)
        subset_set = subset_set - {city}

        # Выводим текущее подмножество и город, который был добавлен в итоговый маршрут
        print(f"  Подмножество {sorted(list(subset_set | {city}))} включено в итоговый маршрут, добавлен город {city}")
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

# Решение задачи
best_cost, best_route = solve_tsp_bellman_held_karp(distance_matrix)

print(f"\nМинимальная длина маршрута: {best_cost}")
print(f"Маршрут: {best_route}")
