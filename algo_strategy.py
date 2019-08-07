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
        self.default_middel_desturctor = [[3, 10], [4, 10], [5, 10], [6, 10], [7, 10], [8, 10], [10, 10], [11, 10], [12, 10], [13, 10], [14, 10] \
                                          , [15, 10], [16, 10], [17, 10], [18, 10], [19, 10], [20, 10], [21, 10], [22, 10], [23, 10]]
        self.lower_flower = [[7,7], [8,7], [9,7], [10,7], [11,7], [12,7], [13,7], [14,7], [15,7], [16,7], [17,7], [18,7], [19,7], [20,7]]
        self.open_location_left = [[5, 9], [5, 10]]
        self.open_location_right = [[22,9], [22, 10]]
        self.attack_release_location_left = [5,8]
        self.attack_release_location_right = [22,8]

        self.open_which_side ='LEFT'
        
        self.corner_destructor_left = [[26,13], [25,12], [24,11], [25,13], [24,12], [23,11]]
        self.corner_destructor_right = [[1,13], [2,12], [3,11], [2,13], [3,12], [4,11]]
        
        self.space_is_open = False
        
        self.prev_left_corner_health = 0.0
        self.prev_right_corner_health = 0.0
        self.left_corner_location = [[0, 13], [1, 13], [1, 12], [2, 13], [2, 12], [2, 11]]
        self.right_corner_location = [[27, 13], [26, 13], [26, 12], [25, 13], [25, 12], [25, 11]]
        self.prev_attack_from_right = False
        self.prev_attack_from_left = False
        self.prev_add_corner = ''
        
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
        First prev turn analysis
        """
        self.prev_turn_analysis(game_state)
        
        """
        Second check defense:
        """
        self.check_default_destructor(game_state)
        self.check_default_flowers(game_state)
        self.add_lower_flowers(game_state, 4)
        
        if self.prev_attack_from_right:
            self.add_extra_corner_destructor(game_state, 2, 'RIGHT')
            self.prev_add_corner = 'RIGHT'
        elif self.prev_attack_from_left:
            self.add_extra_corner_destructor(game_state, 2, 'LEFT')
            self.prev_add_corner = 'LEFT'
            
        """
        Third try to open space and attack
        """
        if game_state.get_resource(game_state.BITS) > 15:
            self.attack(game_state)
        
        """
        Final try to refill edges
        """
    
    def check_default_destructor(self, game_state):
        for location in self.default_middel_desturctor:
            if not game_state.contains_stationary_unit(location):
                if game_state.can_spawn(DESTRUCTOR, location):
                    game_state.attempt_spawn(DESTRUCTOR, location)
                    
    def check_default_flowers(self, game_state):
        for location in self.init_flower:
            if not game_state.contains_stationary_unit(location):
                if game_state.can_spawn(ENCRYPTOR, location):
                    game_state.attempt_spawn(ENCRYPTOR, location)

    def add_lower_flowers(self, game_state, max_flower):
        cnt = 0
        for location in self.init_flower:
            if not game_state.contains_stationary_unit(location) and cnt < max_flower:
                if game_state.can_spawn(ENCRYPTOR, location):
                    game_state.attempt_spawn(ENCRYPTOR, location)
                    cnt += 1
            
    def add_extra_corner_destructor(self, game_state, max_destructor, side_str):
        n = game_state.number_affordable(DESTRUCTOR)
        cnt = 0
        i = 0
        location_list = self.corner_destructor_left
        if side_str == 'RIGHT':
            location_list = self.corner_destructor_right
            
        gamelib.debug_write('Turn[{}] add_extra_corner_destructor() - add {} DESTRUCTOR at {} corner. affordable {} DESTRUCTOR'.format(game_state.turn_number, max_destructor, side_str, n))
        while i < len(location_list) and cnt < max_destructor and n > 0:
            location = location_list[i]
            if not game_state.contains_stationary_unit(location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                cnt = cnt + 1
                n = n - 1
                gamelib.debug_write('Turn[{}] add_extra_corner_destructor() - Spawn at {}'.format(game_state.turn_number, str(location)))
            i = i + 1
        i = 0
        
    def attack(self, game_state):
        if self.space_is_open:
            self.open_space()
        
        location = self.attack_release_location_left
        if self.open_which_side == 'RIGHT':
            location = self.attack_release_location_right
        n = game_state.number_affordable(PING)
        if game_state.can_spawn(PING, location):
            game_state.attempt_spawn(PING, location, n)
            
    def open_space(self, game_state, side_str='RIGHT'):
        for location in self.open_location_right:
            if game_state.contains_stationary_unit(location):
                game_state.attempt_remove(location)
        self.space_is_open = True
        
    def prev_turn_analysis(self, game_state):
        #analysis corner attack
        gamelib.debug_write('Turn[{}] prev_turn_analysis(): prev_left_corner_health = {}'.format(game_state.turn_number, self.prev_left_corner_health))
        gamelib.debug_write('Turn[{}] prev_turn_analysis(): prev_right_corner_health = {}'.format(game_state.turn_number, self.prev_right_corner_health))
        
        current_left_health = self.calc_corner_health(game_state, 'LEFT')
        current_right_health = self.calc_corner_health(game_state, 'RIGHT')
        
        gamelib.debug_write('Turn[{}] prev_turn_analysis(): current_left_corner_health = {}'.format(game_state.turn_number, current_left_health))
        gamelib.debug_write('Turn[{}] prev_turn_analysis(): current_right_corner_health = {}'.format(game_state.turn_number, current_right_health))
        left_diff = current_left_health - self.prev_left_corner_health
        right_diff = current_right_health - self.prev_right_corner_health
        if left_diff < 0 and left_diff < right_diff: 
            self.prev_attack_from_left = True
        elif right_diff < 0 and right_diff < left_diff:
            self.prev_attack_from_right = True       
        
        self.prev_left_corner_health = current_left_health
        self.prev_right_corner_health = current_right_health        

    def calc_corner_health(self, game_state, side_str):
        health = 0
        location_list = self.left_corner_location
        if side_str == 'RIGHT':
            location_list = self.right_corner_location
        for l in location_list:
            if game_state.contains_stationary_unit(l):
                health = health + game_state.game_map[l[0], l[1]][0].stability
        return health
    
if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
