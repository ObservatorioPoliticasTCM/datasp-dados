import requests
import xml.etree.ElementTree as ET
import geopandas as gpd
from io import StringIO
from tqdm import tqdm
import pandas as pd

BASE_URL = 'https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/geoportal/wfs'
SERVICE = 'WFS'
WFS_VERSION = '1.1.0'
SERVER_MAXIMUM_FEATURES = 30000

def get_capabilities(filter: str = None):
    """
    Retrieve WFS capabilities and extract feature types.
    
    Args:
        filter (str, optional): Filter text to match feature names, titles, or abstracts.
    
    Returns:
        list[dict]: List of feature type dictionaries with keys 'name', 'title', and 'abstract'.
    """
    params = {
        'service': SERVICE,
        'version': WFS_VERSION, 
        'request': 'GetCapabilities'
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    
    root = ET.fromstring(response.content)
    namespaces = {
        'wfs': 'http://www.opengis.net/wfs',
        'ows': 'http://www.opengis.net/ows'
    }
    
    feature_types = []
    for ft in root.findall(".//wfs:FeatureType", namespaces):
        name_elem = ft.find("wfs:Name", namespaces)
        title_elem = ft.find("wfs:Title", namespaces)
        abstract_elem = ft.find("wfs:Abstract", namespaces)
        
        if name_elem is not None:
            name = name_elem.text if name_elem is not None else ''
            title = title_elem.text if title_elem is not None else ''
            abstract = abstract_elem.text if abstract_elem is not None else ''

            name = name if name is not None else ''
            title = title if title is not None else ''
            abstract = abstract if abstract is not None else ''
            
            if filter is None or (
                filter.lower() in name.lower() or
                filter.lower() in title.lower() or 
                filter.lower() in abstract.lower()
            ):
                feature_types.append({
                    'name': name,
                    'title': title,
                    'abstract': abstract
                })
    return feature_types

def get_feature_count(feature_type: str, sortBy: str = None):
    """
    Get the total feature count for the specified feature type with pagination.
    
    Args:
        feature_type (str): The feature type name.
        sortBy (str, optional): Column name to sort results.
    
    Returns:
        int: Total number of features.
    """
    total = 0
    offset = 0
    while True:
        params = {
            'service': SERVICE,
            'version': WFS_VERSION,
            'request': 'GetFeature',
            'typeName': feature_type,
            'resultType': 'hits',
            'startIndex': offset,
            'maxFeatures': SERVER_MAXIMUM_FEATURES
        }
        if sortBy:
            params.update({'sortBy': sortBy})
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        count = int(root.attrib.get('numberOfFeatures', 0))
        total += count
        if count < SERVER_MAXIMUM_FEATURES:
            break
        offset += SERVER_MAXIMUM_FEATURES
    return total

def get_feature_columns(feature_type: str):
    """
    Retrieve the list of column names for a given feature type using DescribeFeatureType.
    
    Args:
        feature_type (str): The feature type name.
    
    Returns:
        list[str]: List of column names.
    """
    params = {
        'service': SERVICE,
        'version': WFS_VERSION,
        'request': 'DescribeFeatureType',
        'typeName': feature_type
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    tree = ET.fromstring(response.content)
    ns = { "xsd": "http://www.w3.org/2001/XMLSchema" }
    columns = []
    for elem in tree.findall(".//xsd:element", ns):
        name = elem.attrib.get("name")
        if name:
            columns.append(name)
    return columns

def determine_sort_column(feature_type: str):
    """
    Determine the sorting column from the feature's schema.
    
    Checks for a column named 'cd_identificador_<feature>' first, then any column containing 'cd_identificador'.
    
    Args:
        feature_type (str): The feature type name.
    
    Returns:
        str or None: The column name to sort by, or None if no relevant column is found.
    """
    # Obtém a estrutura da feature diretamente do servidor
    columns = get_feature_columns(feature_type)
    feature_name = feature_type.split(":")[-1]
    best_candidate = f"cd_identificador_{feature_name}"
    if best_candidate in columns:
        return best_candidate
    for col in columns:
        if 'cd_identificador' in col:
            return col
    return None

def get_features(feature_type: str,
                 output_format: str = 'application/json',
                 wfs_max_features: int = 10000):
    """
    Retrieve features for the given feature type, either in a single request or in multiple paginated requests.
    
    Args:
        feature_type (str): The feature type name.
        output_format (str, optional): Desired output format, defaults to 'application/json'.
        wfs_max_features (int, optional): Maximum features per request when paginating.
    
    Returns:
        GeoDataFrame: A GeoPandas GeoDataFrame with the requested features.
    
    Raises:
        ValueError: If the output_format is unsupported.
    """
    sort_col = determine_sort_column(feature_type)
    total = get_feature_count(feature_type, sort_col)
    base_params = {
        'service': SERVICE,
        'version': WFS_VERSION,
        'request': 'GetFeature',
        'typeName': feature_type,
        'outputFormat': output_format
    }
    if sort_col:
        base_params.update({'sortBy': sort_col})

    if total <= wfs_max_features:
        params = base_params.copy()
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        if output_format == "application/json":
            return gpd.read_file(StringIO(response.text))
        else:
            raise ValueError(f"Unsupported output_format: {output_format}")
    else:
        gdf_list = []
        for start in tqdm(range(0, total, wfs_max_features), desc="Downloading features"):
            params = base_params.copy()
            params.update({
                'startIndex': start,
                'maxFeatures': wfs_max_features
            })
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            
            if output_format == "application/json":
                gdf_list.append(gpd.read_file(StringIO(response.text)))
            else:
                raise ValueError(f"Unsupported output_format: {output_format}")
        final_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True))
        final_gdf = final_gdf.set_geometry(gdf_list[0].geometry.name)
        final_gdf = final_gdf.set_crs(gdf_list[0].crs)
        return final_gdf
