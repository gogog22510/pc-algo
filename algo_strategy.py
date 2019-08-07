import gamelib
import random
import math
import warnings
from sys import maxsize

"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

Additional functions are made available by importing the AdvancedGameState 
class from gamelib/advanced.py as a replacement for the regular GameState class 
in game.py.

You can analyze action frames by modifying algocore.py.

The GameState.map object can be manually manipulated to create hypothetical 
board states. Though, we recommended making a copy of the map to preserve 
the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        random.seed()
        self.init_destructor = [[0, 13], [1, 12], [3, 11], [27, 13], [26, 12], [25, 11]]
        self.init_middle_destructor = [[6, 10], [9, 10], [12, 10], [15, 10], [18, 10], [21, 10], [24, 10]]
        self.init_flower = [[4,9],[5,9],[6,9],[7,9],[8,9],[9,9],[10,9],[11,9],[12,9],[13,9],[14,9],[15,9],[16,9],[17,9],[18,9],[19,9],[20,9],[23,9]]
        
        self.open_location_left = [[5, 9], [5, 10]]
        self.open_location_right = [[22,9], [22, 10]]
        
        # initialize stats
        self.unit_stats = {}

    def init_unit_stats(self, key, index):
        self.unit_stats[key] = self.config["unitInformation"][index]

    def on_game_start(self, config):
        """ 
        Read in config and perform any initial setup here 
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]

        gamelib.debug_write(self.config["unitInformation"][2])
        self.init_unit_stats(FILTER, 0)
        self.init_unit_stats(ENCRYPTOR, 1)
        self.init_unit_stats(DESTRUCTOR, 2)
        self.init_unit_stats(PING, 3)
        self.init_unit_stats(EMP, 4)
        self.init_unit_stats(SCRAMBLER, 5)

    def on_turn(self, turn_state):
        """
        This function is called every turn with the game state wrapper as
        an argument. The wrapper stores the state of the arena and has methods
        for querying its state, allocating your current resources as planned
        unit deployments, and transmitting your intended deployments to the
        game engine.
        """
        game_state = gamelib.GameState(self.config, turn_state)
        gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
        #game_state.suppress_warnings(True)  #Uncomment this line to suppress warnings.

        self.starter_strategy(game_state)

        game_state.submit_turn()

    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """
    def starter_strategy(self, game_state):
        """
        Build the C1 logo. Calling this method first prioritises
        resources to build and repair the logo before spending them 
        on anything else.
        """
        if game_state.turn_number == 0:
            self.build_first_round(game_state)
        else:
            self.start_pc_strategy(game_state)

    # Our first round move
    def build_first_round(self, game_state):
        """
        Set up first round
        """
        gamelib.debug_write('Turn[{}] build_first_round() - start'.format(game_state.turn_number))
        for location in self.init_destructor:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
        for location in self.init_middle_destructor:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
        for location in self.init_flower:
            uplocation = [location[0], location[1] + 1]
            if not game_state.contains_stationary_unit(uplocation) and not location in self.open_location_right:
                if game_state.can_spawn(ENCRYPTOR, location):
                    game_state.attempt_spawn(ENCRYPTOR, location)
        
    def start_pc_strategy(self, game_state):
        """
        First check bottom destructor:
        """

        
        """
        Second try to open space and attack
        """

        
        """
        Third try to refill edges
        """


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
