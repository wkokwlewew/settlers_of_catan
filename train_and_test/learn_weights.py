import copy
import pickle

from algorithms.first_choice_hill_climbing import *
from game.catan_state import CatanState
from players.expectimax_weighted_probabilities_player import AlphaBetaWeightedProbabilitiesPlayer
from train_and_test.logger import logger


class WeightsSpace(AbstractHillClimbableSpace):
    def __init__(self):
        self.time_seconds = 0.0005
        self._iterations_count = 0
        self._max_iterations = 10
        self._games_per_iteration = 5
        self._seeds = [i for i in range(1, self._games_per_iteration + 1)]
        self.unit = 0.4
        self._delta = 3

    def evaluate_state(self, weights) -> AbstractHillClimbingStateEvaluation:
        logger.info('| evaluating weights: {}'.format(weights))
        evaluation = 0

        for i in range(self._games_per_iteration):
            seed = self._seeds[i]
            p0 = AlphaBetaWeightedProbabilitiesPlayer(seed, self.time_seconds)
            p1 = AlphaBetaWeightedProbabilitiesPlayer(seed, self.time_seconds, weights)
            state = CatanState([p0, p1], seed)

            while not state.is_final():
                state.make_move(state.get_current_player().choose_move(state))
                state.make_random_move()

            scores = state.get_scores_by_player()
            logger.info('| done iteration {}. scores:{}'
                        .format(i, {'p0 (default weights)': scores[p0], 'p1 (new weights)': scores[p1]}))

            evaluation += scores[p1]
            evaluation -= scores[p0]

        self._iterations_count += 1

        return evaluation

    def get_neighbors(self, weights):
        next_weights = copy.deepcopy(weights)
        unit_fraction = self.unit / len(weights)
        for key in next_weights.keys():
            next_weights[key] -= unit_fraction

        for key in next_weights.keys():
            weight_modification = self.unit
            next_weights[key] += weight_modification
            yield next_weights
            next_weights[key] -= weight_modification

    def is_better(self, first_victories_count: int, second_victories_count: int) -> bool:
        logger.info('| is weight better: {}'.format(first_victories_count > second_victories_count + self._delta))
        return first_victories_count > second_victories_count + self._delta

    def enough_iterations(self) -> bool:
        return self._iterations_count >= self._max_iterations

if __name__ == '__main__':
    space = WeightsSpace()
    previous_result, result = None, None
    for _ in range(5):
        space.unit /= 2
        result = first_choice_hill_climbing(space, AlphaBetaWeightedProbabilitiesPlayer.default_weights)
        if result == previous_result:
            break
        previous_result = result
    logger.info('| learned weights: {}'.format(result))
    f = open('learned_weights', 'wb+')
    pickle.dump(result, f)
