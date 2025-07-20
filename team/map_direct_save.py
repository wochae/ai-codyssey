import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import heapq
import math
import csv

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
    """CSV 데이터를 로드합니다."""
    df = pd.read_csv('/Users/dachae/IdeaProjects/zody/team/integrated_area_data.csv')
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
        if 1 <= new_x <= max_x and 1 <= new_y <= max_y:
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

def save_path_to_csv(path, filename):
    """경로를 CSV 파일로 저장합니다."""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['step', 'x', 'y'])
        for i, (x, y) in enumerate(path):
            writer.writerow([i + 1, x, y])

def draw_map_with_path(df, path, structures, max_x, max_y):
    """지도와 경로를 그립니다."""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # 배경 설정
    ax.set_xlim(0.5, max_x + 0.5)
    ax.set_ylim(0.5, max_y + 0.5)
    ax.set_aspect('equal')
    
    # 그리드 라인 그리기
    for i in range(1, max_x + 2):
        ax.axvline(x=i - 0.5, color='lightgray', linewidth=0.5)
    for i in range(1, max_y + 2):
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
                                   linewidth=1, edgecolor='green', 
                                   facecolor='green', alpha=0.8)
            ax.add_patch(rect)
    
    # 경로 그리기 (빨간 선)
    if path and len(path) > 1:
        path_x = [pos[0] for pos in path]
        path_y = [pos[1] for pos in path]
        ax.plot(path_x, path_y, 'r-', linewidth=3, alpha=0.8, label='최단 경로')
        
        # 시작점과 끝점 표시
        ax.plot(path[0][0], path[0][1], 'ro', markersize=8, label='시작점 (내 집)')
        ax.plot(path[-1][0], path[-1][1], 'bs', markersize=8, label='도착점 (반달곰 커피)')
    
    # 좌표축 설정 (좌측 상단이 (1,1))
    ax.set_xticks(range(1, max_x + 1))
    ax.set_yticks(range(1, max_y + 1))
    ax.invert_yaxis()  # y축 뒤집기
    
    # 제목과 라벨
    ax.set_title('최단 경로 탐색 결과 (15x15 격자)', fontsize=16, fontweight='bold')
    ax.set_xlabel('X 좌표', fontsize=12)
    ax.set_ylabel('Y 좌표', fontsize=12)
    
    # 범례
    legend_elements = [
        patches.Patch(color='gray', alpha=0.7, label='건설 현장 (이동 불가)'),
        patches.Patch(color='brown', alpha=0.8, label='아파트/빌딩'),
        patches.Patch(color='green', alpha=0.8, label='내 집/반달곰 커피'),
        plt.Line2D([0], [0], color='red', linewidth=3, alpha=0.8, label='최단 경로')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98))
    
    # 정보 텍스트 박스
    if path:
        info_text = f'경로 길이: {len(path)}단계\n총 거리: {len(path)-1}칸'
        ax.text(0.98, 0.02, info_text, transform=ax.transAxes, 
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
                verticalalignment='bottom', horizontalalignment='right')
    
    plt.tight_layout()
    plt.savefig('/Users/dachae/IdeaProjects/zody/team/map_final.png', 
                dpi=300, bbox_inches='tight')
    plt.show()

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
            
            if path and len(path) < shortest_distance:
                best_path = path
                best_goal = coffee_pos
                shortest_distance = len(path)
        
        if best_path:
            print(f'\n최단 경로를 찾았습니다!')
            print(f'목적지: {best_goal}')
            print(f'경로 길이: {len(best_path)}단계')
            print(f'경로: {" -> ".join([f"({x},{y})" for x, y in best_path])}')
            
            # CSV 파일로 저장
            print('\n경로를 CSV 파일로 저장하는 중...')
            save_path_to_csv(best_path, '/Users/dachae/IdeaProjects/zody/team/home_to_cafe.csv')
            print('home_to_cafe.csv 파일이 저장되었습니다.')
            
            # 지도 시각화
            print('\n지도를 시각화하는 중...')
            draw_map_with_path(df, best_path, structures, max_x, max_y)
            print('map_final.png 파일이 저장되었습니다.')
            
        else:
            print('경로를 찾을 수 없습니다. 건설현장으로 인해 막혀있을 수 있습니다.')
    
    except KeyboardInterrupt:
        print('\n사용자에 의해 프로그램이 중단되었습니다.')
    except Exception as e:
        print(f'오류가 발생했습니다: {e}')

if __name__ == '__main__':
    main()