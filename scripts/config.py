import os, json

CONFIG_PATH = 'data/config'

config = {}

for file in os.listdir(CONFIG_PATH):
    f = open(CONFIG_PATH + '/' + file, 'r')
    config[file.split('.')[0]] = json.load(f)
    f.close()