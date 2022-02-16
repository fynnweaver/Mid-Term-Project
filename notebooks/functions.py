#---- Data Cleaning -----

#Grouping Data by NTA (Neighborhood Tabulation Area)
def bin_data(dataframe, metric = None, col_name = None, fill_na = 0):
    #create empty list for closest NTA centroids
    NTA_lat = []
    NTA_long = []
    
    #for every row
    for i in range(dataframe.shape[0]):
        #save lat, long
        df_lat, df_long = dataframe.latitude[i], dataframe.longitude[i]
    
        #create empty list to save difference b/w datapoint and NTA
        difference = []
        #for every NTA centroid, append total difference
        for lat, long in NTA.values:
            difference.append(abs(df_lat - lat) + abs(df_long - long))
        
        #save lat, long of closest NTA by getting the index of the minimum difference value
        NTA_lat.append(NTA.loc[difference.index(min(difference)), 'latitude'])
        NTA_long.append(NTA.loc[difference.index(min(difference)), 'longitude'])
        
    #save a new column to inputted dataframe with closest NTA centroid       
    dataframe['NTA_lat'] = close_NTA_lat
    dataframe['NTA_long'] = close_NTA_long
    
    #return data frame grouped depeding on input
    if metric == 'count':
        grouped = dataframe.value_counts(['NTA_lat', 'NTA_long']).rename_axis(['NTA_lat', 'NTA_long']).reset_index(name=col_name)
        grouped_df = pd.DataFrame(grouped)
    elif metric == 'sum':
        grouped = dataframe.groupby(['NTA_lat', 'NTA_long']).sum().drop(['latitude', 'longitude'], axis=1)
        grouped_df = pd.DataFrame(grouped).rename_axis(['NTA_lat', 'NTA_long']).reset_index()
    elif metric == 'mean':
        grouped = dataframe.groupby(['NTA_lat', 'NTA_long']).mean().drop(['latitude', 'longitude'], axis=1)
        grouped_df = pd.DataFrame(grouped).rename_axis(['NTA_lat', 'NTA_long']).reset_index()    
    #if no metric is specified just returned pre-grouped array 
    else:
        return dataframe
    
    #for each NTA value
    for lat, long in NTA.values:
        #check that it is not in the grouped dataframe
        if lat not in grouped_df['NTA_lat'].values and long not in grouped_df['NTA_long'].values:
            #if not then append a row with that NTA lat long
            df = {'NTA_lat': lat, 'NTA_long': long}
            grouped_df = grouped_df.append(df, ignore_index=True)
    
    
    #return df with NaN replaced by 0
    return  grouped_df.fillna(fill_na)
    
    
#Zipping lat and long for mapping + analysis
def lat_long_zip(df):
    import geopandas
    from shapely.geometry import Point
    
    geometry = [Point(xy) for xy in zip(df['NTA_long'], df['NTA_lat'])]
    geo_df = geopandas.GeoDataFrame(df, crs = {'init': 'epsg:2263'},
                                    geometry=geopandas.points_from_xy(df["NTA_long"], df["NTA_lat"]))
    geo_df.drop(['NTA_lat', 'NTA_long'], axis=1, inplace=True)
    return geo_df

#Applies lat_long_zip to inputted dataframe
def llz_set(df_list):
    new_df_list = []
    for element in df_list:
        new_df_list.append(lat_long_zip(element))
    return new_df_list
