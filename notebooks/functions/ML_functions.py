#To call this file: 
# '%run -i ~/Coding/custom_functions/lighthouse_labs/ML_functions.py'
# OR '%run -i [PATH]'

import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 

#Data Processing + Modeling (Supervised Learning)

def data_process(data, target, ord_map = False, split=0.2, scale = False, random_seed = 1):
    """Step 1 of the quick_model function. Can be used alone. Processes data for modeling.
    
    `data` must be pd.DataFrame including both features and target variables
    
    `target` can be:
    1. A string representing the column name of the target variable within `data`
    2. A data frame or array containing the target variable (in this case it must not be present in `data`)
    
    `ord_map` is relevent if any feature data is non-numeric (categorical). 
    For every categorical variable ord_map must have an entry in the list.
    \-> If categorical variable is ordinal the entry should be `1` or `True`. 
    \-> If the cat variable is not ordinal the entry should be `0` or `False`
    \-> Ignore ord_map if all variables are numerical
    
    `split` sets the train_test split percentage. Default is 0.2 or 20% into test data
    
    `scale` sets whether or not to scale the data using sklearn StandardScaler()

    `random_state` can be used to set random state for the train test split. It defaults to 1
    """
    
    #import needed packages 
    from sklearn.model_selection import train_test_split
    import category_encoders as ce
    from sklearn.preprocessing import StandardScaler
    
    if type(target) == str:
        #seperate target and features
        X = data.drop(target, axis=1)
        y = data[target]
    else:
        X = data
        y = target
    
    #save cat features columns
    cat_cols = X.dtypes[X.dtypes == 'object'].index
    
    #if ordinal is defined convert the categorical, ordinal data as defined by ord_map
    if bool(ord_map):
        #call encoder, fit and transform data to it
        encoder = ce.OrdinalEncoder(cols=cat_cols)
        data_enc = encoder.fit_transform(X[cat_cols])
        
        #iterate through index and T/F of ord_map input
        for i, truthy in enumerate(ord_map):
            #if element is T enact ordinal convert
            if truthy:
                X[cat_cols[i]] = data_enc[cat_cols[i]]
            #if element is F enact dummy convert and append to data frame
            else:
                print('false')
                X = X.join(pd.get_dummies(X[cat_cols[i]],columns= [cat_cols[i]], drop_first=True))
                #drop the original column with object dtype
                X = X.drop(cat_cols[i], axis=1)
    
    #if split is an object
    if bool(split):
        #train test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split, 
                                                        random_state=random_seed)
    #if split is false make test and train both the original data set
    else:
        X_train, X_test = X, X
        y_train, y_test = y, y
    
    #create dict of split data so they can be called properly
    data_split = {'X_train': X_train, 'X_test': X_test, 'y_train': y_train, 'y_test': y_test}
    
    if bool(scale):
        scaler = StandardScaler().fit(X_train)
        X_train = scaler.transform(X_train)
        X_test = scaler.transform(X_test)
    
    return data_split

def run_model(split_data, classifier, regression = False, param_grid=None):
    """Step 2 of the quick_model function. Puts data through single model.
    
    `split_data` should be the output from custom function `data_process()`
    
    `classifier` should be a sklearn supervised learning Classifier. It must be able to handle whatever split data represents
    \-> ex: Don't run regression problem through a classification model and vice versa
    \-> you must import Classifier() from relevent sklearn module before running the function
    
    `regression` is a boolean value corresponding to whether the models are targeting a regression
    or classification problem. Defaults to False so assumes classification and will return error if
    run with regression models.

    `param_grid` defines what parameter values to test within a GridSearch for the relevent model
    \-> Must be accurate to the possible parameters for the inputted sklearn Classifier 
    \-> If none are specified it will run with the parameters within the Classifier() entered as the classifier object"""
    
    from sklearn.model_selection import GridSearchCV
    from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, mean_squared_error, mean_absolute_error, r2_score
    
    #split data into objects again
    X_train, X_test, y_train, y_test = split_data.values()
    y_test = np.asarray(y_test)
    
    #if no param_grid is specified run whatever the inputted classifier is
    if param_grid is None:
        clf = classifier
        param_used = None
        #fit to train data
        clf.fit(X_train, y_train)
    #if it is specified call a classifier using grid search with param_grid
    else:
        clf_temp = classifier
        clf = GridSearchCV(clf_temp, param_grid)
        #fit to train
        clf.fit(X_train, y_train)
        #retrieve param used
        param_used = clf.fit(X_train, y_train).best_params_
  
    #predict on test data
    y_pred = clf.predict(X_test)

    #Regression evaluation metrics
    if bool(regression):
        MSE = mean_squared_error(y_test, y_pred)
        MAE = mean_absolute_error(y_test, y_pred)
        R2 = r2_score(y_test, y_pred)
        evaluation = {'MSE': MSE, 'MAE': MAE, 'R2': R2}
    #Classification evaluation metrics
    else:
        ac_score = accuracy_score(y_pred, y_test)
        CM = confusion_matrix(y_test, y_pred)
        report = classification_report(y_test, y_pred)
        evaluation = {'accuracy': ac_score, 'confusion_matrix': CM, 'report': report}
    
    #put into dict to return
    return evaluation, param_used
    
    
