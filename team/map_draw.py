import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import ListedColormap
import seaborn as sns
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

class MapDrawer:
    def __init__(self, data_file='integrated_area_data.csv'):
        """
        지도 그리기 클래스
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
    
    def draw_map(self, save_as_png=True):
        """
        지도를 그리는 메인 함수
        """
        print("\n지역 지도 생성 중...")
        print("="*50)
        
        construction_grid, area_grid, category_grid = self.create_grid_matrices()
        
        # 지도 생성 - 창 크기 설정
        plt.figure(figsize=(10, 8))
        
        # 배경: 지역별 색상
        plt.imshow(area_grid, cmap='Pastel1', alpha=0.3)
        
        # 1단계: 먼저 일반 구조물들을 그리기 (건설 현장이 아닌 것들)
        for _, row in self.df.iterrows():
            x, y = int(row['x']) - 1, int(row['y']) - 1  # 0-based 인덱스로 변환
            cat_id = row['category']
            is_construction = row['ConstructionSite'] == 1
            
            # 건설 현장이 아닌 경우에만 구조물 표시
            if not is_construction and cat_id > 0:
                if cat_id == 1:  # 아파트 - 갈색 원형
                    plt.scatter(x, y, c='brown', s=150, marker='o', alpha=0.8, zorder=2)
                    plt.annotate('아파트', (x, y), xytext=(5, 5), 
                                textcoords='offset points', fontsize=9, zorder=3)
                elif cat_id == 2:  # 빌딩 - 갈색 원형
                    plt.scatter(x, y, c='brown', s=150, marker='o', alpha=0.8, zorder=2)
                    plt.annotate('빌딩', (x, y), xytext=(5, 5), 
                                textcoords='offset points', fontsize=9, zorder=3)
                elif cat_id == 3:  # 내 집 - 녹색 삼각형
                    plt.scatter(x, y, c='green', s=150, marker='^', alpha=0.8, zorder=2)
                    plt.annotate('내 집', (x, y), xytext=(5, 5), 
                                textcoords='offset points', fontsize=9, zorder=3)
                elif cat_id == 4:  # 반달곰 커피 - 녹색 사각형
                    plt.scatter(x, y, c='green', s=150, marker='s', alpha=0.8, zorder=2)
                    plt.annotate('반달곰커피', (x, y), xytext=(5, 5), 
                                textcoords='offset points', fontsize=9, zorder=3)
        
        # 2단계: 건설 현장을 나중에 그리기 (겹침 우선순위)
        construction_y, construction_x = np.where(construction_grid == 1)
        
        # 건설 현장을 회색 사각형으로 표시 (살짝 큰 크기로 겹침 허용)
        for cx, cy in zip(construction_x, construction_y):
            # 사각형 패치를 사용하여 정확한 위치에 그리기
            rect = patches.Rectangle((cx-0.4, cy-0.4), 0.8, 0.8, 
                                   linewidth=1, edgecolor='darkgray', 
                                   facecolor='gray', alpha=0.9, zorder=4)
            plt.gca().add_patch(rect)
        
        # 격자 표시
        for i in range(self.grid_size + 1):
            plt.axhline(i - 0.5, color='black', linewidth=0.5, zorder=1)
            plt.axvline(i - 0.5, color='black', linewidth=0.5, zorder=1)
        
        # 좌표 라벨 추가 (좌측 상단이 (1,1)이 되도록)
        plt.xticks(range(self.grid_size), range(1, self.grid_size + 1))
        plt.yticks(range(self.grid_size), range(1, self.grid_size + 1))
        
        # Y축을 뒤집어서 좌측 상단이 (1,1)이 되도록 설정
        plt.gca().invert_yaxis()
        
        plt.title('지역 지도 (15x15 격자)', fontsize=16, fontweight='bold')
        plt.xlabel('X 좌표')
        plt.ylabel('Y 좌표')
        
        # 범례 추가
        legend_elements = [
            patches.Rectangle((0, 0), 1, 1, facecolor='gray', edgecolor='darkgray', label='건설 현장'),
            plt.scatter([], [], c='brown', s=150, marker='o', label='아파트/빌딩'),
            plt.scatter([], [], c='green', s=150, marker='^', label='내 집'),
            plt.scatter([], [], c='green', s=150, marker='s', label='반달곰커피')
        ]
        plt.legend(handles=legend_elements, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 지도 정보 텍스트
        apartment_count = len(self.df[(self.df['category'] == 1) & (self.df['ConstructionSite'] == 0)])
        building_count = len(self.df[(self.df['category'] == 2) & (self.df['ConstructionSite'] == 0)])
        home_count = len(self.df[(self.df['category'] == 3) & (self.df['ConstructionSite'] == 0)])
        coffee_count = len(self.df[(self.df['category'] == 4) & (self.df['ConstructionSite'] == 0)])
        construction_count = len(construction_x)
        
        info_text = f"""지도 정보:
• 총 {self.grid_size}x{self.grid_size} = {self.grid_size**2}개 구역
• 건설 현장: {construction_count}개 (회색 사각형)
• 아파트: {apartment_count}개 (갈색 원형)
• 빌딩: {building_count}개 (갈색 원형)
• 내 집: {home_count}개 (녹색 삼각형)
• 반달곰커피: {coffee_count}개 (녹색 사각형)
• 좌표 범위: (1,1) ~ ({self.grid_size},{self.grid_size})
• 건설 현장과 구조물 겹침 시 건설 현장 우선"""
        
        plt.figtext(0.02, 0.02, info_text, fontsize=10, 
                   bbox=dict(boxstyle="round", facecolor='lightblue', alpha=0.8))
        
        plt.tight_layout()
        
        # PNG 파일로 저장
        if save_as_png:
            output_path = os.path.join(os.path.dirname(__file__), 'map.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            print(f"\n지도가 저장되었습니다: {output_path}")
        
        plt.show()
        
        return construction_count, apartment_count, building_count, home_count, coffee_count
    
    def print_summary(self):
        """
        지도 생성 결과 요약 출력
        """
        construction_count, apartment_count, building_count, home_count, coffee_count = self.draw_map()
        
        print("\n" + "="*50)
        print("지도 생성 완료 요약")
        print("="*50)
        print(f"건설 현장: {construction_count}개 위치")
        print(f"아파트: {apartment_count}개 위치")
        print(f"빌딩: {building_count}개 위치")
        print(f"내 집: {home_count}개 위치")
        print(f"반달곰커피: {coffee_count}개 위치")
        print(f"\n특징:")
        print(f"   - 좌측 상단이 (1,1), 우측 하단이 ({self.grid_size},{self.grid_size})")
        print(f"   - 건설 현장은 회색 사각형으로 표시 (겹침 허용)")
        print(f"   - 건설 현장과 구조물 겹침 시 건설 현장 우선")
        print(f"   - 결과 이미지: map.png로 저장")

def main():
    """
    메인 실행 함수
    """
    try:
        print("지역 지도 생성 시스템")
        print("="*60)
        
        # MapDrawer 인스턴스 생성
        drawer = MapDrawer()
        
        if drawer.df is None:
            print("데이터를 불러올 수 없습니다. 프로그램을 종료합니다.")
            return
        
        # 지도 생성 및 요약 출력
        drawer.print_summary()
        
        print("\n지도 생성이 완료되었습니다!")
        print("생성된 파일: map.png")
        
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
        print("안전하게 종료합니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
        print("프로그램을 종료합니다.")

if __name__ == "__main__":
    main()