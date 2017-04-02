from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state,
)
from my_planning_graph import PlanningGraph


class AirCargoProblem(Problem):
    def __init__(self, cargos, planes, airports, initial: FluentState,
                 goal: list):
        """

        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial
            state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

    def get_actions(self):
        '''
        This method creates concrete actions (no variables) for all actions in
        the problem domain action schema and turns them into complete Action
        objects as defined in the aimacode.planning module. It is
        computationally expensive to call this method directly; however, it is
        called in the constructor and the results cached in the `actions_list`
        property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        '''
        def load_actions():
            '''Create all concrete Load actions and return a list

            :return: list of Action objects
            '''
            loads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        load_action = create_load_action(c, p, a)
                        loads.append(load_action)
            return loads

        def unload_actions():
            '''Create all concrete Unload actions and return a list

            :return: list of Action objects
            '''
            unloads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        unload_action = create_unload_action(c, p, a)
                        unloads.append(unload_action)
            return unloads

        def fly_actions():
            '''Create all concrete Fly actions and return a list

            :return: list of Action objects
            '''
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = [expr("At({}, {})".format(p, fr)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, fr))]
                            strformat = "Fly({}, {}, {})".format(p, fr, to)
                            fly = Action(expr(strformat),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        """ Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        # TODO implement
        possible_actions = []
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for action in self.actions_list:
            is_possible = True
            for clause in action.precond_pos:
                if clause not in kb.clauses:
                    is_possible = False
                    break
            if not is_possible:
                continue
            for clause in action.precond_neg:
                if clause in kb.clauses:
                    is_possible = False
                    break
            if is_possible:
                possible_actions.append(action)
        return possible_actions

    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        # TODO implement
        new_state = FluentState([], [])
        old_state = decode_state(state, self.state_map)
        for fluent in old_state.pos:
            if fluent not in action.effect_rem:
                new_state.pos.append(fluent)
        for fluent in action.effect_add:
            if fluent not in new_state.pos:
                new_state.pos.append(fluent)
        for fluent in old_state.neg:
            if fluent not in action.effect_add:
                new_state.neg.append(fluent)
        for fluent in action.effect_rem:
            if fluent not in new_state.neg:
                new_state.neg.append(fluent)
        return encode_state(new_state, self.state_map)

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    def h_pg_levelsum(self, node: Node):
        '''
        This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        '''
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    def h_ignore_preconditions(self, node: Node):
        '''
        This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        '''
        # TODO implement (see Russell-Norvig Ed-3 10.2.3  or
        # Russell-Norvig Ed-2 11.2)
        count = 0
        return count


def air_cargo_p1() -> AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p2() -> AirCargoProblem:
    # TODO implement Problem 2 definition
    pass


def air_cargo_p3() -> AirCargoProblem:
    # TODO implement Problem 3 definition
    pass


def create_load_action(cargo, plane, airport):
    '''Returns a load action.'''
    preconditions = create_load_preconditions(cargo, plane, airport)
    effects = create_load_effects(cargo, plane, airport)
    load_expr = create_load(cargo, plane, airport)
    return Action(load_expr, preconditions, effects)


def create_load_preconditions(cargo, plane, airport):
    '''Returns a list of preconditions for a load action.'''
    precond_pos = [
        create_at(cargo, airport), create_at(plane, airport),
        create_cargo(cargo), create_plane(plane)
    ]
    return [precond_pos, []]


def create_load_effects(cargo, plane, airport):
    '''Returns a list of action effects for a load action.'''
    return [[create_in(cargo, airport)], [create_at(cargo, plane)]]


def create_load(cargo, plane, airport):
    '''Returns a Load expression for the given cargo, plane, and airport.'''
    return expr('Load({},{},{})'.format(cargo, plane, airport))


def create_unload_action(cargo, plane, airport):
    '''Returns an unload action.'''
    preconditions = create_unload_preconditions(cargo, plane, airport)
    effects = create_unload_effects(cargo, plane, airport)
    unload_expr = create_unload(cargo, plane, airport)
    return Action(unload_expr, preconditions, effects)


def create_unload_preconditions(cargo, plane, airport):
    '''Returns a list of preconditions for an unload action.'''
    precond_pos = [
        create_in(cargo, airport), create_at(plane, airport),
        create_cargo(cargo), create_plane(plane)
    ]
    return [precond_pos, []]


def create_unload_effects(cargo, plane, airport):
    '''Returns a list of action effects for an unload action.'''
    return [[create_at(cargo, airport)], [create_in(cargo, plane)]]


def create_unload(cargo, plane, airport):
    '''Returns a Load expression for the given cargo, plane, and airport.'''
    return expr('Unload({},{},{})'.format(cargo, plane, airport))



def create_at(thing, location):
    '''Returns an At expression for a given thing and a location.'''
    return expr('At({},{})'.format(thing, location))


def create_cargo(cargo):
    '''Returns a Cargo expression for a given cargo.'''
    return expr('Cargo({})'.format(cargo))


def create_plane(plane):
    '''Returns a Plane expression for a given plane.'''
    return expr('Plane({})'.format(plane))


def create_in(cargo, plane):
    '''Returns an In expression for a given cargo and plane.'''
    return expr('In({},{})'.format(cargo, plane))
