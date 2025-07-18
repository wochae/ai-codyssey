import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import seaborn as sns
from collections import deque
import heapq
import os
import platform

# 한글 폰트 설정
def setup_korean_font():
    """
    한글 폰트 설정 함수
    """
    try:
        if platform.system() == 'Darwin':  # macOS
            plt.rcParams['font.family'] = 'AppleGothic'
        elif platform.system() == 'Windows':  # Windows
            plt.rcParams['font.family'] = 'Malgun Gothic'
        else:  # Linux
            plt.rcParams['font.family'] = 'DejaVu Sans'
        
        plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
        print("한글 폰트 설정 완료")
    except Exception as e:
        print(f"한글 폰트 설정 실패: {e}")
        print("영어로 표시됩니다.")

class MapVisualizer:
    def __init__(self, data_file='integrated_area_data.csv'):
        """
        지도 시각화 및 경로 탐색 클래스
        """
        setup_korean_font()  # 한글 폰트 설정
        
        self.data_file = data_file
        self.df = None
        self.grid_size = 15
        self.load_data()
        
    def load_data(self):
        """
        통합된 데이터를 불러오는 함수
        """
        try:
            file_path = os.path.join(os.path.dirname(__file__), self.data_file)
            self.df = pd.read_csv(file_path)
            print(f"데이터 로딩 완료: {len(self.df)}개 데이터 포인트")
            print(f"컬럼: {list(self.df.columns)}")
        except Exception as e:
            print(f"데이터 로딩 실패: {e}")
            
    def create_grid_matrices(self):
        """
        시각화를 위한 격자 행렬들을 생성하는 함수
        """
        # 각 속성별로 15x15 격자 생성
        construction_grid = np.zeros((self.grid_size, self.grid_size))
        area_grid = np.zeros((self.grid_size, self.grid_size))
        category_grid = np.zeros((self.grid_size, self.grid_size))
        
        for _, row in self.df.iterrows():
            x, y = int(row['x']) - 1, int(row['y']) - 1  # 0-based 인덱스로 변환
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                construction_grid[y, x] = row['ConstructionSite']
                area_grid[y, x] = row['area']
                category_grid[y, x] = row['category']
                
        return construction_grid, area_grid, category_grid
    
    def show_map_overview(self):
        """
        지도 개요를 보여주는 함수 (1개 윈도우만)
        """
        print("\n지도 개요 표시")
        print("="*50)
        
        construction_grid, area_grid, category_grid = self.create_grid_matrices()
        
        # 단일 윈도우로 통합 지도만 표시
        plt.figure(figsize=(12, 10))
        
        # 배경: 지역별 색상
        plt.imshow(area_grid, cmap='Pastel1', alpha=0.3)
        
        # 건설 현장 표시
        construction_y, construction_x = np.where(construction_grid == 1)
        plt.scatter(construction_x, construction_y, c='red', s=200, marker='s', 
                   label='건설 현장 (통행 불가)', alpha=0.8)
        
        # 특별 구조물 표시
        special_y, special_x = np.where(category_grid > 0)
        for y, x in zip(special_y, special_x):
            cat_id = category_grid[y, x]
            struct_name = self.get_struct_name(cat_id)
            plt.scatter(x, y, c='blue', s=150, marker='*', alpha=0.8)
            plt.annotate(f'{struct_name}', (x, y), xytext=(5, 5), 
                        textcoords='offset points', fontsize=10)
        
        # 격자 표시
        for i in range(self.grid_size + 1):
            plt.axhline(i - 0.5, color='black', linewidth=0.5)
            plt.axvline(i - 0.5, color='black', linewidth=0.5)
        
        # 좌표 라벨 추가
        plt.xticks(range(self.grid_size), range(1, self.grid_size + 1))
        plt.yticks(range(self.grid_size), range(1, self.grid_size + 1))
        
        plt.title('지역 지도 (15x15 격자)', fontsize=16, fontweight='bold')
        plt.xlabel('X 좌표')
        plt.ylabel('Y 좌표')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 지도 정보 텍스트
        info_text = f"""지도 정보:
• 총 {self.grid_size}x{self.grid_size} = {self.grid_size**2}개 구역
• 건설 현장: {len(construction_x)}개 (빨간 사각형)
• 특별 구조물: {len(special_x)}개 (파란 별)
• 좌표 범위: (1,1) ~ ({self.grid_size},{self.grid_size})"""
        
        plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                   bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
        
    def get_struct_name(self, category_id):
        """
        카테고리 ID에 해당하는 구조물 이름을 반환
        """
        struct_map = {
            1: '아파트',
            2: '빌딩', 
            3: '주택',
            4: '카페'
        }
        return struct_map.get(category_id, '알수없음')
    
    def is_valid_position(self, x, y):
        """
        유효한 위치인지 확인 (격자 범위 내 + 건설현장 아님)
        """
        if not (1 <= x <= self.grid_size and 1 <= y <= self.grid_size):
            return False
        
        # 해당 위치의 건설현장 여부 확인
        row = self.df[(self.df['x'] == x) & (self.df['y'] == y)]
        if not row.empty and row.iloc[0]['ConstructionSite'] == 1:
            return False
        
        return True
    
    def get_neighbors(self, x, y):
        """
        주변 8방향 이웃 좌표 반환 (대각선 포함)
        """
        directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        neighbors = []
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_valid_position(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def manhattan_distance(self, pos1, pos2):
        """
        맨하탄 거리 계산
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1, pos2):
        """
        유클리드 거리 계산
        """
        return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**0.5
    
    def a_star_pathfinding(self, start, goal):
        """
        A* 알고리즘을 사용한 경로 탐색
        """
        if not self.is_valid_position(start[0], start[1]):
            return None, "시작점이 유효하지 않습니다 (건설현장이거나 범위 밖)"
        
        if not self.is_valid_position(goal[0], goal[1]):
            return None, "목표점이 유효하지 않습니다 (건설현장이거나 범위 밖)"
        
        # A* 알고리즘 구현
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.euclidean_distance(start, goal)}
        
        while open_set:
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                # 경로 재구성
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path, "경로 탐색 성공"
            
            for neighbor in self.get_neighbors(current[0], current[1]):
                tentative_g_score = g_score[current] + self.euclidean_distance(current, neighbor)
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.euclidean_distance(neighbor, goal)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None, "경로를 찾을 수 없습니다"
    
    def visualize_path(self, start, goal, show_plot=True):
        """
        경로를 시각화하는 함수 (1개 윈도우만)
        """
        path, message = self.a_star_pathfinding(start, goal)
        print(f"\n경로 탐색 결과: {message}")
        
        if path is None:
            print("경로를 찾을 수 없습니다.")
            return None
        
        if not show_plot:
            return path
        
        construction_grid, area_grid, category_grid = self.create_grid_matrices()
        
        plt.figure(figsize=(12, 10))
        
        # 배경: 지역별 색상
        plt.imshow(area_grid, cmap='Pastel1', alpha=0.3)
        
        # 건설 현장 표시
        construction_y, construction_x = np.where(construction_grid == 1)
        plt.scatter(construction_x, construction_y, c='red', s=200, marker='s', 
                   label='건설 현장 (통행 불가)', alpha=0.8)
        
        # 특별 구조물 표시
        special_y, special_x = np.where(category_grid > 0)
        for y, x in zip(special_y, special_x):
            cat_id = category_grid[y, x]
            struct_name = self.get_struct_name(cat_id)
            plt.scatter(x, y, c='blue', s=150, marker='*', alpha=0.8)
            plt.annotate(f'{struct_name}', (x, y), xytext=(5, 5), 
                        textcoords='offset points', fontsize=10)
        
        # 경로 표시
        if len(path) > 1:
            path_x = [p[0] - 1 for p in path]  # 0-based로 변환 (시각화용)
            path_y = [p[1] - 1 for p in path]
            plt.plot(path_x, path_y, 'g-', linewidth=4, alpha=0.8, label='최적 경로')
            
            # 경로 상의 점들 표시
            plt.scatter(path_x[1:-1], path_y[1:-1], c='green', s=50, alpha=0.8)
        
        # 시작점과 목표점 표시
        plt.scatter(start[0] - 1, start[1] - 1, c='lime', s=300, marker='o', 
                   label=f'시작점 ({start[0]}, {start[1]})', edgecolors='black', linewidth=2)
        plt.scatter(goal[0] - 1, goal[1] - 1, c='orange', s=300, marker='o', 
                   label=f'목표점 ({goal[0]}, {goal[1]})', edgecolors='black', linewidth=2)
        
        # 격자 표시
        for i in range(self.grid_size + 1):
            plt.axhline(i - 0.5, color='black', linewidth=0.5)
            plt.axvline(i - 0.5, color='black', linewidth=0.5)
        
        # 좌표 라벨 추가
        plt.xticks(range(self.grid_size), range(1, self.grid_size + 1))
        plt.yticks(range(self.grid_size), range(1, self.grid_size + 1))
        
        plt.title(f'경로 탐색: ({start[0]}, {start[1]}) → ({goal[0]}, {goal[1]})', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('X 좌표')
        plt.ylabel('Y 좌표')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 경로 정보 출력
        if path:
            distance = len(path) - 1
            plt.figtext(0.02, 0.02, f'경로 길이: {len(path)}단계\n이동 거리: {distance}칸', 
                       fontsize=12, bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.show()
        
        return path
    
    def interactive_pathfinding(self):
        """
        대화형 경로 탐색 함수
        """
        print("\n대화형 경로 탐색")
        print("="*50)
        print("좌표 입력 방법:")
        print("  - 형식: x,y (예: 1,1 또는 15,15)")
        print("  - 범위: 1~15")
        print("  - 종료: 'quit' 또는 'q' 입력")
        print("  - 지도 보기: 'map' 입력")
        
        while True:
            try:
                print("\n" + "-"*30)
                start_input = input("시작점 좌표 (x,y): ").strip().lower()
                
                if start_input in ['quit', 'q']:
                    print("경로 탐색을 종료합니다.")
                    break
                
                if start_input == 'map':
                    self.show_map_overview()
                    continue
                
                goal_input = input("목표점 좌표 (x,y): ").strip().lower()
                
                if goal_input in ['quit', 'q']:
                    print("경로 탐색을 종료합니다.")
                    break
                
                if goal_input == 'map':
                    self.show_map_overview()
                    continue
                
                # 좌표 파싱
                start_x, start_y = map(int, start_input.split(','))
                goal_x, goal_y = map(int, goal_input.split(','))
                
                start = (start_x, start_y)
                goal = (goal_x, goal_y)
                
                # 좌표 유효성 검사
                if not (1 <= start_x <= 15 and 1 <= start_y <= 15):
                    print("시작점 좌표가 범위를 벗어났습니다. (1~15)")
                    continue
                
                if not (1 <= goal_x <= 15 and 1 <= goal_y <= 15):
                    print("목표점 좌표가 범위를 벗어났습니다. (1~15)")
                    continue
                
                # 경로 탐색 및 시각화
                print(f"\n경로 탐색 중: {start} → {goal}")
                path = self.visualize_path(start, goal)
                
                if path:
                    print(f"\n경로 탐색 성공!")
                    print(f"경로: {' → '.join([f'({p[0]},{p[1]})' for p in path])}")
                    print(f"총 {len(path)-1}단계 이동")
                else:
                    print("경로를 찾을 수 없습니다.")
                    
            except ValueError:
                print("잘못된 입력 형식입니다. 'x,y' 형태로 입력해주세요. (예: 1,1)")
            except Exception as e:
                print(f"오류 발생: {e}")

def main():
    """
    메인 실행 함수
    """
    print("지도 시각화 및 경로 탐색 시스템")
    print("="*60)
    
    # MapVisualizer 인스턴스 생성
    visualizer = MapVisualizer()
    
    if visualizer.df is None:
        print("데이터를 불러올 수 없습니다. 프로그램을 종료합니다.")
        return
    
    # 1. 지도 개요 표시
    print("\n먼저 지도를 확인해보세요!")
    visualizer.show_map_overview()
    
    # 2. 대화형 경로 탐색 시작
    print("\n이제 경로 탐색을 시작합니다!")
    visualizer.interactive_pathfinding()
    
    print("\n프로그램이 완료되었습니다!")
    print("감사합니다!")

if __name__ == "__main__":
    main()