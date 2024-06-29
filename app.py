import re

import geopandas as gpd
import pandas as pd
import requests
import streamlit as st


def create_geodataframe(data):
    features = []
    nested_result = data["results"]
    for key, value in nested_result.items():
        if key not in [
            "properties",
            "bbox",
            "footprint",
            "user",
            "projection",
            "meta_uri",
            "__v",
            "geojson",
        ]:
            nested_result["properties"][key] = value
    properties = nested_result["properties"]
    st.write("Copy TMS:")
    st.code(properties["tms"], language="python")
    geometry = nested_result["geojson"]
    features.append({"geometry": geometry, "properties": properties})

    gdf = gpd.GeoDataFrame.from_features(features)
    return gdf


st.title("OAM TMS Bounds Helper")


url_input = st.text_input(
    "Paste your OpenAerialMap URL:", placeholder="https://map.openaerialmap.org/..."
)

scrape_button = st.button("Fetch")
try:
    splited = url_input.split("/")[-1]
except Exception as ex:
    st.error(ex)
id_regex = r"([^?]+)"

if scrape_button:

    match = re.search(id_regex, splited)
    if match:
        oam_id = match.group()
        st.write(f"Image ID: {oam_id}")
        if oam_id:
            api_url = f"https://api.openaerialmap.org/meta/{oam_id}"
            with st.spinner(f"Fetching data from {api_url}..."):
                response = requests.get(api_url)
                if response.ok:
                    json_response = response.json()
                    gdf = create_geodataframe(json_response)
                    st.subheader("Result")
                    df = pd.DataFrame(gdf)
                    df.drop("geometry", axis=1, inplace=True)
                    st.write(df)
                    geojson_data = gdf.to_json()
                    st.download_button(
                        label="Download Bounds as GeoJSON",
                        data=geojson_data,
                        file_name=f"openaerialmap_data_{oam_id}.geojson",
                        mime="application/json",
                    )

                else:
                    st.error("OAM API is not responding")

    else:
        st.write("No OpenAerial Image ID found in the URL")
