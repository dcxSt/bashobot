#!/opt/homebrew/Caskroom/miniforge/base/bin/python

import json
import praw
import requests
from datetime import date
import os
import random

ROOT = "/Users/steve/Documents/code/bashobot/"

def format_post(haiku , options=None):
    haiku = " // ".join(haiku.split("\n"))
    selftext = ""
    if options != None:
        if "author" in options.keys():
            selftext += f"{options['author']}\n"
        if "date" in options:
            selftext += f"{options['date']}\n"
        if "comment" in options:
            selftext += f"{options['comment']}\n"
    return haiku , selftext

def check_format_json(path_to_json):
    assert path_to_json[-5:] == ".json" , "the argument passed must be a path to a .json file"
    with open(path_to_json) as f:
        dic = json.load(f)
    assert type(dic["haikus"]) == type([]) , f"the json file {path_to_json} must contain a 'haiku' field"
    assert type(dic["posted_haikus"] == type([])) , f"the json file {path_to_json} must contain a 'posted_haiku' field"
    return

def find_valid_and_load(haiku_files):                   # arg is a list of haiku data paths
    for path_to_json in haiku_files:                    # for each path
        check_format_json(path_to_json)                 # make sure it's properly formatted
        with open(path_to_json) as f:
            haiku_dict = json.load(f)                   # load json file into haiku_dict
        if len(haiku_dict["haikus"]) != 0:              # if there are valid haiku in this dict
            return haiku_dict , path_to_json
    raise Exception("Help! There are no more valid haiku in the database!")


### Main script
if __name__=="__main__":
    ### Make sure no poems have been submitted today
    with open(ROOT + "date_last_posted.txt","r") as f:
        date_last_posted = f.read()                     # the date a haiku was last posted by this script 
        today_str = f"{date.today()}"                   # today's date formatted as a string
        assert today_str != date_last_posted , "This script was already used today"


    ### API credentials and object initialization
    credentials_path = ROOT + 'client_secrets.json'     # api credential file
    with open(credentials_path) as f:                   # open the credentials file
        creds = json.load(f)
    reddit = praw.Reddit(client_id=creds['client_id'],  # init a reddit api object
            client_secret=creds['client_secret'],
            user_agent=creds['user_agent'],
            redirect_uri=creds['redirect_uri'],
            refresh_token=creds['refresh_token'])
    reddit.validate_on_submit = True                    # apparently this is required... not sure what it does
    traditional_haiku = reddit.subreddit('Traditional_Haiku')   # init a subreddit object for Traditional_Haiku subreddit


    ### Randomly iterate through haiku data files until you find one that has haiku in it that haven't yet been posted by this script
    datadir = ROOT + "data/"
    haiku_files = [datadir + i for i in os.listdir(datadir) if i[-5:] == ".json"] 
    random.shuffle(haiku_files)                         # shuffle the list
    haiku_dict , path_to_json = find_valid_and_load(haiku_files) # load the source json haiku into a python dictionary

    opt_fields = list(haiku_dict.keys())                # these are the options that can be passed as metadata, e.g. author
    opt_fields.remove("posted_haikus")                  # remove the fields that are not the haiku (i.e. everything but the options fields)
    opt_fields.remove("haikus")                         # remove the fields that are not the haiku (i.e. everything but the options fields) 
    options = {}                                        # init options dict
    for field in opt_fields:                            
        options[field] = haiku_dict[field]              # assumes all other fields are all right
    

    ### load a random haiku and comment into the title and selftext fields respectively
    haikus = haiku_dict["haikus"]                       # a list
    idx = random.randrange(len(haikus))           # randomly choose a haiku (index) in this path
    haiku , selftext = format_post(haikus[idx] , options) # format it

    ### Post the haiku
    # print(f"Uncomment the next line to actually post;\ntitle={haiku}\nselftext={selftext}")
    # assert False                                        # forcefully end the program, for testing purposes
    traditional_haiku.submit(haiku, selftext=selftext)
    print(f"\n\nPosted\n{haikus[idx]}")

    ### Update last_posted.txt which contains the date of the last poem that was posted using this script
    with open(ROOT + "date_last_posted.txt","w") as f:
        f.write(f"{date.today()}")

    ### It is posted successfully, update json data 
    haiku_dict["posted_haikus"].append(haikus[idx])
    haiku_dict["haikus"] = haikus[:idx] + haikus[idx+1:]
    with open(path_to_json , "w") as f:
        json.dump(haiku_dict , f)
    

