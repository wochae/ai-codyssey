import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import seaborn as sns
from collections import deque
import heapq
import os

class MapVisualizer:
    def __init__(self, data_file='integrated_area_data.csv'):
        """
        지도 시각화 및 경로 탐색 클래스
        """
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
            print(f"✅ 데이터 로딩 완료: {len(self.df)}개 데이터 포인트")
            print(f"컬럼: {list(self.df.columns)}")
        except Exception as e:
            print(f"🚨 데이터 로딩 실패: {e}")
            
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
    
    def visualize_map(self, save_plots=True):
        """
        지도를 시각화하는 함수
        """
        print("\n🗺️ 지도 시각화 시작")
        print("="*50)
        
        construction_grid, area_grid, category_grid = self.create_grid_matrices()
        
        # 플롯 설정
        fig, axes = plt.subplots(2, 2, figsize=(16, 16))
        fig.suptitle('🏗️ 지역 데이터 시각화 대시보드', fontsize=20, fontweight='bold')
        
        # 1. 건설 현장 지도
        ax1 = axes[0, 0]
        construction_cmap = ListedColormap(['lightgreen', 'red'])
        im1 = ax1.imshow(construction_grid, cmap=construction_cmap, alpha=0.8)
        ax1.set_title('🏗️ 건설 현장 분포', fontsize=14, fontweight='bold')
        ax1.set_xlabel('X 좌표')
        ax1.set_ylabel('Y 좌표')
        
        # 격자 표시
        for i in range(self.grid_size + 1):
            ax1.axhline(i - 0.5, color='black', linewidth=0.5)
            ax1.axvline(i - 0.5, color='black', linewidth=0.5)
        
        # 범례 추가
        legend_elements = [patches.Patch(color='lightgreen', label='일반 지역'),
                          patches.Patch(color='red', label='건설 현장')]
        ax1.legend(handles=legend_elements, loc='upper right')
        
        # 2. 지역 분포
        ax2 = axes[0, 1]
        area_cmap = plt.cm.Set3
        im2 = ax2.imshow(area_grid, cmap=area_cmap, alpha=0.8)
        ax2.set_title('🏘️ 지역 분포', fontsize=14, fontweight='bold')
        ax2.set_xlabel('X 좌표')
        ax2.set_ylabel('Y 좌표')
        
        # 격자 표시
        for i in range(self.grid_size + 1):
            ax2.axhline(i - 0.5, color='black', linewidth=0.5)
            ax2.axvline(i - 0.5, color='black', linewidth=0.5)
        
        plt.colorbar(im2, ax=ax2, label='지역 ID')
        
        # 3. 구조물 카테고리
        ax3 = axes[1, 0]
        category_cmap = plt.cm.tab10
        im3 = ax3.imshow(category_grid, cmap=category_cmap, alpha=0.8)
        ax3.set_title('🏢 구조물 카테고리', fontsize=14, fontweight='bold')
        ax3.set_xlabel('X 좌표')
        ax3.set_ylabel('Y 좌표')
        
        # 격자 표시
        for i in range(self.grid_size + 1):
            ax3.axhline(i - 0.5, color='black', linewidth=0.5)
            ax3.axvline(i - 0.5, color='black', linewidth=0.5)
        
        plt.colorbar(im3, ax=ax3, label='카테고리 ID')
        
        # 4. 통합 정보 (건설현장 + 구조물)
        ax4 = axes[1, 1]
        
        # 배경: 지역별 색상
        im4_bg = ax4.imshow(area_grid, cmap='Pastel1', alpha=0.3)
        
        # 건설 현장 표시
        construction_y, construction_x = np.where(construction_grid == 1)
        ax4.scatter(construction_x, construction_y, c='red', s=100, marker='s', 
                   label='건설 현장', alpha=0.8)
        
        # 특별 구조물 표시 (category > 0)
        special_y, special_x = np.where(category_grid > 0)
        for i, (y, x) in enumerate(zip(special_y, special_x)):
            cat_id = category_grid[y, x]
            struct_name = self.get_struct_name(cat_id)
            ax4.scatter(x, y, c='blue', s=150, marker='*', alpha=0.8)
            ax4.annotate(f'{struct_name}', (x, y), xytext=(5, 5), 
                        textcoords='offset points', fontsize=8)
        
        ax4.set_title('🗺️ 통합 지도 (건설현장 + 구조물)', fontsize=14, fontweight='bold')
        ax4.set_xlabel('X 좌표')
        ax4.set_ylabel('Y 좌표')
        ax4.legend()
        
        # 격자 표시
        for i in range(self.grid_size + 1):
            ax4.axhline(i - 0.5, color='black', linewidth=0.5)
            ax4.axvline(i - 0.5, color='black', linewidth=0.5)
        
        plt.tight_layout()
        
        if save_plots:
            plt.savefig(os.path.join(os.path.dirname(__file__), 'map_visualization.png'), 
                       dpi=300, bbox_inches='tight')
            print("💾 지도 시각화 저장 완료: map_visualization.png")
        
        plt.show()
        
    def get_struct_name(self, category_id):
        """
        카테고리 ID에 해당하는 구조물 이름을 반환
        """
        struct_map = {
            1: 'Apt',
            2: 'Bldg', 
            3: 'Home',
            4: 'Cafe'
        }
        return struct_map.get(category_id, 'Unknown')
    
    def is_valid_position(self, x, y):
        """
        유효한 위치인지 확인 (격자 범위 내 + 건설현장 아님)
        """
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return False
        
        # 해당 위치의 건설현장 여부 확인
        row = self.df[(self.df['x'] == x + 1) & (self.df['y'] == y + 1)]
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
        # 좌표를 0-based로 변환
        start = (start[0] - 1, start[1] - 1)
        goal = (goal[0] - 1, goal[1] - 1)
        
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
                    path.append((current[0] + 1, current[1] + 1))  # 1-based로 변환
                    current = came_from[current]
                path.append((start[0] + 1, start[1] + 1))  # 시작점 추가
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
    
    def visualize_path(self, start, goal, path=None, save_plot=True):
        """
        경로를 시각화하는 함수
        """
        if path is None:
            path, message = self.a_star_pathfinding(start, goal)
            print(f"경로 탐색 결과: {message}")
            if path is None:
                return
        
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
            path_x = [p[0] - 1 for p in path]  # 0-based로 변환
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
        
        plt.title(f'🛣️ 경로 탐색 결과: ({start[0]}, {start[1]}) → ({goal[0]}, {goal[1]})', 
                 fontsize=16, fontweight='bold')
        plt.xlabel('X 좌표')
        plt.ylabel('Y 좌표')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 경로 정보 출력
        if path:
            plt.figtext(0.02, 0.02, f'경로 길이: {len(path)}단계\n총 거리: {len(path)-1:.1f}', 
                       fontsize=12, bbox=dict(boxstyle="round", facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_plot:
            plt.savefig(os.path.join(os.path.dirname(__file__), 'pathfinding_result.png'), 
                       dpi=300, bbox_inches='tight')
            print("💾 경로 탐색 결과 저장 완료: pathfinding_result.png")
        
        plt.show()
        
        return path
    
    def interactive_pathfinding(self):
        """
        대화형 경로 탐색 함수
        """
        print("\n🛣️ 대화형 경로 탐색")
        print("="*50)
        print("좌표 입력 형식: x,y (예: 1,1)")
        print("종료하려면 'quit' 입력")
        
        while True:
            try:
                start_input = input("\n시작점 좌표 (x,y): ").strip()
                if start_input.lower() == 'quit':
                    break
                
                goal_input = input("목표점 좌표 (x,y): ").strip()
                if goal_input.lower() == 'quit':
                    break
                
                # 좌표 파싱
                start_x, start_y = map(int, start_input.split(','))
                goal_x, goal_y = map(int, goal_input.split(','))
                
                start = (start_x, start_y)
                goal = (goal_x, goal_y)
                
                # 경로 탐색 및 시각화
                path = self.visualize_path(start, goal)
                
                if path:
                    print(f"\n✅ 경로 탐색 성공!")
                    print(f"경로: {' → '.join([f'({p[0]},{p[1]})' for p in path])}")
                    print(f"총 {len(path)-1}단계")
                else:
                    print("❌ 경로를 찾을 수 없습니다.")
                    
            except ValueError:
                print("❌ 잘못된 입력 형식입니다. x,y 형태로 입력해주세요.")
            except Exception as e:
                print(f"❌ 오류 발생: {e}")

def main():
    """
    메인 실행 함수
    """
    print("🗺️ 지도 시각화 및 경로 탐색 시스템")
    print("="*60)
    
    # MapVisualizer 인스턴스 생성
    visualizer = MapVisualizer()
    
    if visualizer.df is None:
        print("❌ 데이터를 불러올 수 없습니다. 프로그램을 종료합니다.")
        return
    
    # 1. 지도 시각화
    visualizer.visualize_map()
    
    # 2. 예시 경로 탐색
    print("\n🛣️ 예시 경로 탐색")
    print("="*50)
    
    # 예시 1: (1,1) → (15,15)
    print("예시 1: 좌상단에서 우하단으로")
    visualizer.visualize_path((1, 1), (15, 15))
    
    # 예시 2: 특별한 구조물 찾아가기
    # 아파트나 건물 위치 찾기
    special_structures = visualizer.df[visualizer.df['category'] > 0]
    if not special_structures.empty:
        target = special_structures.iloc[0]
        print(f"\n예시 2: 특별 구조물({target['struct']})로 이동")
        visualizer.visualize_path((1, 1), (int(target['x']), int(target['y'])))
    
    # 3. 대화형 경로 탐색
    choice = input("\n대화형 경로 탐색을 시작하시겠습니까? (y/n): ").strip().lower()
    if choice == 'y':
        visualizer.interactive_pathfinding()
    
    print("\n🎉 지도 시각화 및 경로 탐색 완료!")
    print("📁 생성된 파일:")
    print("  - map_visualization.png: 지도 시각화")
    print("  - pathfinding_result.png: 경로 탐색 결과")

if __name__ == "__main__":
    main()