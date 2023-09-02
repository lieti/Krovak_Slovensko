import math
import re

import pandas as pd


def normalize_feature_name(name):
    return re.sub(r"-|0*", "", name)


def find_matching_feature(input_name, available_features):
    normalized_input = normalize_feature_name(input_name)
    for feature in available_features:
        if normalized_input == normalize_feature_name(feature):
            return feature
    return None


def euclidean_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# Initialize an empty DataFrame to store point data
points_df = pd.DataFrame(columns=["Name", "X", "Y"])

# Load the CSV file into a DataFrame
file_path = r"c:\\____TRABAJO\\____Scripts\\Krovak_Slovensko\\Klady_ML\\ZM_10_vertices_coordinates.csv"
df = pd.read_csv(file_path)

# Get a list of unique feature names
unique_features = df["feature_name"].unique()

while True:
    user_input = input(
        "Enter the name of the map frame you want to plot (or 'exit' to quit): "
    ).strip()

    if user_input.lower() == "exit":
        # Ask for the CSV file name
        csv_file_name = input("Enter the name for the CSV file: ")

        # Export to CSV
        points_df.to_csv(f"{csv_file_name}.csv", index=False)
        break

    matching_feature = find_matching_feature(user_input, unique_features)

    if matching_feature:
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
                "hodnota smerom na vychod (vlavo) v mm?  "
            ).strip()
            if dist_mm_from_east_to_west_input.lower() == "skip":
                break
            dist_mm_from_east_to_west = float(dist_mm_from_east_to_west_input)
            dist_meters_from_east_to_west = dist_mm_from_east_to_west * 10

            if (
                dist_ne_nw < dist_meters_from_east_to_west
                or dist_meters_from_east_to_west < 0
            ):
                print("Warning: Invalid distance for east to west.")
            else:
                break

        while True:
            dist_mm_from_north_to_south_input = input(
                "hodnota smerom na juh (dole) v mm?  "
            ).strip()
            if dist_mm_from_north_to_south_input.lower() == "skip":
                break
            dist_mm_from_north_to_south = float(dist_mm_from_north_to_south_input)
            dist_meters_from_north_to_south = dist_mm_from_north_to_south * 10

            if (
                dist_ne_se < dist_meters_from_north_to_south
                or dist_meters_from_north_to_south < 0
            ):
                print("Warning: Invalid distance for north to south.")
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

        new_row = pd.DataFrame({"Name": [point_name], "X": [point_x], "Y": [point_y]})
        points_df = pd.concat([points_df, new_row]).reset_index(drop=True)

        print(
            f"Suradnice bod {point_name} v JTSK (5514) su: X = {point_x}, Y = {point_y}"
        )

    else:
        print("No matching feature found. Please try again.")
