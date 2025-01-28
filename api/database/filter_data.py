import pandas as pd
import os


def filter_parts(output_path):
    directory_path = './gltf'
    parts_csv_path = 'parts/parts.csv'
    categories_csv_path = 'parts/part_categories.csv'

    # Filtrowanie kategorii
    used_categories = [
        "1", "3", "5", "9", "11", "14", "15", "16",
        "19", "20", "21", "23", "32", "37", "49", "67"
    ]

    categories_df = pd.read_csv(categories_csv_path)
    categories_map = categories_df.set_index('id')['name'].to_dict()

    parts_df = pd.read_csv(parts_csv_path)

    parts_df = parts_df[parts_df['part_cat_id'].astype(str).isin(used_categories)]
    parts_df['part_cat_id'] = parts_df['part_cat_id'].map(categories_map)

    # Filtrowanie względem dostępnych plików
    file_names_without_extension = [
        os.path.splitext(filename)[0] for filename in os.listdir(directory_path)
    ]

    filtered_parts_df = parts_df[parts_df['part_num'].isin(file_names_without_extension)]

    filtered_parts_df.to_csv(output_path, index=False)


filter_parts("new_parts.csv")
