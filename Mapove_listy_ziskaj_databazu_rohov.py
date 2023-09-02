# Importing necessary libraries for data manipulation
import geopandas as gpd
import pandas as pd


# Function to identify the corner based on coordinates
def identify_corner(coords, centroid):
    x, y = coords
    cx, cy = centroid
    if x > cx and y > cy:
        return "NE"
    elif x > cx and y < cy:
        return "SE"
    elif x < cx and y < cy:
        return "SW"
    elif x < cx and y > cy:
        return "NW"


# Load the GeoPackage file into a GeoDataFrame
file_path = r"c:\____TRABAJO\____Scripts\Krovak_Slovensko\Klady_ML\ZM_10.gpkg"  # Replace with the path to your GeoPackage file
gdf = gpd.read_file(file_path)

# Create an empty DataFrame to hold the results
columns = ["feature_name", "feature_position", "X", "Y"]
vertices_df = pd.DataFrame(columns=columns)

# Iterate through each feature in the GeoDataFrame
for index, row in gdf.iterrows():
    feature_name = row["LIST"]  # Assuming 'LIST' column contains the feature name
    polygon = row["geometry"].convex_hull  # Extract geometry and ensure it's convex

    # Get the centroid of the polygon
    centroid = polygon.centroid.x, polygon.centroid.y

    # Get the coordinates of the vertices
    if polygon.geom_type == "Polygon":
        exterior_coords = list(polygon.exterior.coords)
    elif polygon.geom_type == "MultiPolygon":
        # Take the first polygon if it's a MultiPolygon
        exterior_coords = list(polygon[0].exterior.coords)

    # For polygons with 4 vertices (excluding the closing vertex, which is the same as the first vertex)
    if len(exterior_coords) == 5:
        for coords in exterior_coords[
            :-1
        ]:  # Exclude the last point because it's the same as the first
            x, y = coords
            corner = identify_corner((x, y), centroid)
            vertices_df = vertices_df.append(
                {
                    "feature_name": feature_name,
                    "feature_position": corner,
                    "X": round(x, 2),
                    "Y": round(y, 2),
                },
                ignore_index=True,
            )

# Save the result to a CSV file
vertices_csv_path = r"c:\____TRABAJO\____Scripts\Krovak_Slovensko\Klady_ML\ZM_10.csv"  # Replace with the path where you want to save the CSV
vertices_df.to_csv(vertices_csv_path, index=False)
