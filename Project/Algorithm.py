#!/usr/bin/env python
# coding: utf-8

import json, requests, pandas, pickle

class InvalidInput(Exception):   pass
class NoProfileFound(Exception): pass
class ProfilePrivate(Exception): pass

key = 'EE44CC2E8EDE2A1288B72CA1D41D0462'


def GetInput():
    sid = input('Enter a SteamID64: ')
    if not sid.isdigit() or len(sid) != 17:
        raise InvalidInput
    
    return sid


def GetPlayerSummary(sid):
    url  = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={0}&steamids={1}'.format(key, sid)
    resp = requests.get(url)
    data = json.loads(resp.content)
    
    profiles = data['response']['players']
    if len(profiles) == 0:
        raise NoProfileFound
    
    profile = profiles[0]
    if profile['communityvisibilitystate'] == 1:
        raise ProfilePrivate
    
    return profile['personaname'], profile['lastlogoff']


def GetFriendList(sid):
    url  = 'http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={0}&steamid={1}'.format(key, sid)
    resp = requests.get(url)
    data = json.loads(resp.content)
    
    return data['friendslist']['friends']


def GetGames(sid):
    url  = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={0}&steamid={1}'.format(key, sid)
    resp = requests.get(url)
    data = json.loads(resp.content)
    
    return data['response']['game_count'], data['response']['games']


def Predict(records):
    df = pandas.DataFrame.from_records(records)
    with open('Data/tree.pkl', 'rb') as f:  
        dtr = pickle.load(f)
    
    return dtr.predict(df)


if __name__ == '__main__':
    while True:
        try:
            sid = GetInput()
            personaname, lastlogoff = GetPlayerSummary(sid)
            print('Profile found:', personaname)

            friend_count = len(GetFriendList(sid))
            game_count, games = GetGames(sid)
            playtime = sum([x['playtime_forever'] for x in games])

            records = [(len(personaname), lastlogoff, friend_count, game_count, playtime)]
            pred = Predict(records)
            print('Predicted percentage of completed achievements: {0:.2f}%'.format(pred[0]))

        except InvalidInput:
            print('Input must be a 17 digit number.\n')
        except NoProfileFound:
            print('Profile was not found.\n')
        except ProfilePrivate:
            print('Profile is set to private.\n')

        else:
            break
