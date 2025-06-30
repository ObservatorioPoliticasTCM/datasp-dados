from geopandas import GeoDataFrame


def prepare_tracts(df_tracts:GeoDataFrame,
                   df_vegetation:GeoDataFrame = None,
                   df_street_blocks:GeoDataFrame = None,
                   tracts_id_col:str = None) -> GeoDataFrame:
    """
    Prepare census tracts by processing spatial overlays with optional vegetation and street block geometries.
    Parameters:
        df_tracts (GeoDataFrame): A GeoDataFrame containing census tracts' geometries.
        df_vegetation (GeoDataFrame, optional): A GeoDataFrame containing vegetation geometries. When provided, the function subtracts these areas from the census tracts.
        df_street_blocks (GeoDataFrame, optional): A GeoDataFrame containing street block geometries. When provided, the function refines the tracts by intersecting with street blocks and dissolves the resulting geometries based on the tract identifier.
        tracts_id_col (str, optional): The column name used as the tract identifier for dissolving geometries after intersecting with street blocks. If not provided, the first column of df_tracts is used.
    Returns:
        GeoDataFrame: A new GeoDataFrame containing the adjusted tracts, including a new column 'adjusted_tract_area' that records the area of each geometry after processing.
    Notes:
        - The function performs a difference overlay with vegetation data (if available) followed by an intersection overlay with street blocks (if provided) and a subsequent dissolve operation.
        - The function assumes that the input GeoDataFrames use compatible coordinate reference systems for spatial operations.
    """

    if df_vegetation:
        ol1 = df_tracts.overlay(df_vegetation,
                        how='difference',
                        keep_geom_type=True)
    else:
        ol1 = df_tracts

    if df_street_blocks:
        if not tracts_id_col:
            tracts_id_col = df_tracts.columns[0]

        ol2 = (
            ol1.overlay(df_street_blocks[['geometry']],
                        how='intersection',
                        keep_geom_type=True)
                .dissolve(by=tracts_id_col, aggfunc='first')
                .reset_index()
        )
    else:
        ol2 = ol1

    ol2['adjusted_tract_area'] = ol2.area
    
    return ol2

def prepare_risk_area(risk_area_gdf:GeoDataFrame,
                 risk_area_id_col:str,
                 risk_grade_col_prefix:str,
                 active_risk_prefix:str,
                 subprefeitura_gdf:GeoDataFrame,
                 subprefeitura_id_col:str=None,
                 subprefeitura_additional_cols:list[str]=None) -> GeoDataFrame:
    """
    Prepares and overlays risk area data with subprefeitura data to generate a combined GeoDataFrame.
    This function filters the input risk area GeoDataFrame to retain only those areas whose risk grade
    column (identified by a prefix) starts with the specified active risk prefix (case-insensitive).
    It then performs a spatial overlay (intersection) with a subprefeitura GeoDataFrame to map each
    risk area to its corresponding subprefeitura region. Additionally, it generates a unique identifier
    for each resulting area by concatenating the risk area ID and subprefeitura ID.
    Parameters:
        risk_area_gdf (GeoDataFrame): GeoDataFrame containing risk area geometries and associated attributes.
        risk_area_id_col (str): Column name in risk_area_gdf to use as the risk area identifier.
                                    If not provided, the first column of risk_area_gdf is used.
        risk_grade_col_prefix (str): Prefix to identify the column in risk_area_gdf that contains risk grade data.
        active_risk_prefix (str): Prefix used to filter risk areas based on their risk grade value 
                                    (case-insensitive comparison).
        subprefeitura_gdf (GeoDataFrame): GeoDataFrame containing subprefeitura geometries and associated attributes.
        subprefeitura_id_col (str, optional): Column name in subprefeitura_gdf to use as the subprefeitura identifier.
                                                Defaults to the first column of subprefeitura_gdf if not specified.
        subprefeitura_additional_cols (list[str], optional): Additional columns from subprefeitura_gdf to include
                                                                in the overlay operation. The geometry column is
                                                                automatically included if not specified.
                                                                Defaults to None.
    Returns:
        GeoDataFrame: A GeoDataFrame resulting from the intersection of risk_area_gdf and subprefeitura_gdf,
                        which includes a new column 'id_area_subprefeitura' that uniquely identifies each area by
                        concatenating the risk area ID and the subprefeitura ID.
    Notes:
        - The function assumes that the risk grade column is uniquely identified by the provided prefix,
            and it selects the first matching column.
        - The overlay operation uses an "intersection" method with the parameter keep_geom_type set to True.
    """


    col_grau = [c for c in risk_area_gdf.columns if risk_grade_col_prefix in c][0]
    _gdf = risk_area_gdf.loc[risk_area_gdf[col_grau].str.lower().str.startswith(active_risk_prefix.lower())]

    if not subprefeitura_id_col:
        subprefeitura_id_col = subprefeitura_gdf.columns[0]

    if not subprefeitura_additional_cols:
        subprefeitura_additional_cols = []

    if subprefeitura_gdf.geometry.name not in subprefeitura_additional_cols:
        subprefeitura_additional_cols.append(subprefeitura_gdf.geometry.name)

    ol = _gdf.overlay(
        subprefeitura_gdf[[subprefeitura_id_col] + subprefeitura_additional_cols],
        how='intersection',
        keep_geom_type=True
    )

    if not risk_area_id_col:
        risk_area_id_col=risk_area_gdf.columns[0]


    ol.loc[:, 'id_area_subprefeitura'] = (
        ol.loc[:, risk_area_id_col].astype(str) +
        '.subpref.' +
        ol.loc[:, subprefeitura_id_col].astype(str)
    )

    cols = ['id_area_subprefeitura'] + [col for col in ol.columns if col != 'id_area_subprefeitura']
    ol = ol[cols]

    return ol