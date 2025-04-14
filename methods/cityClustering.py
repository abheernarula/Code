import pandas as pd
from rapidfuzz import fuzz

def cluster_cities(df, col, threshold):
    
    city_list = df[col].unique()
    # print(city_list)
    # city_list = [str(i).lower() for i in city_list]
    # print(city_list)
    clusters = []      
    cluster_map = {}   
    for city in city_list:
        assigned = False
        for i, cluster in enumerate(clusters):
            # print("HERE")
            rep_city = cluster[0]
            score = fuzz.token_set_ratio(city, rep_city)
            # print(f"{city} + {rep_city} = {score}")
            if score >= threshold:
                cluster.append(city)
                cluster_map[city] = i + 1  
                assigned = True
                # print(cluster)
                break
        if not assigned:
            # print(f"HERE 2 - {city}")
            clusters.append([city])
            cluster_map[city] = len(clusters)
            # print(clusters)
            # print(cluster_map)
    # print(cluster_map)
    city_df = pd.DataFrame(df[col])
    city_df['Group'] = city_df[col].map(cluster_map)
    
    return city_df

