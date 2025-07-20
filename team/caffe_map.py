import pandas as pd
import os

def load_csv_files():
    """
    세 개의 CSV 파일을 불러오는 함수
    """
    try:
        # 파일 경로 설정
        data_dir = os.path.join(os.path.dirname(__file__), 'dataFile')
        
        # CSV 파일들 로드
        area_map = pd.read_csv(os.path.join(data_dir, 'area_map.csv'))
        area_struct = pd.read_csv(os.path.join(data_dir, 'area_struct.csv'))
        area_category = pd.read_csv(os.path.join(data_dir, 'area_category.csv'))
        
        print("데이터 파일 로딩 완료")
        print("=" * 50)
        
        return area_map, area_struct, area_category
    
    except Exception as e:
        print(f"파일 로딩 실패: {e}")
        return None, None, None

def analyze_data(area_map, area_struct, area_category):
    """
    데이터 내용을 출력하고 분석하는 함수
    """
    print("\n1. area_map.csv 분석")
    print("-" * 30)
    print(f"데이터 크기: {area_map.shape}")
    print(f"컬럼: {list(area_map.columns)}")
    print("\n첫 5행:")
    print(area_map.head())
    print(f"\n건설현장 개수: {area_map['ConstructionSite'].sum()}개")
    
    print("\n2. area_struct.csv 분석")
    print("-" * 30)
    print(f"데이터 크기: {area_struct.shape}")
    print(f"컬럼: {list(area_struct.columns)}")
    print("\n첫 5행:")
    print(area_struct.head())
    print(f"\n지역별 분포:")
    print(area_struct['area'].value_counts().sort_index())
    print(f"\n구조물 카테고리별 분포:")
    print(area_struct['category'].value_counts().sort_index())
    
    print("\n3. area_category.csv 분석")
    print("-" * 30)
    print(f"데이터 크기: {area_category.shape}")
    print(f"컬럼: {list(area_category.columns)}")
    print("\n전체 내용:")
    print(area_category)

def convert_category_to_name(area_struct, area_category):
    """
    구조물 ID를 area_category.csv 기준으로 이름으로 변환하는 함수
    """
    print("\n4. 구조물 ID를 이름으로 변환")
    print("-" * 30)
    
    # 카테고리 매핑 딕셔너리 생성
    category_map = dict(zip(area_category['category'], area_category[' struct']))
    category_map[0] = '일반 지역'  # 카테고리 0은 일반 지역
    
    print(f"카테고리 매핑: {category_map}")
    
    # 구조물 이름 컬럼 추가
    area_struct['struct'] = area_struct['category'].map(category_map)
    
    print("\n변환 결과 (첫 10행):")
    print(area_struct[['x', 'y', 'category', 'struct']].head(10))
    
    return area_struct

def merge_dataframes(area_map, area_struct):
    """
    세 데이터를 하나의 DataFrame으로 병합하는 함수
    """
    print("\n5. 데이터 병합")
    print("-" * 30)
    
    # x, y 좌표를 기준으로 병합
    merged_df = pd.merge(area_struct, area_map, on=['x', 'y'], how='inner')
    
    print(f"병합된 데이터 크기: {merged_df.shape}")
    print(f"컬럼: {list(merged_df.columns)}")
    
    # area 기준으로 정렬
    merged_df = merged_df.sort_values(['area', 'x', 'y']).reset_index(drop=True)
    
    print("\n병합 결과 (첫 10행):")
    print(merged_df.head(10))
    
    return merged_df

def filter_area_1(merged_df):
    """
    area 1에 대한 데이터만 필터링하는 함수
    """
    print("\n6. area 1 데이터 필터링")
    print("-" * 30)
    
    # 전체 지역별 반달곰 커피 분포 확인
    coffee_by_area = merged_df[merged_df['category'] == 4].groupby('area').size()
    print("지역별 반달곰 커피 분포:")
    print(coffee_by_area)
    
    # area 1만 필터링
    area_1_df = merged_df[merged_df['area'] == 1].copy()
    
    print(f"\narea 1 데이터 크기: {area_1_df.shape}")
    print(f"area 1의 반달곰 커피 개수: {len(area_1_df[area_1_df['category'] == 4])}개")
    
    print("\narea 1 데이터 (첫 15행):")
    print(area_1_df.head(15))
    
    return area_1_df

def generate_summary_report(area_1_df):
    """
    구조물 종류별 요약 통계를 리포트로 출력하는 함수 (보너스)
    """
    print("\n7. 구조물 종류별 요약 통계 리포트")
    print("=" * 50)
    
    # 구조물별 개수
    struct_counts = area_1_df['struct'].value_counts()
    print("\n구조물별 개수:")
    for struct, count in struct_counts.items():
        print(f"  - {struct}: {count}개")
    
    # 건설현장 통계
    construction_stats = area_1_df['ConstructionSite'].value_counts()
    print("\n건설현장 통계:")
    print(f"  - 건설현장: {construction_stats.get(1, 0)}개")
    print(f"  - 일반 지역: {construction_stats.get(0, 0)}개")
    
    # 특별 구조물 위치 정보
    special_structures = area_1_df[area_1_df['category'] > 0]
    if not special_structures.empty:
        print("\n특별 구조물 위치:")
        for _, row in special_structures.iterrows():
            print(f"  - {row['struct']}: ({row['x']}, {row['y']})")
    
    # 좌표 범위
    print("\n좌표 범위:")
    print(f"  - X: {area_1_df['x'].min()} ~ {area_1_df['x'].max()}")
    print(f"  - Y: {area_1_df['y'].min()} ~ {area_1_df['y'].max()}")
    
    # 총 격자 수
    total_grids = len(area_1_df)
    print(f"\n총 격자 수: {total_grids}개 (15x15 = 225개)")
    
    return struct_counts

def save_integrated_data(area_1_df):
    """
    통합된 데이터를 CSV 파일로 저장하는 함수
    """
    try:
        output_path = os.path.join(os.path.dirname(__file__), 'integrated_area_data.csv')
        area_1_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n통합 데이터가 저장되었습니다: {output_path}")
    except Exception as e:
        print(f"\n데이터 저장 실패: {e}")

def main():
    """
    메인 실행 함수
    """
    try:
        print("데이터 수집 및 분석 시스템")
        print("=" * 60)
        
        # 1. CSV 파일 로드
        area_map, area_struct, area_category = load_csv_files()
        
        if area_map is None or area_struct is None or area_category is None:
            print("데이터를 불러올 수 없습니다. 프로그램을 종료합니다.")
            return
        
        # 2. 데이터 분석
        analyze_data(area_map, area_struct, area_category)
        
        # 3. 구조물 ID를 이름으로 변환
        area_struct = convert_category_to_name(area_struct, area_category)
        
        # 4. 데이터 병합
        merged_df = merge_dataframes(area_map, area_struct)
        
        # 5. area 1 데이터 필터링
        area_1_df = filter_area_1(merged_df)
        
        # 6. 요약 통계 리포트 (보너스)
        generate_summary_report(area_1_df)
        
        # 7. 통합 데이터 저장
        save_integrated_data(area_1_df)
        
        print("\n데이터 분석이 완료되었습니다!")
        print("생성된 파일: integrated_area_data.csv")
        
    except KeyboardInterrupt:
        print("\n\n프로그램이 사용자에 의해 중단되었습니다.")
        print("안전하게 종료합니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")
        print("프로그램을 종료합니다.")

if __name__ == '__main__':
    main()