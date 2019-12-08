import pandas as pd

#############
###Helpers###
#############

def format_mat(flavor_mat):
    flavor_frame = pd.DataFrame(flavor_mat)
    flavor_frame.columns = ['provider','machine-name', 'location', 'cores', 'memory', 'price']
    flavor_frame['price'] = pd.to_numeric(flavor_frame['price'])
    flavor_frame['cores'] = pd.to_numeric(flavor_frame['cores'])
    flavor_frame['memory'] = pd.to_numeric(flavor_frame['memory'])
    flavor_frame['core/price'] = flavor_frame['cores']/flavor_frame['price']
    flavor_frame['memory/price'] = flavor_frame['memory']/flavor_frame['price']
    return flavor_frame