def model_quick(data, target, ord_map = None, split = 0.2, random_seed = 1,
                classifiers = None, regression = False, param_dicts = None):
    """Requires custom functions `data_process` and `run_model` to be loaded first
    
    `data` must be pd.DataFrame including both features and target variables
    
    `target` can be:
    1. A string representing the column name of the target variable within `data`
    2. A data frame or array containing the target variable 

    `ord_map` is relevent if any feature data is non-numeric (categorical). 
    For every categorical variable ord_map must have an entry in the list.
    \-> If categorical variable is ordinal the entry should be `1` or `True`. 
    \-> If the cat variable is not ordinal the entry should be `0` or `False`
    \-> Ignore ord_map if all variables are numerical
    
    `split` sets the train_test split percentage. Default is 0.2 or 20% into test data
    
    `random_state` can be used to set random state for the train test split. It defaults to 1

    `classifiers` should be a list of supervised learning Classifiers(). 
    They must be imported prior to running function and able to handle whatever problem data represents
    \-> i.e.: Don't run regression data through a classification models and vice versa
    
    `regression` is a boolean value corresponding to whether the models are targeting a regression
    or classification problem. Defaults to False so assumes classification and will return error if
    run with regression models.

    `param_dicts` should contain a list of dicts that each define what parameter values to test within a GridSearch
    The order of parameters to try within param_dicts MUST match the order of inputted classifiers
    \-> If none are specified it will run with the parameters within the Classifier() of each list element in classifiers
    
    OUTPUT: 3 dictionaries
    1 & 2. Two evaluation dictionaries: first using not scaled data & second using scaled data
        \-> nested within each scaled/not scaled dict there is a dict of the different inputted models
            \-> (use dict.keys() to view the model key names)
        \-> nested within the model dictionaries are the evaluation metrics (`accuracy`, `confusion_matrix`, `report`)
            \-> for classification: (`accuracy`, `confusion_matrix`, `report`)
            \-> for regression: (`MSE`, `MAE`, `R2`)
    3. A `param_used` dict: 
        \-> if `param_dicts` is defined, `param_used` will contain the optimal parameters found and used by GridSearchCV()
        \-> if `param_dicts` is not defined (defaults None), `param_used` will simply say 'Input'
    """
    
    #split data up
    split_data = data_process(data, target, ord_map, split, random_seed)
    split_scaled = data_process(data, target, ord_map, split, random_seed, True)
    
    #empty dict to save evaluation metrics for each model
    evaluations = {}
    evaluations_scale = {}
    
    #if classifiers are specified
    if classifiers is not None:
        param_used= {}
        #iterate through index and classifier within 
        for i, classifier in enumerate(classifiers):
            #create dict key for model using upper characters
            model_key = ''.join([x for x in str(classifier) if x.isupper()])[:4]
            #create a dict for parameters used within grid search
            #if param_dict is not none save evaluation from run_model function using relevent param
            if param_dicts is not None:
                evaluations[model_key], param_used[model_key] = run_model(split_data, classifier, regression, param_dicts[i]) 
                evaluations_scale[model_key], param_used[model_key]  = run_model(split_scaled, classifier, regression, param_dicts[i]) 
            #if is none (error) save evaluation from run model not using any param
            else:
                evaluations[model_key], param_used = run_model(split_data, classifier, regression)
                evaluations_scale[model_key], param_used = run_model(split_scaled, classifier, regression)
                #set param_used to simple string
                param_used = 'Input'
    else:
        #if no classsifiers are specified just return the processed data
        print('No models specified!')
        return split_data
    
    #return dict of evaluations
    return evaluations, evaluations_scale, param_used
    


#Clustering + Visualization (Unsupervised)

def radar_plot(data, cluster, 
               title = "Clustering", 
               save=False, 
               cluster_map=False):
    """
    Creates a radar plot from inputed data and clustering model output
    
    data should be DataFrame and cluster an np.array
    
    title can be specified to set plot title or it will default to 'Clustering'
    
    save can be specified as a string in which case the image is saved to the path
    of that inputted string. If no string is specified the image will not be saved.
    
    cluster_map specifies how many of the identified clusters to draw. 
    Must be integer > 0. Only useful to help visualize clusters with more clarity
    """

    #concatinate clustering and data
    data_cluster = pd.concat([data,pd.DataFrame(cluster)], axis=1)
    data_cluster = data_cluster.rename(columns= {0: 'cluster'})
    #group by cluster with means and save to new frame
    clustered = data_cluster.groupby('cluster').mean()
    #generate category labels
    categories = [*clustered.columns, clustered.columns[0]]

    #empty object for defining groups
    radar = []
    #define groups, last element must be first element to close radar group
    for i in range(len(clustered)):
        radar.append([*clustered.iloc[i], clustered.iloc[i, 0]])
    
    #label location for radar plot
    label_loc = np.linspace(start=0, stop=2 * np.pi, 
                            num=len(radar[0]))
    #color scheme
    colors = ['royalblue', 'darkorange', 'forestgreen', 'sienna', 'mediumpurple']  
    
    #initiate plot
    plt.figure(figsize=(8,8))
    plt.subplot(polar = True)
    
    #if cluster map is defined
    if bool(cluster_map):
        cluster_map = cluster_map
    else:
        cluster_map = len(radar)
    
    #loop through every cluster
    for i in range(0,cluster_map):
        #if there are outliers (ex with DBSCAN) id them
        if clustered.index[i] < 0:
            plt.plot(label_loc, radar[i], label=f"Outliers", color='red')
        #else plot as cluster
        else: 
            plt.plot(label_loc, radar[i], label=f"Cluster {i}", color=colors[i])
    
    lines, labels = plt.thetagrids(np.degrees(label_loc), labels=categories)

    plt.title(title)
    plt.legend()
    
    #if save path is defined save figure
    if bool(save):
        plt.savefig(save)
    #if not just show
    else:
        plt.show()
