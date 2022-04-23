# Mid-Term Project: Clusturing NY Borroughs

Lighthouse Lab mid-term iterating with k-means clustering and visualizations to find the data-set that will most accurately replicate the 5 New York boroughs *without* the use of demographic or economic data.

Data was sourced from the NY Open Data Portal and the Yelp API. Full list of data links can be found in: `raw_data/datalinks.txt`. The raw data is either stored in the folder `raw_data` or accessed directly via API calling within Jupyter notebooks. 

All code work can be found in `notebooks`. `notebooks/deprecated` includes earlier versions of various data processing notebooks. `notebooks/functions` includes two `.py` files in which custom functions for this project have been stored and accessed.

`processed_data` contains the `master.csv` from which all clustering was run. It also contains binned but single feature datasets within category subfolders.

Finally, all saved visualizations can be found in `figures`. Final clustering result had an error rate of 8% and can be seen below:

![cluster_v6](https://github.com/fynnweaver/Mid-Term-Project/blob/main/figures/clustering/clustering_6.png)

