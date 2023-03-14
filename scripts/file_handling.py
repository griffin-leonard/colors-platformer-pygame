# functions for handling json files
import json
import pickle

def load_json(name):
    ''' Load json and return datastructure '''
    with open(name+'.txt') as file:
        data = json.load(file)
        return data

def save_json(name, data):
    ''' Save data json. Returns nothing '''
    try:
        with open(name+'.txt','w') as file:
            json.dump(data,file)
    except Exception:
        print("ERROR: couldn't save json")

def load_pickle(name):
    ''' Load tilemap data for level from pickle '''
    data = []
    pickle_in = open(f'levels/level{name}_data', 'rb')
    data = pickle.load(pickle_in)
    return data
