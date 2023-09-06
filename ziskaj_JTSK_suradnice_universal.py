import math
import re

import pandas as pd


def normalize_feature_name(name):
    return re.sub(r"-|0*", "", name).upper()


def find_matching_feature(input_name, available_features):
    normalized_input = normalize_feature_name(input_name)
    for feature in available_features:
        if normalized_input == normalize_feature_name(feature):
            return feature
    return None


def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# Initialize an empty DataFrame to store point data
points_df = pd.DataFrame(
    columns=["Name", "X", "Y", "typ_mapy", "nomenklatura", "vlavo", "dole"]
)

# Load the CSV files into DataFrames
zm10_path = r"c:\\____TRABAJO\\____Scripts\\Krovak_Slovensko\\Klady_ML\\ZM10_vertices_coordinates.csv"
tm25_path = r"c:\\____TRABAJO\\____Scripts\\Krovak_Slovensko\\Klady_ML\\TM25_vertices_coordinates.csv"

zm10_df = pd.read_csv(zm10_path)
tm25_df = pd.read_csv(tm25_path)

# Merge the DataFrames
df = pd.concat([zm10_df, tm25_df]).reset_index(drop=True)

# Get a list of unique feature names
unique_features = df["feature_name"].unique()

while True:
    map_nomenclature = input(
        "Zadaj cislo (nomeklaturu) mapoveho listu (zadaj 'q' ak chces ukoncit): "
    ).strip()

    if map_nomenclature.lower() == "q":
        # Ask for the CSV file name
        csv_file_name = input("Zadaj meno CSV suboru na ulozenie vysledku: ")

        # Export to CSV
        points_df.to_csv(f"{csv_file_name}.csv", index=False)
        break

    if re.match(r"^\d{6}$", map_nomenclature.replace("-", "").replace("_", "")):
        target_map_type = "ZM10"
    elif re.match(
        r"^(m-?|-?)(\d{2})-?(\d{3})-?([a-zA-Z]{1}-?[a-zA-Z]{1}|[a-zA-Z]{2})$",
        map_nomenclature,
        re.IGNORECASE,
    ):
        # elif re.match(r"^m?-?\d{2}-?\d{3}-?[a-zA-Z]{2}$", map_nomenclature, re.IGNORECASE):
        target_map_type = "TM25"
    else:
        print("Neviem najst zodpovedajuci typ mapy, zadajte nomenklaturu znova.")
        continue

    scale_factor = int(re.search(r"\d+", target_map_type).group())

    matching_feature = find_matching_feature(map_nomenclature, unique_features)

    if matching_feature:
        print(f"Mapa {target_map_type} {matching_feature} najdena.")
        feature_data = df[df["feature_name"] == matching_feature]
        ne_x, ne_y = feature_data.loc[
            feature_data["feature_position"] == "NE", ["X", "Y"]
        ].values[0]
        nw_x, nw_y = feature_data.loc[
            feature_data["feature_position"] == "NW", ["X", "Y"]
        ].values[0]
        se_x, se_y = feature_data.loc[
            feature_data["feature_position"] == "SE", ["X", "Y"]
        ].values[0]

        dist_ne_nw = euclidean_distance(ne_x, ne_y, nw_x, nw_y)
        dist_ne_se = euclidean_distance(ne_x, ne_y, se_x, se_y)

        while True:
            dist_mm_from_east_to_west_input = input(
                "hodnota smerom na zapad (vlavo) v mm?  "
            ).strip()
            if dist_mm_from_east_to_west_input.lower() == "skip":
                break
            dist_mm_from_east_to_west = float(dist_mm_from_east_to_west_input)
            dist_meters_from_east_to_west = dist_mm_from_east_to_west * scale_factor

            if (
                dist_ne_nw < dist_meters_from_east_to_west
                or dist_meters_from_east_to_west < 0
            ):
                print(
                    "Zla hodnota vzdialenosti vychod -> zapad (ak chces preskocit cely bod napis 'skip')"
                )
            else:
                break

        while True:
            dist_mm_from_north_to_south_input = input(
                "hodnota smerom na juh (dole) v mm?  "
            ).strip()
            if dist_mm_from_north_to_south_input.lower() == "skip":
                break
            dist_mm_from_north_to_south = float(dist_mm_from_north_to_south_input)
            dist_meters_from_north_to_south = dist_mm_from_north_to_south * scale_factor

            if (
                dist_ne_se < dist_meters_from_north_to_south
                or dist_meters_from_north_to_south < 0
            ):
                print(
                    "Zla hodnota vzdialenosti sever -> juh (ak chces preskocit cely bod napis 'skip')"
                )
            else:
                break

        if (
            dist_mm_from_east_to_west_input.lower() == "skip"
            or dist_mm_from_north_to_south_input.lower() == "skip"
        ):
            continue

        dx = nw_x - ne_x
        dy = nw_y - ne_y
        ratio_ew = dist_meters_from_east_to_west / dist_ne_nw
        point_x = round(ne_x + dx * ratio_ew, 1)
        point_y = round(ne_y + dy * ratio_ew, 1)

        dx = se_x - ne_x
        dy = se_y - ne_y
        ratio_ns = dist_meters_from_north_to_south / dist_ne_se
        point_x = round(point_x + dx * ratio_ns, 1)
        point_y = round(point_y + dy * ratio_ns, 1)

        point_name = input("Enter the point name: ")

        new_row = pd.DataFrame(
            {
                "Name": [point_name],
                "X": [point_x],
                "Y": [point_y],
                "typ_mapy": [target_map_type],
                "nomenklatura": [matching_feature],
                "vlavo": [dist_mm_from_east_to_west],
                "dole": [dist_mm_from_north_to_south],
            }
        )
        points_df = pd.concat([points_df, new_row]).reset_index(drop=True)

        print(
            f"Bod {point_name}: X = {point_x}, Y = {point_y};  mapa {target_map_type} {matching_feature}, V->Z:{dist_mm_from_east_to_west}mm, S->J: {dist_mm_from_north_to_south}mm"
        )

    else:
        print("No matching feature found. Please try again.")
