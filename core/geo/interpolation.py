from geopandas import GeoDataFrame


def areal_weighted_interpolation(
        left: GeoDataFrame,
        right: GeoDataFrame,
        right_id_col: str,
        original_var_name: str,
        final_var_name: str = None):
    """
    Perform areal weighted interpolation between two GeoDataFrames.
    This function calculates the weighted interpolation of a variable from one GeoDataFrame (`left`) 
    to another GeoDataFrame (`right`) based on the proportion of intersection areas. It is commonly 
    used in spatial analysis to transfer data between different spatial units.
    Parameters:
    -----------
    left : gpd.GeoDataFrame
    The source GeoDataFrame containing the original spatial data and variable to be interpolated.
    right : gpd.GeoDataFrame
    The target GeoDataFrame to which the interpolated variable will be transferred.
    right_id_col : str
    The column name in the `right` GeoDataFrame that uniquely identifies spatial units.
    original_var_name : str
    The column name in the `left` GeoDataFrame containing the variable to be interpolated.
    final_var_name : str, optional
    The column name for the interpolated variable in the resulting GeoDataFrame. 
    If not provided, the `original_var_name` will be used.
    Returns:
    --------
    final_gdf : gpd.GeoDataFrame
    A GeoDataFrame containing the `right` GeoDataFrame with the interpolated variable added.
    Notes:
    ------
    - The function assumes that both GeoDataFrames use the same coordinate reference system (CRS).
    - The intersection areas are calculated using the `gpd.overlay` method with `how='intersection'`.
    - The interpolated variable is calculated as the product of the original variable and the 
        proportion of intersection area relative to the total area of the `left` GeoDataFrame.
    Example:
    --------
    >>> interpolated_gdf = areal_weighted_interpolation(
        left=source_gdf,
        right=target_gdf,
        right_id_col='region_id',
        original_var_name='population',
        final_var_name='interpolated_population'
    >>> interpolated_gdf.head()
    """

    left = left.copy()
    right = right.copy()

    left['total_area'] = left.area

    inter = left.overlay(
        right,
        how='intersection',
        keep_geom_type=True)

    inter['intersection_area'] = inter.area

    inter['inter_prop'] = inter['intersection_area']/inter['total_area']

    if not final_var_name:
        final_var_name = original_var_name

    inter[final_var_name] = inter[original_var_name]*inter['inter_prop']

    right_interpolated = (
        inter
        .loc[:, [right_id_col, final_var_name]]
        .groupby(right_id_col)
        .sum()
        .round(0)
        .reset_index()
    )

    right_interpolated[final_var_name] = right_interpolated[final_var_name].astype(int)
    right_interpolated

    final_gdf = right.merge(
        right_interpolated,
        how='inner',
        on=right_id_col
    )
    
    return final_gdf