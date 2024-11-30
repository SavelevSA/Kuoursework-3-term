import pygame
import itertools
import tkinter as tk
from tkinter import filedialog
import math

# Константы
WIDTH, HEIGHT = 800, 600
NODE_RADIUS = 20
FONT_SIZE = 18
LINE_COLOR = (200, 200, 200)
CURRENT_EDGE_COLOR = (255, 0, 0)
CURRENT_NODE_COLOR = (255, 255, 0)
FINAL_PATH_COLOR = (0, 255, 0)
NODE_COLOR = (0, 0, 255)
TEXT_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (30, 30, 30)

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Визуализация TSP")
font = pygame.font.Font(None, FONT_SIZE)

# Чтение файла с матрицей
def read_distance_matrix(file_path):
    with open(file_path, 'r') as file:
        matrix = []
        for line in file:
            row = line.strip().split()
            matrix.append([float('inf') if x == 'inf' else int(x) for x in row])
        return matrix

# Рисование графа
def draw_graph(matrix, node_positions, visited_edges, current_edges=None, current_nodes=None, final_path_edges=None, step_info=None):
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
def solve_tsp_visual(distance_matrix):
    n = len(distance_matrix)
    dp = {}
    parent = {}
    visited_edges = set()

    node_positions = generate_node_positions(n, WIDTH, HEIGHT)

    # Инициализация
    step_info = ["Инициализация:"]
    for i in range(1, n):
        if distance_matrix[0][i] != float('inf'):
            dp[(frozenset([i]), i)] = distance_matrix[0][i]
            parent[(frozenset([i]), i)] = 0
            step_info.append(f"0 -> {i}: {distance_matrix[0][i]}")
    draw_graph(distance_matrix, node_positions, visited_edges, step_info=step_info)
    pygame.time.wait(1000)

    # Перебор всех подмножеств
    for r in range(2, n):
        for subset in itertools.combinations(range(1, n), r):
            subset_set = frozenset(subset)
            current_nodes = list(subset)
            best_edge_in_subset = None  # Для выделения самого выгодного пути
            best_cost_in_subset = float('inf')  # Стоимость самого выгодного пути
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
                draw_graph(distance_matrix, node_positions, visited_edges, current_edges, current_nodes, step_info=step_info)
                pygame.time.wait(500)

                # Выделяем самый выгодный путь внутри подмножества
                if best_cost < best_cost_in_subset:
                    best_cost_in_subset = best_cost
                    best_edge_in_subset = (best_prev_city, j)

                # После обработки возвращаем цвет ребра
                draw_graph(distance_matrix, node_positions, visited_edges, current_nodes=current_nodes, step_info=step_info)
                pygame.time.wait(500)
                visited_edges.add((best_prev_city, j))

            # Выделение самого выгодного пути
            if best_edge_in_subset:
                visited_edges.add(best_edge_in_subset)

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
            # Добавляем ребро в двух направлениях
            final_path_edges.append((next_city, city))
            final_path_edges.append((city, next_city))  # Для симметрии
        city = next_city


    # Отобразить финальный путь
    step_info = [f"Итоговый путь: {' -> '.join(map(str, route))}", f"Стоимость: {best_cost}"]
    draw_graph(distance_matrix, node_positions, visited_edges, final_path_edges, step_info=step_info)
    return best_cost, route

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

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not algorithm_finished:
                x, y = event.pos
                if WIDTH // 2 - 100 <= x <= WIDTH // 2 + 100 and HEIGHT // 2 - 25 <= y <= HEIGHT // 2 + 25:
                    distance_matrix = load_matrix_via_dialog()
                    if distance_matrix:
                        node_positions = generate_node_positions(len(distance_matrix), WIDTH, HEIGHT)
                        cost, final_path = solve_tsp_visual(distance_matrix)
                        final_path_edges = [(final_path[i], final_path[i + 1]) for i in range(len(final_path) - 1)]
                        # Учет симметрии рёбер
                        final_path_edges += [(j, i) for i, j in final_path_edges]
                        algorithm_finished = True

                        # Создаем поверхность с графом
                        graph_surface = pygame.Surface((WIDTH, HEIGHT))
                        draw_graph(distance_matrix, node_positions, visited_edges, final_path_edges=final_path_edges)
                        graph_surface.blit(screen, (0, 0))  # Копируем на экран

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        if not algorithm_finished:
            screen.fill(BACKGROUND_COLOR)
            # Отрисовка кнопки
            pygame.draw.rect(screen, (0, 255, 0), (WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50))
            button_text = font.render("Загрузить матрицу", True, (0, 0, 0))
            screen.blit(button_text, (WIDTH // 2 - button_text.get_width() // 2, HEIGHT // 2 - button_text.get_height() // 2))
        else:
            # Отображаем граф (из сохраненной поверхности)
            if graph_surface:
                screen.blit(graph_surface, (0, 0))

            # Сообщение после завершения
            completion_text = font.render("Алгоритм завершён. Нажмите ESC для выхода.", True, (255, 255, 255))
            screen.blit(completion_text, (WIDTH // 2 - completion_text.get_width() // 2, HEIGHT - 70))
            path_text = font.render(f"Путь: {' -> '.join(map(str, final_path))}", True, (255, 255, 255))
            screen.blit(path_text, (WIDTH // 2 - path_text.get_width() // 2, HEIGHT - 40))
            cost_text = font.render(f"Стоимость: {cost}", True, (255, 255, 255))
            screen.blit(cost_text, (WIDTH // 2 - cost_text.get_width() // 2, HEIGHT - 10))

        pygame.display.flip()

    pygame.quit()




if __name__ == "__main__":
    main()
