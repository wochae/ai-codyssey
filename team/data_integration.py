import pandas as pd
import os

def load_data():
    """
    CSV 파일들을 pandas 데이터프레임으로 불러오는 함수
    """
    try:
        # 현재 스크립트 위치 기준으로 dataFile 폴더 경로 설정
        data_dir = os.path.join(os.path.dirname(__file__), 'dataFile')
        
        # CSV 파일들을 pandas 데이터프레임으로 읽어오기
        df_category = pd.read_csv(os.path.join(data_dir, 'area_category.csv'))
        df_struct = pd.read_csv(os.path.join(data_dir, 'area_struct.csv'))
        df_map = pd.read_csv(os.path.join(data_dir, 'area_map.csv'))
        
        print("✅ 모든 파일을 성공적으로 불러왔습니다.")
        return df_category, df_struct, df_map
        
    except FileNotFoundError as e:
        print(f"🚨 파일 로딩 실패: {e}. 파일 경로를 확인해주세요.")
        return None, None, None
    except Exception as e:
        print(f"🚨 예상치 못한 오류: {e}")
        return None, None, None

def explore_data(df_category, df_struct, df_map):
    """
    각 데이터프레임의 구조와 내용을 탐색하는 함수
    """
    print("\n" + "="*50)
    print("📊 데이터 탐색 시작")
    print("="*50)
    
    # area_category.csv 탐색
    print("\n--- [area_category.csv] ---")
    print("데이터 형태:")
    print(df_category.head())
    print("\n데이터 정보:")
    print(df_category.info())
    print(f"행 수: {len(df_category)}, 열 수: {len(df_category.columns)}")
    
    # area_struct.csv 탐색
    print("\n--- [area_struct.csv] ---")
    print("데이터 형태:")
    print(df_struct.head())
    print("\n데이터 정보:")
    print(df_struct.info())
    print(f"행 수: {len(df_struct)}, 열 수: {len(df_struct.columns)}")
    
    # area_map.csv 탐색
    print("\n--- [area_map.csv] ---")
    print("데이터 형태:")
    print(df_map.head())
    print("\n데이터 정보:")
    print(df_map.info())
    print(f"행 수: {len(df_map)}, 열 수: {len(df_map.columns)}")
    
    # 각 데이터프레임의 컬럼명 확인
    print("\n--- 컬럼명 비교 ---")
    print(f"area_category 컬럼: {list(df_category.columns)}")
    print(f"area_struct 컬럼: {list(df_struct.columns)}")
    print(f"area_map 컬럼: {list(df_map.columns)}")

def analyze_relationships(df_category, df_struct, df_map):
    """
    데이터 간의 관계를 분석하는 함수
    """
    print("\n" + "="*50)
    print("🔍 데이터 관계 분석")
    print("="*50)
    
    # area_struct의 고유값 분석
    print("\n--- area_struct 분석 ---")
    if 'category' in df_struct.columns:
        print(f"category 고유값: {sorted(df_struct['category'].unique())}")
    if 'area' in df_struct.columns:
        print(f"area 고유값: {sorted(df_struct['area'].unique())}")
    
    # area_map의 ConstructionSite 분석
    print("\n--- area_map 분석 ---")
    if 'ConstructionSite' in df_map.columns:
        print(f"ConstructionSite 고유값: {sorted(df_map['ConstructionSite'].unique())}")
        construction_count = df_map['ConstructionSite'].value_counts()
        print(f"ConstructionSite 분포:\n{construction_count}")
    
    # area_category 분석
    print("\n--- area_category 분석 ---")
    print(f"카테고리 정보:\n{df_category}")

