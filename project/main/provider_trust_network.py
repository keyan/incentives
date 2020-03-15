"""
A simple simulation demonstrating provider payoffs under the novel Provider Trust
Network Model.

To execute run:
    python3 provider_trust_network.py
"""
from enum import Enum
from typing import List, Tuple

CHI = 0.75

class VolumeAction(Enum):
    HIGH = 1
    LOW = 2


class QualityAction(Enum):
    HIGH = 1
    LOW = 2


volume_payoff = {VolumeAction.HIGH: 5, VolumeAction.LOW: 0}
quality_payoff = {QualityAction.HIGH: 2, QualityAction.LOW: 4}
cap_rate = {QualityAction.HIGH: 3, QualityAction.LOW: 1}
externalities = {QualityAction.HIGH: 1, QualityAction.LOW: -1}
bonus_rate = {VolumeAction.HIGH: 0, VolumeAction.LOW: 3}
trust_score_delta = {
    QualityAction.HIGH: 2,
    QualityAction.LOW: -2,
    VolumeAction.HIGH: -3,
    VolumeAction.LOW: 0,
}


class Provider:
    def __init__(
        self, name: str,
        # Tuple of which action to take for how many rounds.
        volume_actions: List[Tuple[VolumeAction, int]],
        # Tuple of which action to take for how many rounds.
        quality_actions: List[Tuple[QualityAction, int]],
    ):
        self.name = name
        self.volume_actions = volume_actions
        self.quality_actions = quality_actions
        # Assigned trust score for each round participated in.
        self.trust_by_round = []

    def update_volume_quality_actions(self):
        self.volume = self.set_volume()
        self.quality = self.set_quality()

    def set_volume(self):
        ret_val = self.volume_actions[0][0]
        if self.volume_actions[0][1] is not None:
            self.volume_actions[0] = (self.volume_actions[0][0], self.volume_actions[0][1] - 1)
            if self.volume_actions[0][1] < 1:
                del self.volume_actions[0]

        return ret_val

    def set_quality(self):
        ret_val = self.quality_actions[0][0]
        if self.quality_actions[0][1] is not None:
            self.quality_actions[0] = (self.quality_actions[0][0], self.quality_actions[0][1] - 1)
            if self.quality_actions[0][1] < 1:
                del self.quality_actions[0]

        return ret_val


class Simulation:
    def __init__(self, chi: float, providers: List[Provider], strategy_string: str):
        self.chi = chi
        self.providers = providers
        self.payoffs_by_round = []
        self.strategy_string = strategy_string

    def run(self, rounds: int, print_rounds: bool = False) -> None:
        if print_rounds:
            print(self.strategy_string)
        for k in range(1, rounds + 1):
            if print_rounds:
                print(f'Round {k}')

            self.payoffs_by_round.append([])
            for p in self.providers:
                p.update_volume_quality_actions()

                t = trust_score_delta[p.quality] + trust_score_delta[p.volume]
                if not p.trust_by_round:
                    p.trust_by_round.append(t)
                else:
                    p.trust_by_round.append(p.trust_by_round[-1] + t)

                payoff = get_payoff(p)
                self.payoffs_by_round[-1].append(payoff)
                if print_rounds:
                    print(f'{p.name}, payoff: {payoff}')


def trust_score(past_scores, k, chi) -> float:
    # Tmax is the highest value possible if a provider behaved perfectly every round.
    t_max = sum(
        trust_score_delta[QualityAction.HIGH] + trust_score_delta[VolumeAction.LOW]
        for _ in range(k)
    )
    assert t_max > 0

    unscaled = sum(past_scores[i]**((i + 1) / k) for i in range(k))

    return min(1, unscaled / (t_max * chi))


def get_payoff(provider: Provider) -> float:
    """
    Return the provider payoff for round k.
    """
    V = volume_payoff[provider.volume]
    C = cap_rate[provider.quality]
    E = externalities[provider.quality]
    Q = quality_payoff[provider.quality]
    B = bonus_rate[provider.volume]
    # Always assume payoff is computed for the latest round.
    T = provider.trust_by_round[-1]
    return min(V + C + B, (V + C + B) * T) + E + Q


def print_payoff_matrix(moves: List[str], top_left, top_right, bottom_right):
    print('                                      Other Provider (O)')
    print('                               -----------------------------------')
    print(f'                               | {moves[0]} | {moves[1]} |')
    print('              ----------------------------------------------------')
    print(f'Provider (P) | {moves[0]}  |    {top_left}  |    {top_right}     |')
    print('              ----------------------------------------------------')
    print(f'             | {moves[1]} |    {list(reversed(top_right))}    |    {bottom_right}       |')
    print('              ----------------------------------------------------')


