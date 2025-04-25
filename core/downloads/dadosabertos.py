
import requests
from typing import List, Dict

BASE_URL = "http://dados.prefeitura.sp.gov.br"


def get_package_list(filter: str = None,
                     base_url: str = BASE_URL) -> List[str]:
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
        response = requests.get(url)
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


def package_show(package: str, base_url: str = BASE_URL) -> Dict:
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
        response = requests.get(url, params=params)
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
                      base_url: str = BASE_URL) -> List[Dict]:
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
        package_data = package_show(package, base_url)
        resources = package_data['resources']

        filtered_resources = []
        for resource in resources:
            name = resource.get('name', '')
            if filter is None or (name and filter.lower() in name.lower()):
                filtered_resources.append({
                    'name': name,
                    'url': resource.get('url', '')
                })

        return filtered_resources

    except Exception as e:
        raise Exception(f"Error fetching resources: {str(e)}")
