import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import heapq
import math
import csv
from itertools import permutations

# 한글 폰트 설정
def setup_korean_font():
    """한글 폰트를 설정합니다."""
    try:
        # macOS의 기본 한글 폰트 사용
        font_path = '/System/Library/Fonts/AppleSDGothicNeo.ttc'
        font_prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = font_prop.get_name()
        plt.rcParams['axes.unicode_minus'] = False
    except:
        # 폰트를 찾을 수 없는 경우 기본 설정
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False

def load_data():
    """CSV 데이터를 로드하고 좌표를 0-14로 변환합니다."""
    df = pd.read_csv('integrated_area_data.csv')
    # 좌표를 0-14로 변환 (1-15에서 1을 빼기)
    df['x'] = df['x'] - 1
    df['y'] = df['y'] - 1
    return df

def create_grid_matrix(df):
    """그리드 매트릭스를 생성합니다."""
    max_x = df['x'].max()
    max_y = df['y'].max()
    
    # 그리드 초기화 (0: 이동 가능, 1: 건설현장으로 이동 불가)
    grid = [[0 for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    
    # 구조물 정보 저장
    structures = {}
    
    for _, row in df.iterrows():
        x, y = int(row['x']), int(row['y'])
        
        # 건설현장은 이동 불가
        if row['ConstructionSite'] == 1:
            grid[y][x] = 1
        
        # 구조물 정보 저장
        if row['struct'] != '일반 지역':
            structures[(x, y)] = row['struct'].strip()
    
    return grid, structures, max_x, max_y

def heuristic(a, b):
    """A* 알고리즘의 휴리스틱 함수 (맨하탄 거리)"""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(pos, max_x, max_y):
    """주변 8방향의 이웃 좌표를 반환합니다."""
    x, y = pos
    neighbors = []
    
    # 8방향 이동 (상하좌우 + 대각선)
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    for dx, dy in directions:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x <= max_x and 0 <= new_y <= max_y:
            neighbors.append((new_x, new_y))
    
    return neighbors

def a_star_pathfinding(grid, start, goal, max_x, max_y):
    """A* 알고리즘으로 최단 경로를 찾습니다."""
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current == goal:
            # 경로 재구성
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        
        for neighbor in get_neighbors(current, max_x, max_y):
            nx, ny = neighbor
            
            # 건설현장은 지나갈 수 없음
            if grid[ny][nx] == 1:
                continue
            
            # 대각선 이동의 경우 거리 계산
            if abs(neighbor[0] - current[0]) == 1 and abs(neighbor[1] - current[1]) == 1:
                tentative_g_score = g_score[current] + math.sqrt(2)
            else:
                tentative_g_score = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                
                if (f_score[neighbor], neighbor) not in open_set:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return None  # 경로를 찾을 수 없음

def calculate_path_distance(path):
    """경로의 총 거리를 계산합니다."""
    if not path or len(path) < 2:
        return 0
    
    total_distance = 0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        
        # 대각선 이동인지 확인
        if abs(x2 - x1) == 1 and abs(y2 - y1) == 1:
            total_distance += math.sqrt(2)
        else:
            total_distance += 1
    
    return total_distance

def find_optimal_structure_tour(grid, home, structures, max_x, max_y):
    """모든 구조물을 한 번씩 방문하는 최적화된 경로를 계산합니다 (TSP 변형)."""
    # 구조물 위치만 추출 (내 집 제외)
    structure_positions = [pos for pos, name in structures.items() if 'MyHome' not in name]
    
    if not structure_positions:
        return None, 0
    
    best_total_path = None
    best_total_distance = float('inf')
    
    # 모든 구조물 방문 순서의 순열을 시도
    for perm in permutations(structure_positions):
        total_path = [home]  # 집에서 시작
        total_distance = 0
        current_pos = home
        valid_tour = True
        
        # 각 구조물을 순서대로 방문
        for target_pos in perm:
            path_segment = a_star_pathfinding(grid, current_pos, target_pos, max_x, max_y)
            if path_segment is None:
                valid_tour = False
                break
            
            # 경로 연결 (시작점 중복 제거)
            total_path.extend(path_segment[1:])
            total_distance += calculate_path_distance(path_segment)
            current_pos = target_pos
        
        # 마지막에 집으로 돌아가기
        if valid_tour:
            return_path = a_star_pathfinding(grid, current_pos, home, max_x, max_y)
            if return_path is not None:
                total_path.extend(return_path[1:])
                total_distance += calculate_path_distance(return_path)
                
                if total_distance < best_total_distance:
                    best_total_path = total_path
                    best_total_distance = total_distance
    
    return best_total_path, best_total_distance

def save_path_to_csv(path, filename):
    """경로를 CSV 파일로 저장합니다."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['step', 'x', 'y'])
        for i, (x, y) in enumerate(path):
            writer.writerow([i + 1, x, y])

def draw_map_with_path(df, path, structures, max_x, max_y, bonus_path=None):
    """지도와 경로를 그립니다 - 그래픽스 좌표계 (0,0 시작)"""
    
    fig, ax = plt.subplots(figsize=(14, 12))
    
    # 배경 설정 (0-14 좌표계)
    ax.set_xlim(-0.5, max_x + 0.5)
    ax.set_ylim(-0.5, max_y + 0.5)
    ax.set_aspect('equal')
    
    # 그리드 라인 그리기
    for i in range(max_x + 2):
        ax.axvline(x=i - 0.5, color='lightgray', linewidth=0.5)
    for i in range(max_y + 2):
        ax.axhline(y=i - 0.5, color='lightgray', linewidth=0.5)
    
    # 건설현장과 구조물 그리기
    for _, row in df.iterrows():
        x, y = int(row['x']), int(row['y'])
        
        # 건설현장 (회색 사각형)
        if row['ConstructionSite'] == 1:
            rect = patches.Rectangle((x - 0.4, y - 0.4), 0.8, 0.8, 
                                   linewidth=1, edgecolor='gray', 
                                   facecolor='gray', alpha=0.7)
            ax.add_patch(rect)
        
        # 구조물 그리기
        struct_name = row['struct'].strip()
        if struct_name == 'Apartment' or struct_name == 'Building':
            circle = patches.Circle((x, y), 0.3, color='brown', alpha=0.8)
            ax.add_patch(circle)
        elif struct_name == 'MyHome':
            triangle = patches.RegularPolygon((x, y), 3, radius=0.3, 
                                            orientation=0, color='green', alpha=0.8)
            ax.add_patch(triangle)
        elif struct_name == 'BandalgomCoffee':
            rect = patches.Rectangle((x - 0.3, y - 0.3), 0.6, 0.6, 
                                   linewidth=1, edgecolor='orange', 
                                   facecolor='orange', alpha=0.8)
            ax.add_patch(rect)
    
    # 기본 최단 경로 그리기 (빨간 선)
    if path and len(path) > 1:
        path_x = [pos[0] for pos in path]
        path_y = [pos[1] for pos in path]
        ax.plot(path_x, path_y, 'r-', linewidth=3, alpha=0.8, label='최단 경로 (집→커피숍)')
        
        # 시작점과 끝점 표시
        ax.plot(path[0][0], path[0][1], 'ro', markersize=10, label='시작점 (내 집)')
        ax.plot(path[-1][0], path[-1][1], 'bs', markersize=10, label='도착점 (반달곰 커피)')
    
    # 보너스: 모든 구조물 방문 경로 그리기 (파란 선)
    if bonus_path and len(bonus_path) > 1:
        bonus_x = [pos[0] for pos in bonus_path]
        bonus_y = [pos[1] for pos in bonus_path]
        ax.plot(bonus_x, bonus_y, 'b--', linewidth=2, alpha=0.6, label='모든 구조물 방문 경로')
    
    # 좌표축 설정 (그래픽스 좌표계 - 좌상단이 (0,0))
    ax.set_xticks(range(0, max_x + 1))
    ax.set_yticks(range(0, max_y + 1))
    ax.invert_yaxis()  # y축 뒤집기 (그래픽스 좌표계)
    
    # 제목과 라벨
    ax.set_title('최단 경로 탐색 결과 - 그래픽스 좌표계 (좌상단 (0,0))', fontsize=16, fontweight='bold')
    ax.set_xlabel('X 좌표', fontsize=12)
    ax.set_ylabel('Y 좌표', fontsize=12)
    
    # 범례
    legend_elements = [
        patches.Patch(color='gray', alpha=0.7, label='건설 현장 (이동 불가)'),
        patches.Patch(color='brown', alpha=0.8, label='아파트/빌딩'),
        patches.Patch(color='green', alpha=0.8, label='내 집'),
        patches.Patch(color='orange', alpha=0.8, label='반달곰 커피'),
        plt.Line2D([0], [0], color='red', linewidth=3, alpha=0.8, label='최단 경로')
    ]
    
    if bonus_path:
        legend_elements.append(
            plt.Line2D([0], [0], color='blue', linewidth=2, linestyle='--', alpha=0.6, label='모든 구조물 방문')
        )
    
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))
    
    # 정보 텍스트 박스
    info_lines = []
    if path:
        distance = calculate_path_distance(path)
        info_lines.append(f'최단 경로: {len(path)}단계')
        info_lines.append(f'총 거리: {distance:.2f}칸')
    
    if bonus_path:
        bonus_distance = calculate_path_distance(bonus_path)
        info_lines.append(f'구조물 투어: {len(bonus_path)}단계')
        info_lines.append(f'투어 거리: {bonus_distance:.2f}칸')
    
    if info_lines:
        info_text = '\n'.join(info_lines)
        ax.text(0.98, 0.02, info_text, transform=ax.transAxes, 
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                verticalalignment='bottom', horizontalalignment='right')
    
    plt.tight_layout()
    plt.savefig('map_final.png', dpi=300, bbox_inches='tight')
    plt.close()

def find_coffee_locations(structures):
    """반달곰 커피 위치를 찾습니다."""
    coffee_locations = []
    for pos, struct_name in structures.items():
        if 'BandalgomCoffee' in struct_name:
            coffee_locations.append(pos)
    return coffee_locations

def find_home_location(structures):
    """내 집 위치를 찾습니다."""
    for pos, struct_name in structures.items():
        if 'MyHome' in struct_name:
            return pos
    return None

def main():
    """메인 함수"""
    try:
        # 한글 폰트 설정
        setup_korean_font()
        
        # 데이터 로드
        print('데이터를 로드하는 중...')
        df = load_data()
        
        # 그리드 매트릭스 생성
        print('그리드 매트릭스를 생성하는 중...')
        grid, structures, max_x, max_y = create_grid_matrix(df)
        
        print(f'지도 크기: {max_x + 1} x {max_y + 1} (0-{max_x} x 0-{max_y})')
        
        # 시작점과 도착점 찾기
        home_location = find_home_location(structures)
        coffee_locations = find_coffee_locations(structures)
        
        if not home_location:
            print('내 집을 찾을 수 없습니다.')
            return
        
        if not coffee_locations:
            print('반달곰 커피를 찾을 수 없습니다.')
            return
        
        print(f'시작점 (내 집): {home_location}')
        print(f'도착점 후보 (반달곰 커피): {coffee_locations}')
        
        # 가장 가까운 커피숍 찾기
        best_path = None
        best_goal = None
        shortest_distance = float('inf')
        
        for coffee_pos in coffee_locations:
            print(f'\n{coffee_pos} 위치의 반달곰 커피로의 경로를 탐색 중...')
            path = a_star_pathfinding(grid, home_location, coffee_pos, max_x, max_y)
            
            if path:
                distance = calculate_path_distance(path)
                print(f'경로 발견: {len(path)}단계, 거리: {distance:.2f}칸')
                
                if distance < shortest_distance:
                    best_path = path
                    best_goal = coffee_pos
                    shortest_distance = distance
        
        if best_path:
            print(f'\n=== 최단 경로 결과 ===')
            print(f'목적지: {best_goal}')
            print(f'경로 길이: {len(best_path)}단계')
            print(f'총 거리: {shortest_distance:.2f}칸')
            print(f'경로: {" -> ".join([f"({x},{y})" for x, y in best_path])}')
            
            # CSV 파일로 저장
            print('\n경로를 CSV 파일로 저장하는 중...')
            save_path_to_csv(best_path, 'home_to_cafe.csv')
            print('home_to_cafe.csv 파일이 저장되었습니다.')
            
            # 보너스: 모든 구조물 방문 경로 계산
            print('\n=== 보너스: 모든 구조물 방문 경로 계산 ===')
            bonus_path, bonus_distance = find_optimal_structure_tour(grid, home_location, structures, max_x, max_y)
            
            if bonus_path:
                print(f'모든 구조물 방문 경로 길이: {len(bonus_path)}단계')
                print(f'총 거리: {bonus_distance:.2f}칸')
                print(f'방문 순서: {" -> ".join([f"({x},{y})" for x, y in bonus_path])}')
            else:
                print('모든 구조물을 방문하는 경로를 찾을 수 없습니다.')
            
            # 지도 시각화
            print('\n지도를 시각화하는 중...')
            draw_map_with_path(df, best_path, structures, max_x, max_y, bonus_path)
            print('map_final.png 파일이 저장되었습니다.')
            
        else:
            print('경로를 찾을 수 없습니다. 건설현장으로 인해 막혀있을 수 있습니다.')
    
    except KeyboardInterrupt:
        print('\n사용자에 의해 프로그램이 중단되었습니다.')
    except Exception as e:
        print(f'오류가 발생했습니다: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()