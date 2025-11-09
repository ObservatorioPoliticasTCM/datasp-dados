import requests
from typing import List, Dict
import pandas as pd
from requests.sessions import default_headers

BASE_URL = "http://dados.prefeitura.sp.gov.br"
    
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 Edg/142.0.0.0'
}


def get_package_list(filter: str = None,
                     base_url: str = BASE_URL,
                     headers: dict = DEFAULT_HEADERS) -> List[str]:
    """
    Fetches package list from dados.prefeitura.sp.gov.br API and returns as list

    Args:
        filter (str, optional): String to filter package names
        url (str): API endpoint URL

    Returns:
        List[str]: List containing the filtered package names
    """

    url = f'{base_url}/api/3/action/package_list'
    try:
        response = requests.get(url, headers=default_headers)
        response.raise_for_status()
        data = response.json()

        if data['success']:
            results = data['result']
            if filter:
                return [pkg
                        for pkg in results if filter.lower() in pkg.lower()]
            return results
        else:
            raise ValueError("API request unsuccessful")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data: {str(e)}")


def package_show(package: str, base_url: str = BASE_URL, headers: dict = DEFAULT_HEADERS) -> Dict:
    """
    Fetches package details from dados.prefeitura.sp.gov.br API

    Args:
        package (str): Package ID to fetch
        base_url (str): Base API URL

    Returns:
        Dict: Package details from API result
    """
    url = f'{base_url}/api/3/action/package_show'
    params = {'id': package}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data['success']:
            return data['result']
        else:
            raise ValueError("API request unsuccessful")

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching data: {str(e)}")


def package_resources(package: str,
                      filter: str = None,
                      base_url: str = BASE_URL,
                      headers: dict = DEFAULT_HEADERS) -> List[Dict]:
    """
    Fetches package resources from dados.prefeitura.sp.gov.br API

    Args:
        package (str): Package ID to fetch
        filter (str, optional): String to filter resource names
        base_url (str): Base API URL

    Returns:
        List[Dict]: List of filtered resources with name and url
    """
    try:
        package_data = package_show(package, base_url, headers)
        resources = package_data['resources']

        filtered_resources = []
        for resource in resources:
            name = resource.get('name', '')
            url = resource.get('url', '')
            filename = url.split('/')[-1] if url else ''
            
            if filter is None or (
                (name and filter.lower() in name.lower()) or 
                (filename and filter.lower() in filename.lower())
            ):
                filtered_resources.append({
                    'name': name,
                    'id': resource.get('id', ''),
                    'url': url
                })

        return filtered_resources

    except Exception as e:
        raise Exception(f"Error fetching resources: {str(e)}")

def load_resource(resource_id: str,
                  base_url: str = BASE_URL,
                  headers: dict = DEFAULT_HEADERS,
                  pandas_kwargs:dict={}) -> pd.DataFrame:
    """
    Loads a resource from dados.prefeitura.sp.gov.br API as a pandas DataFrame.
    
    Args:
        resource_id (str): Resource ID to fetch from the API
        base_url (str, optional): Base API URL. Defaults to BASE_URL.
        pandas_header (List[int], optional): List of row indices to use as column headers. 
            Defaults to [0].
    
    Returns:
        pd.DataFrame: Resource data loaded as a pandas DataFrame
        
    Raises:
        ValueError: If resource is PDF or unsupported format
        Exception: If API request fails or other errors occur
        
    Examples:
        >>> df = load_resource("abc123")  # Single header row
        >>> df = load_resource("xyz789", pandas_header=[0,1])  # Multi-index headers
    """
    url = f'{base_url}/api/3/action/resource_show'
    params = {'id': resource_id}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data['success']:
            result = data['result']
            resource_url = result['url']
            mimetype = result.get('mimetype', '').lower()
            format = result.get('format', '').lower()
            url_ext = resource_url.split('.')[-1].lower()
            
            if any(t in 'pdf' for t in [mimetype, format, url_ext]):
                raise ValueError("PDF resources are not supported")
                
            if any(t in 'csv' for t in [mimetype, format, url_ext]):
                csv_default_kwargs = {
                    'sep': ';',
                    'decimal': ',',
                    'thousands': '.',
                    'encoding': 'latin1'
                }
                csv_default_kwargs.update(pandas_kwargs)
                return pd.read_csv(resource_url, **csv_default_kwargs)
            elif any(t in ['xls', 'xlsx', 'excel', 'ods'] for t in [mimetype, format, url_ext]):
                excel_default_kwargs = {
                }
                excel_default_kwargs.update(pandas_kwargs)
                return pd.read_excel(resource_url, **excel_default_kwargs)
            else:
                raise ValueError(f"Unsupported file format: {mimetype or format or url_ext}")
                
        else:
            raise ValueError("API request unsuccessful")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching resource: {str(e)}")
