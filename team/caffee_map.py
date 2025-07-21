import pandas as pd


map_df = pd.read_csv("dataFile/area_map.csv")
struct_df = pd.read_csv("dataFile/area_struct.csv")
cat_df = pd.read_csv("dataFile/area_category.csv")


cat_dict = cat_df.set_index("category")[" struct"].str.strip().to_dict()
struct_df["struct"] = struct_df["category"].map(cat_dict).fillna("None")


merged = pd.merge(map_df, struct_df, on=["x", "y"], how="left")
merged = merged.sort_values("area")

area1 = merged[merged["area"] == 1]
print("--- Area 1 데이터 ---")
print(area1)


print("\n--- 구조물 종류별 요약 통계 (Area 1) ---")
summary = area1["struct"].value_counts()
print(summary)


merged.to_csv("dataFile/merged_data.csv", index=False)
print("\n병합된 데이터가 merged_data.csv로 저장되었습니다.")
