# from LCU_driver_test.get_lobby_status import session
from abc import ABC, abstractmethod, abstractclassmethod
import asyncio
from typing import Optional
from packages.JSONsaver import JSONSaver
from packages.champNameIdMapper import ChampNameIdMapper

from termcolor import colored
# from menu import MenuApp

class Command(ABC):
    OK_S = f"[{colored(' OK  ', 'green')}]"
    ERR_S = f"[{colored('ERROR', 'red')}]"
    INFO_S = f"[{colored('INFO ', 'blue')}]"

    receiver = None
    actual_state = None

    def __init__(self):
        if Command.receiver:
            # self.receiver = receiver
            Command.connection = Command.receiver.connection
            Command._loop = Command.receiver.loop
            Command.locals = Command.connection.locals

        else:
            print(self.INFO_S, 'receiver is None type', sep=' ')

    def execute(self):
        return asyncio.run_coroutine_threadsafe(self._execute(), Command._loop)
        
    @abstractmethod
    async def _execute(self):
        pass

class MatchFinder(Command):

    async def _execute(self):

        res = await self.connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
        if res.status == 204:
            print(self.OK_S,
                    'Game searching has been started.')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)

class Canceller(Command):
    async def _execute(self):

        res = await self.connection.request('delete', '/lol-lobby/v2/lobby/matchmaking/search')
        if res.status == 204:
            print(self.OK_S,
                    'Gamer searching has been cancelled.')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)
    
class Acceptor(Command):
    async def _execute(self):

        reqs = '/lol-matchmaking/v1/ready-check/accept'
        res = await self.connection.request('post', reqs)

        if res.status == 200:
            print(self.OK_S,
                    'Game has been accepted.', sep=' ')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)

class Decliner(Command):
    async def _execute(self):

        reqs = '/lol-matchmaking/v1/ready-check/decline'
        res = await self.connection.request('post', reqs)

        if res.status == 200:
            print(self.OK_S,
                    'Game has been declined.', sep=' ')

        else:
            print(self.ERR_S, f'error: {res.status}')
            # _error_whit_connection(res)

class WS_JSONSaver(Command):
    def __init__(self, spinner, textinput):
        super().__init__()
        self.text, self.values = spinner.text, spinner.values
        self.filename = textinput.text
        self.saver = JSONSaver()


    async def _execute(self):

        if self.text == 'session':
            try:
                to_save = Command.locals['session'].data

            except KeyError:
                print(Command.ERR_S, 'session is empty')

            else:
                print(Command.OK_S,
                    f'the saving the {self.text}.',
                    f'Name of file: {self.filename}.',
                    sep=' ')
                    
                self.saver.save(what=to_save,
                                filename=self.filename,
                                type=self.text)


        elif self.text == 'lobby':
            try:
                to_save = Command.locals['lobby'].data

            except KeyError:
                print(Command.ERR_S, 'lobby is empty')

            else:
                name = self.saver.save(what=to_save, 
                                       filename=self.filename,
                                       type=self.text)

                print(Command.OK_S,
                    f'the saving the "{self.text}".',
                    f'Name of file: "{name}".',
                    sep=' ')
                  

        elif self.text == 'queue':
            try:
                to_save = Command.locals['queue'].data

            except KeyError:
                print(Command.ERR_S, 'queue is empty')

            else:
                name = self.saver.save(what=to_save, 
                                       filename=self.filename,
                                       type=self.text)

                print(Command.OK_S,
                    f'the saving the "{self.text}".',
                    f'Name of file: "{name}".',
                    sep=' ')

        elif self.text == 'search':
            try:
                to_save = Command.locals['search'].data

            except KeyError:
                print(Command.ERR_S, 'search is empty')

            else:
                name = self.saver.save(what=to_save, 
                                       filename=self.filename,
                                       type=self.text)

                print(Command.OK_S,
                    f'the saving the "{self.text}".',
                    f'Name of file: "{name}".',
                    sep=' ')

class AllyBansGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        my_team_bans = self.locals['session'].data['bans']['myTeamBans']
        bans = (champs[str(ban)] for ban in my_team_bans)
        
        try:
            print('Our team bans: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')
        
        # except Exception as e:
        #     print(e)
        #     print(e.with_traceback)

class EnemyBansGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        enemy_team_bans = self.locals['session'].data['bans']['theirTeamBans']
        bans = (champs[str(ban)] for ban in enemy_team_bans)
        
        try:
            print('enemy team bans: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')
        
        # except Exception as e:
        #     print(e)
        #     print(e.with_traceback)

class Hover(Command):
    def __init__(self, champion: str = None):
        super().__init__()
        try:
            self.champion = int(champion)

        except ValueError:
            champs = ChampNameIdMapper.get_champion_dict(order='normal')

            try:
                self.champion = champs[champion]

            except KeyError:
                print(Command.ERR_S,
                      'Invalid name of the champion.',
                      'Note, that this field is case-sensitive', sep=' ')

    async def _execute(self):
        champ_id = self.champion
        active_action = Command.locals['active_action']
        reqs = f'/lol-champ-select/v1/session/actions/{active_action["id"]}'

        res = await self.connection.request('patch', reqs,
                                            data={'championId': champ_id})

        if res.status in list(range(200, 209)):
            print(Command.OK_S,
                  'successfully changed hovered champ to:',
                    colored(self.champion, 'red'), sep=' ')

        else:
            print(Command.ERR_S,
                  'something went wrong while hovering the champion',
                    colored(self.champion, 'red'), sep=' ')

class HoverGetter(Command):
    async def _execute(self):
        action = self.locals['active_action']
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')

        if action['championId']:
            champ = champs[str(action['championId'])]
            print(f'Champion {colored(champ, "red")} is hovered.')
        
        else:
            print('A champion has not been selected yet.')

class MyTeamChampsGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        my_team_picks = self.locals['session'].data['myTeam']
        bans = (champs.get(str(ban['championId'])) for ban in my_team_picks)
        
        try:
            print('Our team picks: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')

class EnemyTeamChampsGetter(Command):
    async def _execute(self):
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        my_team_picks = self.locals['session'].data['theirTeam']
        bans = (champs.get(str(ban['championId'])) for ban in my_team_picks)
        
        try:
            print('enemy team picks: |', *[colored(f'{b}', 'cyan') + ' |' for b in bans])

        except KeyError as e:
            print(f'key error:\n{e}')

class MyPositionGetter(Command):
    async def _execute(self):

        # TODO: this shoudl be available globally
        reqs = '/lol-summoner/v1/current-summoner'
        res = await self.connection.request('get', reqs)

        data = await res.json()
        SUMMONER_ID = data['summonerId']

        for player in self.locals['session'].data['myTeam']:
            if player['summonerId'] == SUMMONER_ID:
                if player['assignedPosition']:
                    print(f"Your position: {player['assignedPosition']}")

                else:
                    print('In this mode positioning is disabled')

class Complete(Command):

    async def _execute(self):
        active_action = self.locals['active_action']
        champs = ChampNameIdMapper.get_champion_dict(order='reversed')
        action_type = active_action['type']
        champ_id = active_action['championId']

        # reqs = f'/lol-champ-select/v1/session/actions/{active_action["id"]}'
        # res = await connection.request('patch', reqs,
        #                                data={'isInProgress': False})

        reqs = f'/lol-champ-select/v1/session/actions/{active_action["id"]}/complete'
        res = await self.connection.request('post', reqs)

        if res.status in list(range(200, 209)):
            act = lambda: action_type + 'n' if action_type == 'ban'\
                                            else action_type
            print(Command.OK_S,
                    f'Champion has been {act()}ed.',
                    colored(champs[str(champ_id)], 'red'), sep=' ')

class EndpointSaver(Command):
    def __init__(self, reqs: str, filename: str):
        super().__init__()

        self.reqs: str = reqs
        self.filename: str = filename
        self.saver = JSONSaver()

    async def _execute(self):
        res = await self.connection.request('get', self.reqs)

        if res.status in list(range(200, 209)):
            print(Command.OK_S,
                    f'endpoint requested successfully', sep=' ')

            data = await res.json()
            name = self.saver.save(what=data,
                                   filename=self.filename,
                                   type='customEndpoint')
        
        else:
            print(Command.ERR_S,
                  f'error no.: {res.status}', sep=' ')

# Made for Launcher class:
class InitState(Command):
    async def _execute(self):
        Command.actual_state.initialized = True

class GameModeGetter(Command):
    '''Depreciated, TODO: change all occurences with replacement: LobbyGetter'''

    def __init__(self):
        super().__init__()
        self._return = None

    async def _execute(self):
        game_mode = None
        try:
            data = Command.locals['lobby']
        except KeyError:
            print(Command.INFO_S,
                  'lobby object not found in locals\n',
                  '       acquring new data...',
                  sep=' ')
            
            await self.update_locals()
            data = Command.locals['lobby']

        else:
            self._return = data['gameConfig']['gameMode']
        
    async def update_locals(self):
        reqs = '/lol-lobby/v2/lobby'
        res = await self.connection.request('get', reqs)
        data = await res.json()
        Command.locals.update({'lobby': data})

    def get_result(self):
        return self._return

class SearchGetter(Command):
    def __init__(self):
        super().__init__()
        self._return = None
        # self.arg = arg_ready_check

    async def _execute(self):
        is_found = False
        try:
            data = Command.locals['search'].data
        except KeyError:
            print(Command.INFO_S,
                  'search object not found in search\n',
                #   '       acquring new data...',
                  sep=' ')
            
            # await self.update_locals()
            # data = Command.locals['queue']

        else:
            self._return = data
            # if len(data) != 0:
            #     in_queue = data['isCurrentlyInQueue']
            #     is_found = data['searchState']

            #     if in_queue and is_found:
            #         self.arg.allowed_to_change_state = True
                # self._return = game_mode

    def get_return(self):
        return self._return

class LobbyGetter(Command):
    def __init__(self):
        super().__init__()
        self._return = None

    async def _execute(self):
        try:
            data = Command.locals['lobby']

        except KeyError:
            print(Command.INFO_S,
                  'lobby object not found in locals\n',
                  '       acquring new data...',
                  sep=' ')
            
            await self._update_locals()
            data = Command.locals['lobby']

        else:
            self._return = data
        
    async def _update_locals(self):
        reqs = '/lol-lobby/v2/lobby'
        res = await self.connection.request('get', reqs)
        data = await res.json()
        Command.locals.update({'lobby': data})

        self._return = data

    def get_result(self):
        return self._return

class SessionGetter(Command):
    def __init__(self):
        super().__init__()
        self._return = None

    async def _execute(self):
        try:
            data = Command.locals['session'].data

        except KeyError:
            print(Command.INFO_S,
                  'session object not found in session\n',
                #   '       acquring new data...',
                  sep=' ')

        else:
            self._return = data

    def get_return(self):
        return self._return

class QueueGetter(Command):
    def __init__(self):
        super().__init__()
        self._return = None

    async def _execute(self):
        try:
            data = Command.locals['queue'].data

        except KeyError:
            print(Command.INFO_S,
                  'queue object not found in queue\n',
                #   '       acquring new data...',
                  sep=' ')

        else:
            self._return = data

    def get_return(self):
        return self._return