def integrate_data(df_category, df_struct, df_map):
    """
    데이터를 통합하는 함수
    """
    print("\n" + "="*50)
    print("🔗 데이터 통합 시작")
    print("="*50)
    
    try:
        # area_struct를 기준으로 시작
        merged_df = df_struct.copy()
        
        # area_map과 좌표 기준으로 병합 (x, y 좌표가 공통)
        if 'x' in df_struct.columns and 'y' in df_struct.columns and 'x' in df_map.columns and 'y' in df_map.columns:
            merged_df = pd.merge(merged_df, df_map, on=['x', 'y'], how='left')
            print("✅ area_struct와 area_map 병합 완료")
        
        # area_category와 category 기준으로 병합
        if 'category' in merged_df.columns and 'category' in df_category.columns:
            # 컬럼명 정리 (공백 제거)
            df_category_clean = df_category.copy()
            df_category_clean.columns = df_category_clean.columns.str.strip()
            
            merged_df = pd.merge(merged_df, df_category_clean, on='category', how='left')
            print("✅ category 정보 병합 완료")
        
        # 🔧 NaN 값 처리 및 데이터 정리
        print("\n🔧 데이터 품질 개선 시작")
        
        # 1. 'struct' 컬럼의 NaN 값을 '일반 지역'으로 채우기
        if 'struct' in merged_df.columns:
            nan_count_before = merged_df['struct'].isna().sum()
            merged_df['struct'].fillna('일반 지역', inplace=True)
            print(f"✅ NaN 값 처리 완료: {nan_count_before}개 → '일반 지역'으로 변경")
        
        # 2. 모든 컬럼명의 앞뒤 공백 제거
        merged_df.columns = merged_df.columns.str.strip()
        print("✅ 컬럼명 공백 제거 완료")
        
        # 3. 결측치 처리 후 결과 확인
        print("\n--- [결측치 처리 후 데이터 미리보기] ---")
        print(merged_df.head(10))
        
        print(f"\n최종 통합 데이터 형태: {merged_df.shape}")
        
        # 4. 수정 후 구조물 유형별 분포 확인
        if 'struct' in merged_df.columns:
            print("\n--- [수정 후 구조물 유형별 분포] ---")
            struct_distribution = merged_df['struct'].value_counts()
            for struct_type, count in struct_distribution.items():
                print(f"- {struct_type}: {count}개")
        
        # 통합 데이터 저장
        output_path = os.path.join(os.path.dirname(__file__), 'integrated_area_data.csv')
        merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\n💾 개선된 통합 데이터가 저장되었습니다: {output_path}")
        
        return merged_df
        
    except Exception as e:
        print(f"🚨 데이터 통합 중 오류 발생: {e}")
        return None

def generate_summary(merged_df):
    """
    통합된 데이터의 요약 정보를 생성하는 함수
    """
    if merged_df is None:
        return
        
    print("\n" + "="*50)
    print("📋 데이터 통합 요약")
    print("="*50)
    
    print(f"총 데이터 포인트: {len(merged_df)}개")
    print(f"총 컬럼 수: {len(merged_df.columns)}개")
    print(f"컬럼명: {list(merged_df.columns)}")
    
    # 결측치 확인
    print("\n--- 결측치 현황 ---")
    missing_data = merged_df.isnull().sum()
    if missing_data.sum() == 0:
        print("✅ 결측치 없음 - 모든 데이터가 완전합니다!")
    else:
        print("결측치가 있는 컬럼:")
        for col, count in missing_data.items():
            if count > 0:
                print(f"- {col}: {count}개")
    
    # 건설 현장 분포
    if 'ConstructionSite' in merged_df.columns:
        construction_summary = merged_df['ConstructionSite'].value_counts()
        print(f"\n건설 현장 분포:")
        print(f"- 건설 현장 (1): {construction_summary.get(1, 0)}개")
        print(f"- 일반 지역 (0): {construction_summary.get(0, 0)}개")
        
        # 건설 현장 비율
        construction_ratio = construction_summary.get(1, 0) / len(merged_df) * 100
        print(f"- 건설 현장 비율: {construction_ratio:.1f}%")
    
    # 지역별 분포
    if 'area' in merged_df.columns:
        area_summary = merged_df['area'].value_counts().sort_index()
        print(f"\n지역 분포:")
        for area_id, count in area_summary.items():
            percentage = count / len(merged_df) * 100
            print(f"- 지역 {area_id}: {count}개 ({percentage:.1f}%)")
    
    # 구조물 유형별 분포 (개선된 버전)
    if 'struct' in merged_df.columns:
        struct_summary = merged_df['struct'].value_counts()
        print(f"\n구조물 유형별 분포:")
        for struct_type, count in struct_summary.items():
            percentage = count / len(merged_df) * 100
            print(f"- {struct_type}: {count}개 ({percentage:.1f}%)")
    
    # 카테고리별 분포
    if 'category' in merged_df.columns:
        category_summary = merged_df['category'].value_counts().sort_index()
        print(f"\n카테고리별 분포:")
        for cat_id, count in category_summary.items():
            percentage = count / len(merged_df) * 100
            print(f"- 카테고리 {cat_id}: {count}개 ({percentage:.1f}%)")

def main():
    """
    메인 실행 함수
    """
    print("🚀 팀 프로젝트 - 지역 데이터 통합 분석 시작")
    print("="*60)
    
    # 1. 데이터 로드
    df_category, df_struct, df_map = load_data()
    
    if df_category is None or df_struct is None or df_map is None:
        print("❌ 데이터 로딩에 실패했습니다. 프로그램을 종료합니다.")
        return
    
    # 2. 데이터 탐색
    explore_data(df_category, df_struct, df_map)
    
    # 3. 데이터 관계 분석
    analyze_relationships(df_category, df_struct, df_map)
    
    # 4. 데이터 통합
    merged_df = integrate_data(df_category, df_struct, df_map)
    
    # 5. 요약 정보 생성
    generate_summary(merged_df)
    
    print("\n🎉 데이터 통합 분석이 완료되었습니다!")
    print("📁 결과 파일: integrated_area_data.csv")

if __name__ == "__main__":
    main()