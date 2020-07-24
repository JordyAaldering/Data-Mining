#!/usr/bin/env python
# coding: utf-8

import json, pandas, pickle, requests

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
    
    return profile['personaname']


def GetGames(sid):
    url  = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={0}&steamid={1}'.format(key, sid)
    resp = requests.get(url)
    data = json.loads(resp.content)
    
    return [x['appid'] for x in data['response']['games']]


def GetAchievements(sid, appid):
    url  = 'http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={0}&key={1}&steamid={2}'.format(appid, key, sid)
    resp = requests.get(url)
    data = json.loads(resp.content)
    
    playerstats = data['playerstats']
    if 'achievements' in playerstats:
        return playerstats['achievements']
    return {}


def GetPercentage(sid, games):
    gotten, total = 0., 0.
    for appid in games:
        
        achievements = GetAchievements(sid, appid)
        gotten += sum([a['achieved'] for a in achievements])
        total += len(achievements)
    
    return gotten * 100 / total


if __name__ == '__main__':
    while True:
        try:
            sid = GetInput()
            personaname = GetPlayerSummary(sid)
            print('Profile found:', personaname)

            games = GetGames(sid)
            pct = GetPercentage(sid, games)
            print('Calculated percentage of completed achievements: {0:.2f}%'.format(pct))

        except InvalidInput:
            print('Input must be a 17 digit number.\n')
        except NoProfileFound:
            print('Profile was not found.\n')
        except ProfilePrivate:
            print('Profile is set to private.\n')
        except ZeroDivisionError:
            print('That profile cannot obtain any achievements.\n')
            break

        else:
            break
