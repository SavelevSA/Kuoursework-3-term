﻿import pygame
import itertools
import tkinter as tk
from tkinter import filedialog
import math

# Константы
WIDTH, HEIGHT = 800, 600
NODE_RADIUS = 20
FONT_SIZE = 18
LINE_COLOR = (200, 200, 200)
CURRENT_EDGE_COLOR = (234,197,5)
CURRENT_NODE_COLOR = (234,197,5)
FINAL_PATH_COLOR = (0, 255, 0)
NODE_COLOR = (2,121,205)
TEXT_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (30, 30, 30)

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Визуализация TSP")
font = pygame.font.Font(None, FONT_SIZE)

# Поле ввода скорости
input_box = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 50, 100, 30)
speed_input = "200"  # Начальное значение задержки (в миллисекундах)
speed_active = False  # Статус активности поля

# Чтение файла с матрицей
def read_distance_matrix(file_path):
    with open(file_path, 'r') as file:
        matrix = []
        for line in file:
            row = line.strip().split()
            matrix.append([float('inf') if x == 'inf' else int(x) for x in row])
        return matrix

# Рисование графа
def draw_graph(matrix, node_positions, visited_edges, current_edges=None, current_nodes=None, final_path_edges=None, step_info=None, best_costs_per_r=None):
    screen.fill(BACKGROUND_COLOR)

    # Рисуем рёбра
    for i in range(len(matrix)):
        for j in range(len(matrix)):
            if i != j and matrix[i][j] != float('inf'):
                if final_path_edges and (i, j) in final_path_edges:
                    color = FINAL_PATH_COLOR
                elif current_edges and (i, j) in current_edges:
                    color = CURRENT_EDGE_COLOR
                elif (i, j) in visited_edges or (j, i) in visited_edges:
                    color = LINE_COLOR
                else:
                    color = LINE_COLOR
                pygame.draw.line(screen, color, node_positions[i], node_positions[j], 2)
                # Вес ребра
                mid_x = (node_positions[i][0] + node_positions[j][0]) // 2
                mid_y = (node_positions[i][1] + node_positions[j][1]) // 2
                weight_text = font.render(str(matrix[i][j]), True, TEXT_COLOR)
                screen.blit(weight_text, (mid_x, mid_y))

    # Рисуем вершины
    for i, pos in enumerate(node_positions):
        color = CURRENT_NODE_COLOR if current_nodes and i in current_nodes else NODE_COLOR
        pygame.draw.circle(screen, color, pos, NODE_RADIUS)
        node_label = font.render(str(i), True, TEXT_COLOR if final_path_edges else (255, 255, 255))
        screen.blit(node_label, (pos[0] - NODE_RADIUS // 2, pos[1] - NODE_RADIUS // 2))

    # Отображаем информацию о текущем шаге
    if step_info:
        y_offset = 10
        for line in step_info:
            step_text = font.render(line, True, TEXT_COLOR)
            screen.blit(step_text, (10, y_offset))
            y_offset += FONT_SIZE + 5

    # Отображаем список стоимости для каждого r
    if best_costs_per_r:
        y_offset = HEIGHT // 2 + 100  # Начальная позиция под графом
        for cost_info in best_costs_per_r:
            cost_text = font.render(cost_info, True, TEXT_COLOR)
            screen.blit(cost_text, (10, y_offset))
            y_offset += FONT_SIZE + 5

    pygame.display.flip()


# Генерация позиций узлов
def generate_node_positions(n, width, height):
    radius = min(width, height) // 3
    center = (width // 2, height // 2)
    positions = [
        (int(center[0] + radius * math.cos(2 * math.pi * i / n)),
         int(center[1] + radius * math.sin(2 * math.pi * i / n)))
        for i in range(n)
    ]
    return positions

# Загрузка матрицы через диалог
def load_matrix_via_dialog():
    tk.Tk().withdraw()
    file_path = filedialog.askopenfilename(title="Выберите файл с матрицей",
                                           filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if file_path:
        return read_distance_matrix(file_path)
    return None

# Реализация алгоритма с визуализацией
def solve_tsp_visual(distance_matrix, animation_speed=200):
    n = len(distance_matrix)
    dp = {}
    parent = {}
    visited_edges = set()

    node_positions = generate_node_positions(n, WIDTH, HEIGHT)
    best_costs_per_r = []  # Хранение стоимости для каждого r

    # Инициализация
    step_info = ["Инициализация:"]
    for i in range(1, n):
        if distance_matrix[0][i] != float('inf'):
            dp[(frozenset([i]), i)] = distance_matrix[0][i]
            parent[(frozenset([i]), i)] = 0
            step_info.append(f"0 -> {i}: {distance_matrix[0][i]}")
    draw_graph(distance_matrix, node_positions, visited_edges, step_info=step_info)
    pygame.time.wait(animation_speed)

    # Перебор всех подмножеств
    for r in range(2, n):
        for subset in itertools.combinations(range(1, n), r):
            subset_set = frozenset(subset)
            current_nodes = list(subset)
            current_edges = []
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
                        current_edges.append((k, j))

                dp[(subset_set, j)] = best_cost
                parent[(subset_set, j)] = best_prev_city

                # Обновляем шаг и выделяем обрабатываемые рёбра
                step_info = [f"Обрабатываем подмножество: {subset}", f"{best_prev_city} -> {j}: {best_cost}"]
                draw_graph(distance_matrix, node_positions, visited_edges, current_edges, current_nodes, step_info=step_info, best_costs_per_r=best_costs_per_r)
                pygame.time.wait(animation_speed)

                visited_edges.add((best_prev_city, j))

        # Вычисление наиболее выгодного пути после обработки всех подмножеств текущего размера
        best_path, best_cost = find_current_best_path(dp, parent, r, n)
        best_costs_per_r.append(f"{r} вершин: {best_cost}")
        step_info = [f"Наилучший путь для r = {r}: {' -> '.join(map(str, best_path))}", f"Стоимость: {best_cost}"]
        draw_graph(distance_matrix, node_positions, visited_edges, step_info=step_info, best_costs_per_r=best_costs_per_r)
        pygame.time.wait(animation_speed+1500)

    # Завершаем маршрут
    final_subset = frozenset(range(1, n))
    best_cost = float('inf')
    last_city = None
    for i in range(1, n):
        if distance_matrix[i][0] != float('inf'):
            cost = dp.get((final_subset, i), float('inf')) + distance_matrix[i][0]
            if cost < best_cost:
                best_cost = cost
                last_city = i

    # Восстановление маршрута
    route = [0]
    subset_set = final_subset
    city = last_city
    final_path_edges = []
    while city is not None:
        route.append(city)
        next_city = parent.get((subset_set, city), None)
        subset_set = subset_set - {city}
        if next_city is not None:
            final_path_edges.append((next_city, city))
        city = next_city

    # Отобразить финальный путь
    step_info = [f"Итоговый путь: {' -> '.join(map(str, route))}", f"Стоимость: {best_cost}"]
    draw_graph(distance_matrix, node_positions, visited_edges, final_path_edges=final_path_edges, step_info=step_info, best_costs_per_r=best_costs_per_r)
    pygame.time.wait(animation_speed)

    return best_cost, route


# Функция для нахождения текущего наилучшего пути
def find_current_best_path(dp, parent, r, n):
    best_cost = float('inf')
    best_path = []
    for subset in itertools.combinations(range(1, n), r):
        subset_set = frozenset(subset)
        for j in subset:
            if (subset_set, j) in dp:
                cost = dp[(subset_set, j)]
                if cost < best_cost:
                    best_cost = cost
                    best_path = reconstruct_path(parent, subset_set, j)
    return best_path, best_cost

# Вспомогательная функция для восстановления пути
def reconstruct_path(parent, subset_set, last_node):
    path = []
    while subset_set:
        path.append(last_node)
        next_node = parent.get((subset_set, last_node), None)
        subset_set = subset_set - {last_node}
        last_node = next_node
    return list(reversed(path))


import random

# Новый функционал: ввод матрицы с генерацией случайных весов
def create_random_matrix():
    import tkinter.simpledialog as simpledialog
    tk.Tk().withdraw()
    
    # Ввод количества вершин
    num_nodes = simpledialog.askinteger("Ввод количества вершин", "Введите количество вершин:")
    if not num_nodes or num_nodes <= 0:
        return None

    # Ввод количества рёбер
    num_edges = simpledialog.askinteger("Ввод количества рёбер", "Введите количество рёбер:")
    if not num_edges or num_edges <= 0:
        return None

    # Инициализация пустой матрицы
    distance_matrix = [[float('inf') if i != j else 0 for j in range(num_nodes)] for i in range(num_nodes)]

    # Генерация случайных рёбер
    edges = set()
    while len(edges) < num_edges:
        i, j = random.randint(0, num_nodes - 1), random.randint(0, num_nodes - 1)
        if i != j and (i, j) not in edges and (j, i) not in edges:
            weight = random.randint(1, 50)
            distance_matrix[i][j] = weight
            distance_matrix[j][i] = weight
            edges.add((i, j))

    # Сохранение в файл
    save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
                                             title="Сохранить матрицу как")
    if save_path:
        with open(save_path, 'w') as f:
            for row in distance_matrix:
                f.write(" ".join('inf' if x == float('inf') else str(x) for x in row) + "\n")
        print(f"Матрица успешно сохранена в файл {save_path}")

    return distance_matrix

# Изменения в основном цикле
def main():
    running = True
    distance_matrix = None
    algorithm_finished = False
    final_path = []
    node_positions = []
    final_path_edges = []
    visited_edges = set()
    cost = 0
    graph_surface = None  # Поверхность для графа
    global speed_input, speed_active

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Проверка нажатия на поле ввода скорости
                if input_box.collidepoint(event.pos):
                    speed_active = True
                else:
                    speed_active = False

                # Кнопка "Создать матрицу"
                if not algorithm_finished and WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and HEIGHT // 2 - 75 <= y <= HEIGHT // 2 - 25:
                    distance_matrix = create_random_matrix()
                    if distance_matrix:
                        node_positions = generate_node_positions(len(distance_matrix), WIDTH, HEIGHT)

                # Кнопка "Загрузить матрицу"
                if not algorithm_finished and WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and HEIGHT // 2 - 25 <= y <= HEIGHT // 2 + 25:
                    try:
                        animation_speed = max(100, int(speed_input))  # Минимальная скорость 100 мс
                    except ValueError:
                        animation_speed = 200  # По умолчанию
                    distance_matrix = load_matrix_via_dialog()
                    if distance_matrix:
                        node_positions = generate_node_positions(len(distance_matrix), WIDTH, HEIGHT)
                        cost, final_path = solve_tsp_visual(distance_matrix, animation_speed)
                        final_path_edges = [(final_path[i], final_path[i + 1]) for i in range(len(final_path) - 1)]
                        # Учет симметрии рёбер
                        final_path_edges += [(j, i) for i, j in final_path_edges]
                        algorithm_finished = True

                        # Создаем поверхность с графом
                        graph_surface = pygame.Surface((WIDTH, HEIGHT))
                        draw_graph(distance_matrix, node_positions, visited_edges, final_path_edges=final_path_edges)
                        graph_surface.blit(screen, (0, 0))  # Копируем на экран

                # Кнопка "Рассчитать быстро"
                if not algorithm_finished and WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and HEIGHT // 2 + 130 <= y <= HEIGHT // 2 + 180:
                    distance_matrix = load_matrix_via_dialog()
                    if distance_matrix:
                        node_positions = generate_node_positions(len(distance_matrix), WIDTH, HEIGHT)
                        cost, final_path = solve_tsp_quick(distance_matrix)
                        final_path_edges = [(final_path[i], final_path[i + 1]) for i in range(len(final_path) - 1)]
                        # Учет симметрии рёбер
                        final_path_edges += [(j, i) for i, j in final_path_edges]
                        algorithm_finished = True

                        # Создаем поверхность с графом
                        graph_surface = pygame.Surface((WIDTH, HEIGHT))
                        draw_graph(distance_matrix, node_positions, visited_edges, final_path_edges=final_path_edges)
                        graph_surface.blit(screen, (0, 0))  # Копируем на экран

                # Кнопка "Выход"
                if not algorithm_finished and WIDTH // 2 - 50 <= x <= WIDTH // 2 + 50 and HEIGHT // 2 + 200 <= y <= HEIGHT // 2 + 240:
                    running = False

            elif event.type == pygame.KEYDOWN:
                # Возврат к первому окну
                if event.key == pygame.K_ESCAPE and algorithm_finished:
                    algorithm_finished = False
                    distance_matrix = None
                    final_path = []
                    node_positions = []
                    final_path_edges = []
                    visited_edges = set()
                    cost = 0

                # Обработка ввода текста
                if speed_active:
                    if event.key == pygame.K_BACKSPACE:
                        speed_input = speed_input[:-1]  # Удаление символа
                    elif event.unicode.isdigit():  # Только цифры
                        speed_input += event.unicode

        # Отображение начального окна
        if not algorithm_finished:
            screen.fill(BACKGROUND_COLOR)
            # Кнопка "Создать матрицу"
            pygame.draw.rect(screen, (100, 100, 255), (WIDTH // 2 - 100, HEIGHT // 2 - 75, 200, 50))
            create_button_text = font.render("Создать матрицу", True, (255, 255, 255))
            screen.blit(create_button_text, (WIDTH // 2 - create_button_text.get_width() // 2, HEIGHT // 2 - 65))

            # Кнопка "Загрузить матрицу"
            pygame.draw.rect(screen, (0, 255, 0), (WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50))
            button_text = font.render("Загрузить матрицу", True, (0, 0, 0))
            screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, HEIGHT // 2 - button_text.get_height() // 2))

            # Кнопка "Рассчитать быстро"
            pygame.draw.rect(screen, (0, 0, 255), (WIDTH // 2 - 100, HEIGHT // 2 + 130, 200, 50))
            quick_button_text = font.render("Рассчитать быстро", True, (255, 255, 255))
            screen.blit(quick_button_text, (WIDTH // 2 - quick_button_text.get_width() // 2, HEIGHT // 2 + 140 + quick_button_text.get_height() // 2))

            # Кнопка "Выход"
            pygame.draw.rect(screen, (255, 0, 0), (WIDTH // 2 - 50, HEIGHT // 2 + 200, 100, 50))
            exit_text = font.render("Выход", True, (0, 0, 0))
            screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 210 + exit_text.get_height() // 2))

            # Поле ввода скорости
            pygame.draw.rect(screen, (255, 255, 255), input_box, 2 if speed_active else 1)
            input_text = font.render(speed_input, True, (255, 255, 255))
            screen.blit(input_text, (input_box.x + 5, input_box.y + 10))
            label_text = font.render("Скорость (мс):", True, (255, 255, 255))
            screen.blit(label_text, (input_box.x - label_text.get_width() + 90, input_box.y - 15))
        else:
            # Отображение финального графа
            if graph_surface:
                screen.blit(graph_surface, (0, 0))

            completion_text = font.render("Алгоритм завершён. Нажмите ESC для возврата.", True, (255, 255, 255))
            screen.blit(completion_text, (WIDTH // 2 - completion_text.get_width() // 2, HEIGHT - 70))
            path_text = font.render(f"Путь: {' -> '.join(map(str, final_path))}", True, (255, 255, 255))
            screen.blit(path_text, (WIDTH // 2 - path_text.get_width() // 2, HEIGHT - 40))
            cost_text = font.render(f"Стоимость: {cost}", True, (255, 255, 255))
            screen.blit(cost_text, (WIDTH // 2 - cost_text.get_width() // 2, HEIGHT - 20))

        pygame.display.update()


# Алгоритм без визуализации
def solve_tsp_quick(distance_matrix):
    import itertools

    n = len(distance_matrix)
    dp = {}
    parent = {}

    # Инициализация
    for i in range(1, n):
        dp[(frozenset([i]), i)] = distance_matrix[0][i]
        parent[(frozenset([i]), i)] = 0

    # Перебор всех подмножеств
    for r in range(2, n):
        for subset in itertools.combinations(range(1, n), r):
            subset_set = frozenset(subset)
            for j in subset:
                prev_subset = subset_set - {j}
                best_cost = float('inf')
                best_prev_city = None
                for k in subset:
                    if k != j:
                        cost = dp[(prev_subset, k)] + distance_matrix[k][j]
                        if cost < best_cost:
                            best_cost = cost
                            best_prev_city = k
                dp[(subset_set, j)] = best_cost
                parent[(subset_set, j)] = best_prev_city

    # Завершаем маршрут
    final_subset = frozenset(range(1, n))
    best_cost = float('inf')
    last_city = None
    for i in range(1, n):
        cost = dp[(final_subset, i)] + distance_matrix[i][0]
        if cost < best_cost:
            best_cost = cost
            last_city = i

    # Восстановление маршрута
    route = [0]
    subset_set = final_subset
    city = last_city
    while city != 0:
        route.append(city)
        next_city = parent[(subset_set, city)]
        subset_set -= {city}
        city = next_city
    route.append(0)

    return best_cost, route


if __name__ == "__main__":
    main()
