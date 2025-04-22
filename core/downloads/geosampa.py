import requests
import xml.etree.ElementTree as ET
import geopandas as gpd
from io import StringIO

BASE_URL = 'https://wfs.geosampa.prefeitura.sp.gov.br/geoserver/geoportal/wfs'
SERVICE = 'WFS'
WFS_VERSION = '1.1.0'

def get_capabilities(filter: str = None):
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

def get_features(feature_type: str, output_format: str = "application/json"):
    params = {
        'service': SERVICE,
        'version': WFS_VERSION,
        'request': 'GetFeature',
        'typeName': feature_type,
        'outputFormat': output_format
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    
    if output_format == "application/json":
        # Convert the GeoJSON response into a GeoDataFrame
        return gpd.read_file(StringIO(response.text))
    else:
        raise ValueError(f"Unsupported output_format: {output_format}")
