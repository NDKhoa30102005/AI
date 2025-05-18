import pygame, sys
import random
from collections import deque
from collections import defaultdict

import heapq
import time
import math

pygame.init()

execution_time = 0

WIDTH, HEIGHT = 1100, 600
x_state = 150
y_state = 50
x_goal =  500
y_goal = 50

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Puzzle Solver")

BLUE_BG = (64, 90, 136)
TEXT_COLOR = (0, 0, 0)
TILE_COLOR = (242, 241, 220)
HIGHLIGHT = (255, 255, 240)
SHADOW = (158, 158, 158)

TILE_SIZE = 250 // 3
FONT = pygame.font.Font(None, 40)
FONT_ACTION = pygame.font.Font(None, 30)
STATE = [0] * 9  
GOAL = [1, 2, 3,
        4, 5, 6,
        7, 8, 0]

selected_index = None  # Lưu ô đang được chọn để nhập số
pressed_button = None  # Nút đang được nhấn

BUTTONS = [
    ("BFS", 50, 400),
    ("DFS", 50, 460),
    ("IDDFS", 50, 520),
    ("UCS", 180, 400),
    ("A*", 180, 460),
    ("IDA*", 180, 520),
    ("Greedy", 310, 400),
    ("SHC", 310, 460),
    ("HC", 310, 520),
    ("SAHC", 440, 400),
    ("Genetic", 440, 460),
    ("SA", 440, 520),
    ("Beam", 570, 400),
    ("Belief", 570, 460),
    ("POS", 570, 520),
    ("MinConf", 700, 520),
    ("and-or", 700, 400),
    ("BackFor", 700, 460),


    ("BackTrack", 830, 400),
    ("Q-lerning", 830, 460),

    ("Random", 960, 400),
    ("Reset", 960, 460),
    ("Easy", 960, 520),
]

