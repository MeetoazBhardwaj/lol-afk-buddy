from abc import ABC, abstractmethod
import asyncio

from lcu_driver import connector
from termcolor import colored
# from menu import MenuApp

class Command(ABC):
    OK_S = f"[{colored(' OK  ', 'green')}]"
    ERR_S = f"[{colored('ERROR', 'red')}]"
    INFO_S = f"[{colored('INFO ', 'blue')}]"

    def __init__(self, receiver=None, loop=None):
        if receiver:
            self.receiver = receiver
            self.connection = self.receiver.connection
            self.locals = self.connection.locals
            self._loop = loop

        else:
            print('receiver is None type')

    @abstractmethod
    def execute(self):
        pass


class MatchFinder(Command):
    def execute(self):
        # asyncio.run(self._execute())
        # print('im running')

        # TODO: jak z tego poziomu dostac loop?
        print(self.INFO_S,
              'current loop from Command:',
              self._loop, sep=' ')
        
        asyncio.run_coroutine_threadsafe(self._execute(), self._loop)
        # print(f'running loop: {asyncio.get_running_loop()}')

        # loop = asyncio.new_event_loop()
        # loop.run_until_complete(self._execute())
        # loop.close()

    async def _execute(self):
        # print(self.locals['lobby'])
        # print('\n\nmatch finder is working....\n\n')

        '''While in lobby start fingin a match.'''
        res = await self.connection.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
        if res.status == 200:
            print(colored('[OK]', 'green'),
                    'Game searching has been started.')

        else:
            print(f'error {res.status}')
            # _error_whit_connection(res)


class Canceller(Command):
    def execute(self):
        print('\n\ncancell is working....\n\n')