if __name__ == '__main__':

    ###########################################################################
    print('Everyone plays V_low, 4 rounds, no changing strategies')
    rounds = 4

    s = Simulation(
        chi=CHI,
        providers=[
            Provider('P', [(VolumeAction.LOW, None)], [(QualityAction.LOW, None)]),
            Provider('OP', [(VolumeAction.LOW, None)], [(QualityAction.LOW, None)]),
        ],
        strategy_string='P (V_low, Q_low), OP (V_low, Q_low)',
    )

    s.run(rounds)
    top_left = s.payoffs_by_round[-1]

    s = Simulation(
        chi=CHI,
        providers=[
            Provider('P', [(VolumeAction.LOW, None)], [(QualityAction.LOW, None)]),
            Provider('OP', [(VolumeAction.LOW, None)], [(QualityAction.HIGH, None)]),
        ],
        strategy_string='P (V_low, Q_low), OP (V_low, Q_high)',
    )

    s.run(rounds)
    top_right = s.payoffs_by_round[-1]

    s = Simulation(
        chi=CHI,
        providers=[
            Provider('P', [(VolumeAction.LOW, None)], [(QualityAction.HIGH, None)]),
            Provider('OP', [(VolumeAction.LOW, None)], [(QualityAction.HIGH, None)]),
        ],
        strategy_string='P (V_low, Q_high), OP (V_low, Q_high)',
    )

    s.run(rounds)
    bottom_right = s.payoffs_by_round[-1]

    print_payoff_matrix(
        ['(V_low, Q_low)', '(V_low, Q_high)'],
        top_left, top_right, bottom_right,
    )

    ###########################################################################
    print('Everyone plays V_high, 4 rounds, no changing strategies')
    rounds = 4

    s = Simulation(
        chi=CHI,
        providers=[
            Provider('P', [(VolumeAction.HIGH, None)], [(QualityAction.LOW, None)]),
            Provider('OP', [(VolumeAction.HIGH, None)], [(QualityAction.LOW, None)]),
        ],
        strategy_string='P (V_high, Q_low), OP (V_high, Q_low)',
    )

    s.run(rounds)
    top_left = s.payoffs_by_round[-1]

    s = Simulation(
        chi=CHI,
        providers=[
            Provider('P', [(VolumeAction.HIGH, None)], [(QualityAction.LOW, None)]),
            Provider('OP', [(VolumeAction.HIGH, None)], [(QualityAction.HIGH, None)]),
        ],
        strategy_string='P (V_high, Q_low), OP (V_high, Q_high)',
    )

    s.run(rounds)
    top_right = s.payoffs_by_round[-1]

    s = Simulation(
        chi=CHI,
        providers=[
            Provider('P', [(VolumeAction.HIGH, None)], [(QualityAction.HIGH, None)]),
            Provider('OP', [(VolumeAction.HIGH, None)], [(QualityAction.HIGH, None)]),
        ],
        strategy_string='P (V_high, Q_high), OP (V_high, Q_high)',
    )

    s.run(rounds)
    bottom_right = s.payoffs_by_round[-1]

    print_payoff_matrix(
        ['(V_high, Q_low)', '(V_high, Q_high)'],
        top_left, top_right, bottom_right,
    )

    ###########################################################################
    print('Everyone plays V_low, 4 rounds, P tries to build trust then defect')
    rounds = 8

    s = Simulation(
        chi=CHI,
        providers=[
            Provider(
                'P',
                [(VolumeAction.LOW, 2), (VolumeAction.HIGH, None)],
                [(QualityAction.HIGH, None)],
            ),
            Provider('OP', [(VolumeAction.LOW, None)], [(QualityAction.LOW, None)]),
        ],
        strategy_string='P (V_low, Q_low), OP (V_low, Q_low)',
    )

    s.run(rounds)
    top_left = s.payoffs_by_round[-1]

    s = Simulation(
        chi=CHI,
        providers=[
            Provider('P', [(VolumeAction.LOW, None)], [(QualityAction.LOW, None)]),
            Provider('OP', [(VolumeAction.LOW, None)], [(QualityAction.HIGH, None)]),
        ],
        strategy_string='P (V_low, Q_low), OP (V_low, Q_high)',
    )

    s.run(rounds)
    top_right = s.payoffs_by_round[-1]

    s = Simulation(
        chi=CHI,
        providers=[
            Provider(
                'P',
                [(VolumeAction.LOW, 2), (VolumeAction.HIGH, None)],
                [(QualityAction.HIGH, None)],
            ),
            Provider('OP', [(VolumeAction.LOW, None)], [(QualityAction.HIGH, None)]),
        ],
        strategy_string='P (V_low, Q_high), OP (V_low, Q_high)',
    )

    s.run(rounds)
    bottom_right = s.payoffs_by_round[-1]

    print_payoff_matrix(
        ['(V_low, Q_low)', '(V_low, Q_high)'],
        top_left, top_right, bottom_right,
    )
