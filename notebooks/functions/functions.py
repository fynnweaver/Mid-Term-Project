#---- API Calls ----

#Basic api call function
def API(root, search_term, param, header=None):
    """
    'search_term' must be a string of valid end point queries 
            - as specified by the relevent documentation
            
    OUTPUT: JSON of results
   """
 
    #define endpoint
    if search_term is not None:
        #if search_term is defined add it to the root to make the endpoint
        endpoint = root + search_term
    else:
        #otherwise endpoint is just the root
        endpoint = root
    
    #GET
    response = re.get(endpoint, params = param, headers=header)
   
    #return status code and results
    status_code, results = response.status_code, response.json()
    
    #Let's make sure it worked
    if status_code != 200:
        print('Something went wrong!')
        print(status_code)
        
    return results

#function to retrieve data from SODA datasets within inputted time frame
def range_SODA(root, column, time_range, params=None):
    #set endpoint
    range_endpoint = f"?$where=project_start_date between '{time_range[0]}' and '{time_range[1]}'"
    
    endpoint = root + range_endpoint
    
    results = API(endpoint, None, params)
    
    return results

#Convert JSON (or JSON like array) into a pandas DataFrame
def JSON_to_DF(JSON, desired_features):
    """
    `JSON` must be valid JSON result or JSON like array
    `desired_features` must be a list of keys from the JSON with the desired values
     
    OUTPUT: pandas DataFrame
    """ 
    columns = {}
    
    #for each desired column
    for feat in desired_features: 
        #empty value list
        values = []
        #for each project
        for element in JSON:
            #try to append value
            try:
                values.append(element[feat])
            #if error means no value append NaaN
            except:
                values.append('NaaN')
            
        columns[feat] = values

    #make dict into pandas dataframe        
    return pd.DataFrame(columns)                    


#---- Data Cleaning -----

#function to find centroid from list of coordinates
def centroid(vertexes):
    _x_list = [vertex [0] for vertex in vertexes]
    _y_list = [vertex [1] for vertex in vertexes]
    _len = len(vertexes)
    _x = sum(_x_list) / _len
    _y = sum(_y_list) / _len
    return(_x, _y)


#getting lat and long from point geometry
def coord_from_geom(dataframe):
    """
    Intakes a dataframe with point geometry in a column and converts to data frame with two columns:
        - 'latitude'
        - 'longitude'
    """
    
    latitude = []
    longitude = []

    for row in range(dataframe.shape[0]):
        #latitude
        latitude.append(dataframe.the_geom[row]['coordinates'][1])
        
        #longitude
        longitude.append(dataframe.the_geom[row]['coordinates'][0])

    dataframe['latitude'] = latitude
    dataframe['longitude'] = longitude
    
    dataframe = dataframe.drop('the_geom', axis = 1)
    
    return dataframe

#Grouping Data by NTA (Neighborhood Tabulation Area)
def bin_data(dataframe, metric = None, col_name = None, fill_na = 0):
    """
    `dataframe` must be valid pandas dataframe with columns 'latitude' and 'longitude'
        - If other columns are included they will be dropped if metric is `count`.
        - If metric is not `count` there must be a numeric feature associated with each coordinate
        
    `metric` when specified must be a string {'count', 'sum', 'mean'}. If metric is not specified function
    will return pre-grouped data where every point has an associated lat/long and NTA lat/long
    
    `col_name` can be specified to assign a column name to the count data column of the outputted dataframe
    
    `fill_na` must be an integer with which to replace values that had no data (NA). It defaults to 0
    
    REQUIRES: NTA csv to be loaded as object `NTA`
    OUTPUT: Pandas Dataframe with 195 rows, each row being an NTA
    """
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
        NTA_lat.append(NTA.loc[difference.index(min(difference)), 'NTA_lat'])
        NTA_long.append(NTA.loc[difference.index(min(difference)), 'NTA_long'])
        
    #save a new column to inputted dataframe with closest NTA centroid       
    dataframe['NTA_lat'] = NTA_lat
    dataframe['NTA_long'] = NTA_long
    
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

#plot clusters
def plot_clusters(X,y_res, plt_cluster_centers = False):
    X_centroids = []
    Y_centroids = []

    for cluster in set(y_res):
        x = X[y_res == cluster,0]
        y = X[y_res == cluster,1]
        X_centroids.append(np.mean(x))
        Y_centroids.append(np.mean(y))

        plt.scatter(x,
                    y,
                    s=50,
                    marker='s',
                    label=f'cluster {cluster}')

    if plt_cluster_centers:
        plt.scatter(X_centroids,
                    Y_centroids,
                    marker='*',
                    c='red',
                    s=250,
                    label='centroids')
    plt.legend()
    plt.grid()
    plt.show()