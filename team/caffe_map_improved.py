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

def find_special_structures(merged_df):
    """
    특별 구조물들의 위치를 찾는 함수
    """
    print("\n6. 특별 구조물 위치 검색")
    print("-" * 30)
    
    # MyHome 찾기
    myhome_data = merged_df[merged_df['struct'].str.contains('MyHome', na=False)]
    if not myhome_data.empty:
        for _, row in myhome_data.iterrows():
            print(f"MyHome 위치: ({row['x']}, {row['y']}) - area {row['area']}")
    else:
        print("MyHome을 찾을 수 없습니다.")
    
    # 반달곰 커피 찾기
    coffee_data = merged_df[merged_df['struct'].str.contains('BandalgomCoffee', na=False)]
    if not coffee_data.empty:
        print(f"\n반달곰 커피 총 {len(coffee_data)}개 발견:")
        for _, row in coffee_data.iterrows():
            print(f"  - 위치: ({row['x']}, {row['y']}) - area {row['area']}")
    
    # 아파트 찾기
    apartment_data = merged_df[merged_df['struct'].str.contains('Apartment', na=False)]
    if not apartment_data.empty:
        print(f"\n아파트 총 {len(apartment_data)}개 발견:")
        for _, row in apartment_data.iterrows():
            print(f"  - 위치: ({row['x']}, {row['y']}) - area {row['area']}")
    
    # 빌딩 찾기
    building_data = merged_df[merged_df['struct'].str.contains('Building', na=False)]
    if not building_data.empty:
        print(f"\n빌딩 총 {len(building_data)}개 발견:")
        for _, row in building_data.iterrows():
            print(f"  - 위치: ({row['x']}, {row['y']}) - area {row['area']}")
    
    return myhome_data, coffee_data, apartment_data, building_data

def analyze_by_area(merged_df, target_area=None):
    """
    지역별 데이터 분석 함수 (개선된 버전)
    """
    print("\n7. 지역별 데이터 분석")
    print("-" * 30)
    
    if target_area is None:
        # 모든 지역 분석
        print("전체 지역 분석:")
        for area in sorted(merged_df['area'].unique()):
            area_df = merged_df[merged_df['area'] == area]
            print(f"\n=== Area {area} ===")
            print(f"총 격자 수: {len(area_df)}개")
            
            # 구조물별 개수
            struct_counts = area_df['struct'].value_counts()
            print("구조물 분포:")
            for struct, count in struct_counts.items():
                if struct != '일반 지역':
                    print(f"  - {struct}: {count}개")
            
            # 건설현장 개수
            construction_count = area_df['ConstructionSite'].sum()
            print(f"건설현장: {construction_count}개")
    else:
        # 특정 지역만 분석
        area_df = merged_df[merged_df['area'] == target_area]
        print(f"Area {target_area} 상세 분석:")
        print(f"데이터 크기: {area_df.shape}")
        
        # 구조물별 개수
        struct_counts = area_df['struct'].value_counts()
        print("\n구조물별 개수:")
        for struct, count in struct_counts.items():
            print(f"  - {struct}: {count}개")
        
        # 건설현장 통계
        construction_stats = area_df['ConstructionSite'].value_counts()
        print("\n건설현장 통계:")
        print(f"  - 건설현장: {construction_stats.get(1, 0)}개")
        print(f"  - 일반 지역: {construction_stats.get(0, 0)}개")
        
        # 특별 구조물 위치 정보
        special_structures = area_df[area_df['category'] > 0]
        if not special_structures.empty:
            print("\n특별 구조물 위치:")
            for _, row in special_structures.iterrows():
                print(f"  - {row['struct']}: ({row['x']}, {row['y']})")
        
        return area_df
    
    return merged_df

def generate_comprehensive_report(merged_df):
    """
    종합 분석 리포트 생성 함수
    """
    print("\n8. 종합 분석 리포트")
    print("=" * 50)
    
    # 전체 통계
    total_grids = len(merged_df)
    total_areas = merged_df['area'].nunique()
    total_construction = merged_df['ConstructionSite'].sum()
    
    print(f"\n전체 통계:")
    print(f"  - 총 격자 수: {total_grids}개")
    print(f"  - 총 지역 수: {total_areas}개")
    print(f"  - 총 건설현장: {total_construction}개")
    
    # 구조물별 전체 통계
    all_structures = merged_df['struct'].value_counts()
    print(f"\n전체 구조물 분포:")
    for struct, count in all_structures.items():
        print(f"  - {struct}: {count}개")
    
    # 지역별 요약
    print(f"\n지역별 요약:")
    for area in sorted(merged_df['area'].unique()):
        area_df = merged_df[merged_df['area'] == area]
        special_count = len(area_df[area_df['category'] > 0])
        construction_count = area_df['ConstructionSite'].sum()
        print(f"  - Area {area}: 격자 {len(area_df)}개, 특별구조물 {special_count}개, 건설현장 {construction_count}개")

def save_integrated_data(merged_df, filename='integrated_area_data.csv'):
    """
    통합된 데이터를 CSV 파일로 저장하는 함수 (전체 데이터)
    """
    try:
        output_path = os.path.join(os.path.dirname(__file__), filename)
        merged_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n통합 데이터가 저장되었습니다: {output_path}")
    except Exception as e:
        print(f"\n데이터 저장 실패: {e}")

def main():
    """
    메인 실행 함수 (개선된 버전)
    """
    try:
        print("데이터 수집 및 분석 시스템 (개선된 버전)")
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
        
        # 5. 특별 구조물 위치 검색
        find_special_structures(merged_df)
        
        # 6. 지역별 데이터 분석 (전체)
        analyze_by_area(merged_df)
        
        # 7. 종합 분석 리포트
        generate_comprehensive_report(merged_df)
        
        # 8. 통합 데이터 저장 (전체 데이터)
        save_integrated_data(merged_df)
        
        # 9. 사용자 선택 옵션
        print("\n" + "=" * 60)
        print("추가 분석 옵션:")
        print("특정 지역만 분석하려면 analyze_by_area(merged_df, target_area=숫자) 함수를 사용하세요.")
        print("예: analyze_by_area(merged_df, target_area=1)")
        
        return merged_df
        
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {e}")
        return None

if __name__ == "__main__":
    result = main()