def screen_belief_algorithm():
    """Hiển thị giao diện riêng cho thuật toán Belief."""
    running = True
    belief_state = [
                    [1, 2, 3,
                    0, 5, 6,
                    4, 7, 8],

                    [1, 0, 3,
                     4, 2, 6,
                     7, 5, 8],

                    [0, 2, 3,
                    1, 5, 6,
                    4, 7, 8] 
                        ]
    BUTTONS = [
        ("Start", 960, 400),
        ("Reset", 960, 460)
    ]
    
    solution_paths = []  # Danh sách các bộ trạng thái cho mỗi bước
    actions = []        # Chuỗi hành động chung
    cost = 0           # Chi phí của đường đi
    goal_state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    pressed_button = None
    click = None
    execution_time = 0
    scroll_y = 0
    current_step = 0  # Theo dõi bước hiện tại trong animation

    while running:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for text, rect in button_rects.items():
                    if rect.collidepoint(mouse_x, mouse_y):
                        pressed_button = text
                        print(f"{pressed_button} button pressed!")
                        break
            elif event.type == pygame.MOUSEBUTTONUP:
                if pressed_button and button_rects[pressed_button].collidepoint(mouse_x, mouse_y):
                    print(f"{pressed_button} button clicked!")
                    click = pressed_button

        if click == "Start":
            start_time = time.time()
            solution_paths, actions, cost = belief_search(belief_state, goal_state)
            execution_time = time.time() - start_time
            current_step = 0
            print("Solution Paths:", solution_paths)
            print("Actions:", actions)
            print("Cost:", cost)
        elif click == "Reset":
            belief_state = [
                            [1, 2, 3,
                            0, 5, 6,
                            4, 7, 8],

                            [1, 0, 3,
                            4, 2, 6,
                            7, 5, 8],

                            [0, 2, 3,
                            1, 5, 6,
                            4, 7, 8] 
                        ]
            solution_paths = []
            actions = []
            cost = 0
            pressed_button = None
            scroll_y = 0
            current_step = 0
        click = None 

        # Vẽ nền
        SCREEN.fill(BLUE_BG)

        button_rects = {text: draw_button(x, y, text, pressed_button == text) for text, x, y in BUTTONS}

        # Vẽ tiêu đề
        title = FONT.render("Belief Search Algorithm", True, TEXT_COLOR)
        SCREEN.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))

        # Vẽ hướng dẫn quay lại
        back_text = FONT_ACTION.render("Nhan ESC de quay lai", True, TEXT_COLOR)
        SCREEN.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

        # Vẽ trạng thái tin tưởng
        for i, state in enumerate(belief_state):
            x = 150 + (i % 3) * 300
            y = 50 + (i // 3) * 200
            draw_grid(x, y, state, None)

        # Hiển thị chi phí và thời gian
        text_cost = FONT.render(f"Cost: {cost}", True, TEXT_COLOR)
        SCREEN.blit(text_cost, (70, 320))

        text_time = FONT.render(f"Time: {execution_time:.6f}", True, TEXT_COLOR)
        SCREEN.blit(text_time, (250, 320))
        # Vẽ các hành động
        if actions:
            action_text = FONT_ACTION.render("Actions: " + ", ".join(actions), True, TEXT_COLOR)
            SCREEN.blit(action_text, (70, 370))

        # Hiển thị animation của các đường đi
        if solution_paths and current_step < len(solution_paths):
            for i in range(len(belief_state)):
                belief_state[i] = solution_paths[current_step][i]  # Cập nhật cả ba trạng thái
            current_step += 1
            pygame.display.flip()
            pygame.time.delay(500)

        if current_step >= len(solution_paths):
            solution_paths = []  # Đặt lại để dừng animation
            current_step = 0

        pygame.display.flip()

def is_solvable(state):
    """Kiểm tra trạng thái có thể giải được không"""
    inversions = 0
    for i in range(8):
        for j in range(i + 1, 9):
            if state[i] and state[j] and state[i] > state[j]:
                inversions += 1
    return inversions % 2 == 0

class SearchNode:
    """Định nghĩa một nút trong cây tìm kiếm"""
    def __init__(self, state, parent=None, action=None, cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost

    def __lt__(self, other):
        """So sánh dựa trên chi phí"""
        return self.cost < other.cost

def extract_path(node):
    """Trích xuất đường đi từ nút đích"""
    path = []
    action = []
    cost = node.cost
    while node.parent:
        action.append(node.action)
        path.append(node.state)
        node = node.parent
    path.reverse()
    action.reverse()
    return path,action, cost

def move(state, action):
    """Di chuyển ô trống"""
    new_state = state[:]
    i = new_state.index(0)  # Tìm vị trí ô trống

    if action == "up" and i >= 3:
        new_state[i], new_state[i - 3] = new_state[i - 3], new_state[i]
    elif action == "down" and i < 6:
        new_state[i], new_state[i + 3] = new_state[i + 3], new_state[i]
    elif action == "left" and i % 3 != 0:
        new_state[i], new_state[i - 1] = new_state[i - 1], new_state[i]
    elif action == "right" and i % 3 != 2:
        new_state[i], new_state[i + 1] = new_state[i + 1], new_state[i]
    else:
        return None

    return new_state

def bfs_solve(initial_state, goal_state):
    frontier = deque([SearchNode(initial_state, cost=0)])
    explored = set()

    while frontier:
        node = frontier.popleft()
        if node.state == goal_state:
            return extract_path(node)

        explored.add(tuple(node.state))
        
        for action in ["up", "down", "left", "right"]:
            new_state = move(node.state, action)
            if new_state and tuple(new_state) not in explored:
                frontier.append(SearchNode(new_state, node, action, node.cost + 1))

    return None,None, 0

def dfs_solve(initial_state, goal_state,depth=50):
    frontier = [SearchNode(initial_state, cost=0)]
    explored = set()

    while frontier:
        node = frontier.pop()
        if node.state == goal_state:
            return extract_path(node)

        if node.cost < depth:
            explored.add(tuple(node.state))
            for action in ["up", "down", "left", "right"]:
                new_state = move(node.state, action)
                if new_state and tuple(new_state) not in explored:
                    frontier.append(SearchNode(new_state, node, action, node.cost + 1))

    return None,None, 0

def iterative_deepening_dfs_solve(initial_state, goal_state):
    for depth in range (1,100):
        frontier = [SearchNode(initial_state, cost=0)]
        explored = set()

        while frontier:
            node = frontier.pop()
            if node.state == goal_state:
                return extract_path(node)

            if node.cost < depth:
                explored.add(tuple(node.state))
                
                for action in ["up", "down", "left", "right"]:
                    new_state = move(node.state, action)
                    if new_state and tuple(new_state) not in explored:
                        frontier.append(SearchNode(new_state, node, action, node.cost + 1))
    return None,None, 0
    
def manhattan_distance(state, goal_state):
    distance = 0
    for i in range(9):
        if state[i] != 0:
            x1, y1 = i % 3, i // 3
            x2, y2 = goal_state.index(state[i]) % 3, goal_state.index(state[i]) // 3
            distance += abs(x1 - x2) + abs(y1 - y2)
    return distance
     
def greedy_best_first_search(initial_state, goal_state):
    frontier = [SearchNode(initial_state, cost=0)]
    explored = set()

    while frontier:
        frontier.sort(key=lambda node: manhattan_distance(node.state, goal_state))
        node = frontier.pop(0)
        if node.state == goal_state:
            return extract_path(node)

        explored.add(tuple(node.state))
        
        for action in ["up", "down", "left", "right"]:
            new_state = move(node.state, action)
            if new_state and tuple(new_state) not in explored:
                frontier.append(SearchNode(new_state, node, action, node.cost + 1))

    return None,None, 0

def a_star_search(initial_state, goal_state):
    frontier = [SearchNode(initial_state, cost=0)]
    explored = set()

    while frontier:
        frontier.sort(key=lambda node: node.cost + manhattan_distance(node.state, goal_state))
        node = frontier.pop(0)
        if node.state == goal_state:
            return extract_path(node)

        explored.add(tuple(node.state))
        
        for action in ["up", "down", "left", "right"]:
            new_state = move(node.state, action)
            if new_state and tuple(new_state) not in explored:
                frontier.append(SearchNode(new_state, node, action, node.cost + 1))

    return None,None, 0

def uniform_cost_search(initial_state, goal_state):
    frontier = []  # Priority queue
    heapq.heappush(frontier, (0, SearchNode(initial_state, cost=0)))
    explored = set()
    cost_so_far = {tuple(initial_state): 0}  # Track lowest cost to reach each state
    
    while frontier:
        cost, node = heapq.heappop(frontier)
        
        if node.state == goal_state:
            return extract_path(node)
        
        explored.add(tuple(node.state))
        
        for action in ["up", "down", "left", "right"]:
            new_state = move(node.state, action)
            if new_state:
                new_state_tuple = tuple(new_state)
                new_cost = node.cost + 1
                
                if new_state_tuple not in explored and (new_state_tuple not in cost_so_far or new_cost < cost_so_far[new_state_tuple]):
                    cost_so_far[new_state_tuple] = new_cost
                    heapq.heappush(frontier, (new_cost, SearchNode(new_state, node, action, new_cost)))
    
    return None,None, 0

def ida_star_search(STATE, GOAL):
    def search(node, g, bound):
        f = g + manhattan_distance(node.state, GOAL)
        if f > bound:
            return f, None  # Trả về ngưỡng mới để tăng dần

        if node.state == GOAL:
            return -1, node  # Khi tìm thấy lời giải, trả về nút cuối cùng

        min_cost = float("inf")
        best_solution = None  # Lưu trạng thái của nút lời giải nếu tìm thấy

        for action in ["up", "down", "left", "right"]:
            new_state = move(node.state, action)
            if new_state and new_state != node.state:
                new_node = SearchNode(new_state, node, action, g + 1)  # Dùng g + 1 thay vì node.cost + 1
                cost, result_node = search(new_node, g + 1, bound)

                if cost == -1:
                    return -1, result_node  # Trả về nút chứa trạng thái đích

                if cost < min_cost:
                    min_cost = cost

        return min_cost, best_solution

    bound = manhattan_distance(STATE, GOAL)
    node = SearchNode(STATE)

    while True:
        cost, result_node = search(node, 0, bound)
        if cost == -1:
            return extract_path(result_node)  # Dùng nút kết thúc để lấy đường đi

        if cost == float("inf"):
            return None, None, 0  # Không tìm thấy đường đi

        bound = cost  # Cập nhật ngưỡng mới nếu chưa tìm thấy

def hill_climbing(STATE, GOAL, max_restarts=100, max_steps=100):
    def get_heuristic(state):
        return manhattan_distance(state, GOAL)

    best_path = None
    best_actions = None
    best_heuristic = float('inf')

    for _ in range(max_restarts):
        current = SearchNode(STATE)
        path = [STATE[:]]
        actions = []
        visited = set()
        for _ in range(max_steps):
            if current.state == GOAL:
                return path, actions, len(actions)
            visited.add(tuple(current.state))
            neighbors = []
            for action in ["up", "down", "left", "right"]:
                new_state = move(current.state, action)
                if new_state and tuple(new_state) not in visited:
                    neighbors.append((get_heuristic(new_state), action, new_state))
            if not neighbors:
                break
            # Chọn hàng xóm tốt nhất (ít heuristic nhất)
            neighbors.sort(key=lambda x: x[0])
            best_h, best_action, best_state = neighbors[0]
            if best_h >= get_heuristic(current.state):
                break  # Không cải thiện nữa, restart vòng ngoài
            current = SearchNode(best_state)
            path.append(best_state)
            actions.append(best_action)
            # Cập nhật best nếu tốt hơn
            if best_h < best_heuristic:
                best_heuristic = best_h
                best_path = path[:]
                best_actions = actions[:]
            if best_state == GOAL:
                return path, actions, len(actions)
    # Nếu không tìm được goal, trả về đường đi tốt nhất đã tìm được
    if best_path:
        return best_path, best_actions, len(best_actions)
    return None, None, 0

def sahc(STATE, GOAL):
    def get_heuristic(state):
        return manhattan_distance(state, GOAL)

    for _ in range(100):  # Thử lại tối đa 100 lần nếu bị mắc kẹt
        current = SearchNode(STATE)
        visited = set()
        while True:
            if current.state == GOAL:
                return extract_path(current)
            visited.add(tuple(current.state))
            neighbors = []
            for action in ["up", "down", "left", "right"]:
                new_state = move(current.state, action)
                if new_state and tuple(new_state) not in visited:
                    neighbors.append(SearchNode(new_state, current, action, current.cost + 1))
            if not neighbors:
                break
            best_neighbor = min(neighbors, key=lambda node: get_heuristic(node.state))
            if get_heuristic(best_neighbor.state) >= get_heuristic(current.state):
                # Restart với trạng thái ngẫu nhiên hợp lệ
                for _ in range(20):
                    random_state = random.sample(range(9), 9)
                    if is_solvable(random_state):
                        current = SearchNode(random_state)
                        visited = set()
                        break
                else:
                    break
            else:
                current = best_neighbor
    return None, None, 0

def shc(STATE, GOAL, max_restarts=30, steps_per_restart=50):
    def get_heuristic(state):
        return manhattan_distance(state, GOAL)

    best_path = None
    best_actions = None
    best_heuristic = float('inf')

    for _ in range(max_restarts):
        current = SearchNode(STATE)
        path = [STATE[:]]
        actions = []
        visited = set()
        for _ in range(steps_per_restart):
            if current.state == GOAL:
                return path, actions, len(actions)
            visited.add(tuple(current.state))
            neighbors = []
            for action in ["up", "down", "left", "right"]:
                new_state = move(current.state, action)
                if new_state and tuple(new_state) not in visited:
                    neighbors.append((get_heuristic(new_state), action, new_state))
            if not neighbors:
                break
            # Chọn ngẫu nhiên một hàng xóm tốt hơn (nếu có)
            better_neighbors = [n for n in neighbors if n[0] < get_heuristic(current.state)]
            if better_neighbors:
                _, chosen_action, chosen_state = random.choice(better_neighbors)
            else:
                # Nếu không có hàng xóm tốt hơn, chọn ngẫu nhiên một hàng xóm
                _, chosen_action, chosen_state = random.choice(neighbors)
            current = SearchNode(chosen_state)
            path.append(chosen_state)
            actions.append(chosen_action)
            # Cập nhật best nếu tốt hơn
            h = get_heuristic(chosen_state)
            if h < best_heuristic:
                best_heuristic = h
                best_path = path[:]
                best_actions = actions[:]
            if chosen_state == GOAL:
                return path, actions, len(actions)
    # Nếu không tìm được goal, trả về đường đi tốt nhất đã tìm được
    if best_path:
        return best_path, best_actions, len(best_actions)
    return None, None, 0

def genetic_algorithm(initial_state, goal_state, population_size=200, generations=1000, mutation_rate=0.7):
    def fitness(individual):
        """Tính độ phù hợp dựa trên khoảng cách Manhattan của trạng thái cuối cùng."""
        state = get_state_from_actions(initial_state, individual)
        distance = manhattan_distance(state, goal_state)
        penalty = 0 if state == goal_state else 50  # Phạt nặng nếu không phải goal_state
        return -(distance + penalty)

    def get_state_from_actions(start_state, actions):
        """Áp dụng chuỗi hành động để lấy trạng thái cuối cùng."""
        state = start_state[:]
        for action in actions:
            new_state = move(state, action)
            if new_state:
                state = new_state
        return state

    def get_path_from_actions(start_state, actions):
        """Tạo danh sách các trạng thái từ chuỗi hành động."""
        path = [start_state[:]]
        current_state = start_state[:]
        for action in actions:
            new_state = move(current_state, action)
            if new_state:
                path.append(new_state)
                current_state = new_state
        return path

    def crossover(parent1, parent2):
        """Lai hai chuỗi hành động."""
        # Kiểm tra độ dài của cha mẹ
        if len(parent1) <= 1 or len(parent2) <= 1:
            return parent1 if len(parent1) > len(parent2) else parent2

        # Chọn điểm cắt ngẫu nhiên, nhưng đảm bảo không cắt chuỗi quá ngắn
        crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]

        # Loại bỏ các hành động trùng lặp liên tiếp để tối ưu chuỗi
        optimized_child = []
        last_action = None
        for action in child:
            if action != last_action:
                optimized_child.append(action)
                last_action = action

        # Giới hạn độ dài
        if len(optimized_child) > 15:
            optimized_child = optimized_child[:15]
        return optimized_child

    def mutate(actions):
        """Đột biến bằng cách thay đổi, thêm hoặc xóa hành động."""
        if random.random() < mutation_rate:
            actions = actions[:]
            num_mutations = random.randint(1, 3)  # Áp dụng 1-3 đột biến
            for _ in range(num_mutations):
                mutation_type = random.choice(["replace", "add", "remove"])
                if mutation_type == "replace" and actions:
                    idx = random.randint(0, len(actions) - 1)
                    actions[idx] = random.choice(["up", "down", "left", "right"])
                elif mutation_type == "add":
                    actions.insert(random.randint(0, len(actions)), random.choice(["up", "down", "left", "right"]))
                elif mutation_type == "remove" and actions:
                    actions.pop(random.randint(0, len(actions) - 1))
            # Giới hạn độ dài
            if len(actions) > 15:
                actions = actions[:15]
            elif len(actions) == 0:
                actions = [random.choice(["up", "down", "left", "right"])]
        return actions

    # Khởi tạo quần thể: Mỗi cá thể là một chuỗi hành động
    population = []
    for _ in range(population_size):
        actions = []
        current_state = initial_state[:]
        for _ in range(random.randint(3, 8)):  # Chuỗi ngắn hơn để gần goal
            action = random.choice(["up", "down", "left", "right"])
            new_state = move(current_state, action)
            if new_state:
                actions.append(action)
                current_state = new_state
        if is_solvable(current_state):
            population.append(actions)

    # Chạy thuật toán di truyền
    for generation in range(generations):
        # Sắp xếp quần thể theo độ phù hợp
        population.sort(key=fitness, reverse=True)

        # Kiểm tra cá thể tốt nhất
        best_individual = population[0]
        best_state = get_state_from_actions(initial_state, best_individual)
        if best_state == goal_state:
            solution_path = get_path_from_actions(initial_state, best_individual)
            return solution_path, best_individual, len(best_individual)

        # Chọn một nửa quần thể tốt nhất
        next_generation = population[:population_size // 2]

        # Tạo cá thể mới qua lai và đột biến
        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(next_generation, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            child_state = get_state_from_actions(initial_state, child)
            if is_solvable(child_state):
                next_generation.append(child)

        population = next_generation

    # Nếu không tìm thấy giải pháp chính xác, trả về None
    return None, None, 0


def beam_search(initial_state, goal_state, beam_width=3):
    frontier = [SearchNode(initial_state, cost=0)]
    explored = set()

    while frontier:
        frontier.sort(key=lambda node: manhattan_distance(node.state, goal_state))
        if len(frontier) > beam_width:
            frontier = frontier[:beam_width]

        node = frontier.pop(0)
        if node.state == goal_state:
            return extract_path(node)

        explored.add(tuple(node.state))

        for action in ["up", "down", "left", "right"]:
            new_state = move(node.state, action)
            if new_state and tuple(new_state) not in explored:
                frontier.append(SearchNode(new_state, node, action, node.cost + 1))

    return None,None, 0

def simulated_annealing(STATE, GOAL, initial_temp=10, cooling_rate=0.9):
    def get_heuristic(state):
        return manhattan_distance(state, GOAL)

    current = SearchNode(STATE)
    temp = initial_temp

    while temp > 0.0001:
        if current.state == GOAL:
            return extract_path(current)

        neighbors = []
        for action in ["up", "down", "left", "right"]:
            new_state = move(current.state, action)
            if new_state:
                neighbors.append(SearchNode(new_state, current, action, current.cost + 1))

        if not neighbors:
            break

        next_node = random.choice(neighbors)
        delta_e = get_heuristic(next_node.state) - get_heuristic(current.state)

        if delta_e < 0 or random.random() < math.exp(-delta_e / temp):
            current = next_node

        temp *= cooling_rate

    return None, None, 0

def and_or_search(initial_state, goal_state):
    """AND-OR search for the 8-puzzle problem."""
    def recursive_search(node, explored, depth_limit=25):
        """Recursively search for a solution."""
        if depth_limit <= 0:
            return None, None, float('inf')  # Stop recursion if depth limit is exceeded

        if node.state == goal_state:
            return [node.state], [], node.cost  # Return path, actions, and cost

        state_tuple = tuple(node.state)
        if state_tuple in explored:
            return None, None, float('inf')  # Avoid cycles

        explored.add(state_tuple)
        best_path = None
        best_actions = None
        best_cost = float('inf')

        # Explore all possible actions (OR node)
        for action in ["up", "down", "left", "right"]:
            new_state = move(node.state, action)
            if new_state:  # Only proceed if the move is valid
                # Create a new node for the child state
                child_node = SearchNode(new_state, node, action, node.cost + 1)
                # Recursively search the child state
                child_path, child_actions, child_cost = recursive_search(child_node, explored, depth_limit - 1)

                # If a valid path is found and its cost is lower, update the best solution
                if child_path is not None and child_cost < best_cost:
                    best_path = [node.state] + child_path
                    best_actions = [action] + child_actions
                    best_cost = child_cost

        explored.remove(state_tuple)  # Backtrack to allow other paths to explore this state
        if best_path is None:
            return None, None, float('inf')
        return best_path, best_actions, best_cost

    # Initialize the search with the initial state
    initial_node = SearchNode(initial_state, cost=0)
    explored = set()
    path, actions, cost = recursive_search(initial_node, explored)

    if path is None:
        return None, None, 0  # No solution found
    return path, actions, cost

def backtracking_search(initial_state, goal_state, max_depth=30):
    """Backtracking search cho bài toán 8-puzzle"""
    def recursive_search(state, depth, path, actions):
        if state == tuple(goal_state):  # So sánh với tuple(goal_state)
            return path, actions, len(actions)

        if depth >= max_depth:
            return None, None, 0

        for action in ["up", "down", "left", "right"]:
            new_state_list = move(list(state), action)  # chuyển tuple -> list để dùng hàm move
            if new_state_list is not None:
                new_state = tuple(new_state_list)  # chuyển lại list -> tuple để dùng trong path
                if new_state not in set(path):
                    result_path, result_actions, cost = recursive_search(
                        new_state, depth + 1, path + [new_state], actions + [action]
                    )
                    if result_path:
                        return result_path, result_actions, cost

        return None, None, 0

    return recursive_search(tuple(initial_state), 0, [tuple(initial_state)], [])

def partial_order_search(initial_state, goal_state, max_depth=30):
    """Tìm kiếm theo thứ tự một phần cho bài toán 8-puzzle (giới hạn độ sâu)"""
    def recursive_search(state, path, actions, depth):
        if state == tuple(goal_state):
            return path, actions, len(actions)
        if depth >= max_depth:
            return None, None, 0
        for action in ["up", "down", "left", "right"]:
            new_state_list = move(list(state), action)
            if new_state_list is not None:
                new_state = tuple(new_state_list)
                if new_state not in set(path):
                    result_path, result_actions, cost = recursive_search(
                        new_state, path + [new_state], actions + [action], depth + 1
                    )
                    if result_path:
                        return result_path, result_actions, cost
        return None, None, 0

    return recursive_search(tuple(initial_state), [tuple(initial_state)], [], 0)

def q_learning_solve(initial_state, goal_state, episodes=100000, alpha=0.1, gamma=0.95, epsilon=1.0, min_epsilon=0.05, decay=0.9995, max_steps=300):
    import pickle
    import os
    from collections import defaultdict

    actions = ["up", "down", "left", "right"]
    q_table_file = "q_table.pkl"

    # Tải Q-table nếu đã lưu
    if os.path.exists(q_table_file):
        with open(q_table_file, "rb") as f:
            q_table = defaultdict(lambda: {a: 0.0 for a in actions}, pickle.load(f))
    else:
        q_table = defaultdict(lambda: {a: 0.0 for a in actions})

    def choose_action(state, epsilon):
        if random.random() < epsilon:
            return random.choice(actions)
        q_vals = q_table[tuple(state)]
        return max(q_vals, key=q_vals.get)

    for ep in range(episodes):
        state = initial_state[:]
        for _ in range(max_steps):
            action = choose_action(state, epsilon)
            next_state = move(state, action)
            if not next_state:
                next_state = state
                reward = -5
            elif next_state == goal_state:
                reward = 100
            else:
                reward = -1

            next_max_q = max(q_table[tuple(next_state)].values())
            q_table[tuple(state)][action] += alpha * (reward + gamma * next_max_q - q_table[tuple(state)][action])

            if next_state == goal_state:
                break
            state = next_state
        # Giảm epsilon dần
        if epsilon > min_epsilon:
            epsilon *= decay

    # Lưu Q-table lại
    with open(q_table_file, "wb") as f:
        pickle.dump(dict(q_table), f)

    # Trích xuất lời giải tốt nhất sau khi học
    state = initial_state[:]
    path = [state[:]]
    actions_taken = []
    visited = set()
    for _ in range(max_steps):
        best_action = max(q_table[tuple(state)], key=q_table[tuple(state)].get)
        next_state = move(state, best_action)
        if not next_state or tuple(next_state) in visited:
            break
        path.append(next_state)
        actions_taken.append(best_action)
        visited.add(tuple(next_state))
        if next_state == goal_state:
            return path, actions_taken, len(actions_taken)
        state = next_state

    # Nếu không đến được goal, trả về đường đi tốt nhất tìm được
    return path, actions_taken, len(actions_taken)
def belief_search(belief_state, goal_state):
    """
    Tìm kiếm trên không gian belief state để tìm chuỗi hành động chung dẫn tất cả trạng thái đến goal_state.
    Trả về: (solution_paths, actions, cost)
    """
    from collections import deque
    import heapq

    # Chuyển belief_state thành tập hợp các tuple
    initial_belief = [tuple(state) for state in belief_state]  # Giữ thứ tự gốc
    goal_tuple = tuple(goal_state)
    explored = set()
    visited = set()
    max_steps = 5000

    # Hàng đợi ưu tiên: (heuristic + cost, cost, belief_state, actions)
    frontier = [(0, 0, set(initial_belief), [])]
    belief_states_path = [list(initial_belief)]

    # Thêm trạng thái ban đầu vào explored
    for state in initial_belief:
        explored.add(state)

    def belief_heuristic(belief_state):
        """Heuristic: Tổng khoảng cách Manhattan của tất cả trạng thái trong belief_state"""
        return sum(manhattan_distance(list(state), goal_state) for state in belief_state)

    while frontier and len(explored) < max_steps:
        _, cost, belief_state, actions = heapq.heappop(frontier)
        belief_state_tuple = frozenset(belief_state)

        # Kiểm tra mục tiêu: Tất cả trạng thái trong belief_state phải là goal_state
        if all(state == goal_tuple for state in belief_state):
            # Tạo solution_paths: Lưu trạng thái cho mỗi bước của actions
            solution_paths = []
            current_states = [list(state) for state in initial_belief]  # Sử dụng initial_belief gốc
            solution_paths.append(current_states[:])  # Lưu trạng thái ban đầu
            for action in actions:
                next_states = []
                for state in current_states:
                    new_state = move(state, action)
                    next_states.append(new_state if new_state else state[:])
                solution_paths.append(next_states[:])
                current_states = next_states
            return solution_paths, actions, len(actions)

        if belief_state_tuple in visited:
            continue
        visited.add(belief_state_tuple)

        # Thử các hành động: right, left, down, up (ưu tiên right)
        for action in ["right", "left", "down", "up"]:
            new_belief = set()
            for state in belief_state:
                state_list = list(state)
                next_state = move(state_list, action)
                if next_state:
                    new_belief.add(tuple(next_state))
                else:
                    new_belief.add(state)

            # Thu hẹp belief state: Giữ 3 trạng thái có heuristic tốt nhất
            if new_belief:
                new_belief = set(
                    sorted(new_belief, key=lambda s: manhattan_distance(list(s), goal_state))[:3]
                )
                for state in new_belief:
                    if state not in explored:
                        explored.add(state)
                new_cost = cost + 1
                heapq.heappush(
                    frontier,
                    (new_cost + belief_heuristic(new_belief), new_cost, new_belief, actions + [action])
                )
                belief_states_path.append(list(new_belief))

    return [[] for _ in belief_state], [], 0

def backtacking_forward_search(initial_state, goal_state):
    """
    Tìm kiếm theo chiều tiến lùi cho bài toán 8-puzzle.
    Trả về: (solution_paths, actions, cost)
    """
    def recursive_search(state, depth, path, actions):
        if state == tuple(goal_state):
            return path, actions, len(actions)

        if depth >= 30:
            return None, None, 0

        for action in ["up", "down", "left", "right"]:
            new_state_list = move(list(state), action)
            if new_state_list is not None:
                new_state = tuple(new_state_list)
                if new_state not in set(path):
                    result_path, result_actions, cost = recursive_search(
                        new_state, depth + 1, path + [new_state], actions + [action]
                    )
                    if result_path:
                        return result_path, result_actions, cost

        return None, None, 0

    return recursive_search(tuple(initial_state), 0, [tuple(initial_state)], [])

def min_conflict_search(initial_state, goal_state, max_steps=100):
    """
    Tìm kiếm xung đột tối thiểu cho bài toán 8-puzzle.
    Trả về: (solution_paths, actions, cost)
    """
    def get_heuristic(state):
        return manhattan_distance(state, goal_state)

    current = SearchNode(initial_state)
    path = [tuple(initial_state)]
    actions = []
    visited = set()
    for _ in range(max_steps):
        if current.state == goal_state:
            return [list(s) for s in path], actions, len(actions)

        visited.add(tuple(current.state))

        # Tìm tất cả hàng xóm hợp lệ chưa đi qua
        neighbors = []
        for action in ["up", "down", "left", "right"]:
            new_state = move(current.state, action)
            if new_state and tuple(new_state) not in visited:
                neighbors.append((get_heuristic(new_state), action, new_state))

        if not neighbors:
            break

        # Chọn hàng xóm có heuristic nhỏ nhất (ít xung đột nhất)
        neighbors.sort(key=lambda x: x[0])
        best_heuristic, best_action, best_state = neighbors[0]

        # Nếu không cải thiện, chọn ngẫu nhiên một hàng xóm để tránh mắc kẹt
        if best_heuristic >= get_heuristic(current.state):
            best_heuristic, best_action, best_state = random.choice(neighbors)

        current = SearchNode(best_state)
        path.append(tuple(best_state))
        actions.append(best_action)

    return None, None, 0  # Không tìm thấy lời giải

def randomize_state():
    global STATE
    STATE = GOAL[:]  # Sao chép trạng thái GOAL
    random.shuffle(STATE)  # Xáo trộn ngẫu nhiên
    while not is_solvable(STATE):  # Đảm bảo trạng thái có thể giải được
        random.shuffle(STATE)  # Xáo trộn lại nếu không giải được

def draw_button(x, y, text, is_pressed=False):
    """Vẽ nút có hiệu ứng nhấn"""
    width, height = 120, 50
    rect = pygame.Rect(x, y, width, height)

    bg_color = (230, 180, 100) if is_pressed else TILE_COLOR  
    pygame.draw.rect(SCREEN, bg_color, rect)  
    pygame.draw.rect(SCREEN, SHADOW, rect, 3)  

    pygame.draw.polygon(SCREEN, HIGHLIGHT, [(x, y), (x + width, y), (x + width - 3, y + 3), (x + 3, y + 3)])
    pygame.draw.polygon(SCREEN, HIGHLIGHT, [(x, y), (x, y + height), (x + 3, y + height - 3), (x + 3, y + 3)])

    pygame.draw.polygon(SCREEN, SHADOW, [(x + width, y), (x + width, y + height), (x + width - 3, y + height - 3), (x + width - 3, y + 3)])
    pygame.draw.polygon(SCREEN, SHADOW, [(x, y + height), (x + width, y + height), (x + width - 3, y + height - 3), (x + 3, y + height - 3)])

    text_surf = FONT.render(text, True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    SCREEN.blit(text_surf, text_rect)

    return rect  

def get_tile_index(x, y, start_x, start_y):
    """Xác định chỉ số ô trong mảng dựa trên vị trí chuột"""
    if start_x <= x < start_x + 3 * TILE_SIZE and start_y <= y < start_y + 3 * TILE_SIZE:
        col = (x - start_x) // TILE_SIZE
        row = (y - start_y) // TILE_SIZE
        return row * 3 + col
    return None

def draw_grid(start_x, start_y, grid_data, selected_idx):
    """Vẽ lưới 3x3 tại vị trí chỉ định"""
    for row in range(3):
        for col in range(3):
            index = row * 3 + col
            num = grid_data[index]
            x = start_x + col * TILE_SIZE
            y = start_y + row * TILE_SIZE
            draw_tile(x, y, num, index == selected_idx)

def draw_tile(x, y, num, is_selected):
    """Vẽ một ô trong bảng"""
    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
    color = (255, 220, 150) if is_selected else TILE_COLOR  
    pygame.draw.rect(SCREEN, color, rect)

    pygame.draw.polygon(SCREEN, HIGHLIGHT, [(x, y), (x + TILE_SIZE, y), (x + TILE_SIZE - 5, y + 5), (x + 5, y + 5)])
    pygame.draw.polygon(SCREEN, HIGHLIGHT, [(x, y), (x, y + TILE_SIZE), (x + 5, y + TILE_SIZE - 5), (x + 5, y + 5)])
    pygame.draw.polygon(SCREEN, SHADOW, [(x + TILE_SIZE, y), (x + TILE_SIZE, y + TILE_SIZE),
                                         (x + TILE_SIZE - 5, y + TILE_SIZE - 5), (x + TILE_SIZE - 5, y + 5)])
    pygame.draw.polygon(SCREEN, SHADOW, [(x, y + TILE_SIZE), (x + TILE_SIZE, y + TILE_SIZE),
                                         (x + TILE_SIZE - 5, y + TILE_SIZE - 5), (x + 5, y + TILE_SIZE - 5)])

    if num != 0:
        text = FONT.render(str(num), True, TEXT_COLOR)
        text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
        SCREEN.blit(text, text_rect)
    else:
        pygame.draw.rect(SCREEN, (200, 200, 200), rect)

def wrap_text(text, font, max_width):
    """
    Tự động xuống dòng văn bản để vừa với chiều rộng max_width.
    """
    lines = []
    words = text.split()
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        lines.append(current_line.strip())

    return lines

def draw_scrollable_textbox(screen, rect, text, font, scroll_y, scroll_speed=30):
    # Chỉ tính toán lại wrapped_lines khi văn bản thay đổi
    if not hasattr(draw_scrollable_textbox, 'wrapped_lines') or text != draw_scrollable_textbox.text:
        draw_scrollable_textbox.wrapped_lines = []
        for paragraph in text.split('\n'):
            draw_scrollable_textbox.wrapped_lines.extend(wrap_text(paragraph, font, rect.width - 10))
        draw_scrollable_textbox.text = text

    wrapped_lines = draw_scrollable_textbox.wrapped_lines
    line_height = font.get_linesize()
    total_height = len(wrapped_lines) * line_height

    # Xử lý sự kiện cuộn
    keys = pygame.key.get_pressed()
    if keys[pygame.K_DOWN]:
        scroll_y = min(scroll_y + scroll_speed, max(total_height - rect.height, 0))
    elif keys[pygame.K_UP]:
        scroll_y = max(scroll_y - scroll_speed, 0)

    for event in pygame.event.get(pygame.MOUSEBUTTONDOWN):
        if event.button == 4:
            scroll_y = max(scroll_y - scroll_speed, 0)
        elif event.button == 5:
            scroll_y = min(scroll_y + scroll_speed, max(total_height - rect.height, 0))

    # Vẽ nền textbox
    pygame.draw.rect(screen, (255, 255, 255), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    # Tính dòng bắt đầu và kết thúc cần hiển thị
    start_line = scroll_y // line_height
    end_line = start_line + (rect.height // line_height) + 1

    visible_lines = wrapped_lines[start_line:end_line]

    # Vẽ các dòng có thể thấy
    for i, line in enumerate(visible_lines):
        y = rect.y + i * line_height - (scroll_y % line_height)
        rendered = font.render(line, True, (0, 0, 0))
        screen.blit(rendered, (rect.x + 5, y))

    return scroll_y


button_rects = {text: draw_button(x, y, text) for text, x, y in BUTTONS}
click = None
solution_path = None
action = None
cost = 0
scroll_y = 0 

while True:
    SCREEN.fill(BLUE_BG)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    text_state = FONT.render("State", True, TEXT_COLOR)
    SCREEN.blit(text_state, (x_state + 90, y_state - 30))
    text_goal = FONT.render("Goal", True, TEXT_COLOR)
    SCREEN.blit(text_goal, (x_goal + 90, y_goal - 30))

    draw_grid(x_state, y_state, STATE, selected_index)
    draw_grid(x_goal, y_goal, GOAL, None)

    button_rects = {text: draw_button(x, y, text, pressed_button == text) for text, x, y in BUTTONS}

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            for text, rect in button_rects.items():
                if rect.collidepoint(mouse_x, mouse_y):
                    pressed_button = text
                    print (f"{pressed_button} button pressed!")
                    break
            

        elif event.type == pygame.MOUSEBUTTONUP:
            if pressed_button and button_rects[pressed_button].collidepoint(mouse_x, mouse_y):
                print(f"{pressed_button} button clicked!")
                click = pressed_button

        elif event.type == pygame.KEYDOWN and selected_index is not None:
            if pygame.K_1 <= event.key <= pygame.K_8:
                num = event.key - pygame.K_0
                STATE[selected_index] = num
                selected_index = None
            elif event.key == pygame.K_BACKSPACE:
                STATE[selected_index] = 0
                selected_index = None
    if click:
        start_time = time.time()
        
        if is_solvable(STATE):
            if click == "BFS":
                solution_path,action, cost = bfs_solve(STATE, GOAL)
            elif click == "DFS":
                solution_path,action, cost = dfs_solve(STATE, GOAL)
            elif click == "IDDFS":
                solution_path,action, cost = iterative_deepening_dfs_solve(STATE, GOAL)
            elif click == "UCS":
                solution_path,action, cost = uniform_cost_search(STATE, GOAL)
            elif click == "Greedy":
                solution_path,action, cost = greedy_best_first_search(STATE, GOAL)
            elif click == "A*":
                solution_path,action, cost = a_star_search(STATE, GOAL)
            elif click == "Genetic":
                try:
                    solution_path, action, cost = genetic_algorithm(STATE, GOAL)
                except Exception as e:
                    print(f"Error in genetic_algorithm: {e}")
                    solution_path, action, cost = None, None, 0
            elif click == "IDA*":
                solution_path,action, cost = ida_star_search(STATE, GOAL)
            elif click == "Beam":
                solution_path,action, cost = beam_search(STATE, GOAL)
            elif click == "BackFor":
                solution_path,action, cost = backtacking_forward_search(STATE, GOAL)
            elif click == "MinConf":
                solution_path,action, cost = min_conflict_search(STATE, GOAL)
            elif click == "POS":
                solution_path,action, cost = partial_order_search(STATE, GOAL)
            elif click == "SA":
                while True:
                    solution_path,action, cost = simulated_annealing(STATE, GOAL)
                    if solution_path:
                        break
            elif click == "HC":
                solution_path,action, cost = hill_climbing(STATE, GOAL)
            elif click == "SAHC":
                solution_path,action, cost = sahc(STATE, GOAL)
            elif click == "SHC":
                    solution_path,action, cost = shc(STATE, GOAL)
            elif click == "and-or":
                solution_path,action, cost = and_or_search(STATE, GOAL)
            elif click == "Belief":
                screen_belief_algorithm()
                # solution_path,action, cost = belief_search(STATE, GOAL)
            elif click == "BackTrack":
                solution_path,action, cost = backtracking_search(STATE, GOAL)
            elif click == "Q-lerning":
                solution_path,action, cost = q_learning_solve(STATE, GOAL)
                    
            
        if click == "Random":
            randomize_state()
            solution_path = None
            action = None
            cost = 0
        elif click == "Reset":
            STATE = [3, 1, 6,
                     5, 0, 8,
                     2, 4, 7]
            selected_index = None
            solution_path = None
            action = None
            cost = 0
        elif click == "Easy":
            STATE = [5, 1, 3,
                    0, 2, 6,
                    4, 7, 8]
            selected_index = None
            solution_path = None
            action = None
            cost = 0
        execution_time = time.time() - start_time 
        click = None


    text_cost = FONT.render(f"Cost: {cost}", True, TEXT_COLOR)
    SCREEN.blit(text_cost, (70, 320))
    


    text_time = FONT.render(f"Time: {execution_time:.6f}", True, TEXT_COLOR)
    SCREEN.blit(text_time, (250, 320))

    scroll_y = draw_scrollable_textbox(SCREEN, pygame.Rect(780, 50, 300, 200), str(action), FONT_ACTION, scroll_y)    

    if solution_path:
        state = solution_path.pop(0)
        draw_grid(x_state, y_state, state, None)
        STATE = state
        pygame.display.flip()
        pygame.time.delay(100)

    pygame.display.update()
