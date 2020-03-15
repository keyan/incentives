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
    VolumeAction.HIGH: -2,
    VolumeAction.LOW: 0,
}


class Provider:
    def __init__(
        self, name: str, volume_action: VolumeAction,
        quality_action: QualityAction,
    ):
        self.name = name
        self.volume = volume_action
        self.quality = quality_action
        # Assigned trust score for each round participated in.
        self.trust_by_round = []


class Simulation:
    def __init__(self, chi: float, providers: List[Provider]):
        self.chi = chi
        self.providers = providers
        # The maximum possible trust score (not scaled) for each round.
        self.unscaled_t_max_by_round: List[float] = [
            trust_score_delta[QualityAction.HIGH] + trust_score_delta[VolumeAction.LOW],
        ]

    def run(self, rounds: int) -> None:
        for k in range(1, rounds + 1):
            print(f'Round {k}')
            for p in self.providers:
                t = trust_score_delta[p.quality] + trust_score_delta[p.volume]
                if not p.trust_by_round:
                    p.trust_by_round.append(t)
                else:
                    p.trust_by_round.append(p.trust_by_round[-1] + t)

                payoff = get_payoff(p)
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


if __name__ == '__main__':
    print('P (V_low, Q_low), OP (V_low, Q_low)')
    s = Simulation(chi=CHI, providers=[
            Provider('P', VolumeAction.LOW, QualityAction.LOW),
            Provider('OP', VolumeAction.LOW, QualityAction.LOW),
        ],
    )

    s.run(4)
    print()

    print('P (V_low, Q_low), OP (V_low, Q_high)')
    s = Simulation(chi=CHI, providers=[
            Provider('P', VolumeAction.LOW, QualityAction.LOW),
            Provider('OP', VolumeAction.LOW, QualityAction.HIGH),
        ],
    )

    s.run(4)
    print()

    print('P (V_low, Q_high), OP (V_low, Q_high)')
    s = Simulation(chi=CHI, providers=[
            Provider('P', VolumeAction.LOW, QualityAction.HIGH),
            Provider('OP', VolumeAction.LOW, QualityAction.HIGH),
        ],
    )

    s.run(4)
    print()

    ###########################################################################

    print('P (V_high, Q_low), OP (V_high, Q_low)')
    s = Simulation(chi=CHI, providers=[
            Provider('P', VolumeAction.HIGH, QualityAction.LOW),
            Provider('OP', VolumeAction.HIGH, QualityAction.LOW),
        ],
    )

    s.run(4)
    print()

    print('P (V_high, Q_low), OP (V_high, Q_high)')
    s = Simulation(chi=CHI, providers=[
            Provider('P', VolumeAction.HIGH, QualityAction.LOW),
            Provider('OP', VolumeAction.HIGH, QualityAction.HIGH),
        ],
    )

    s.run(4)
    print()

    print('P (V_high, Q_high), OP (V_high, Q_high)')
    s = Simulation(chi=CHI, providers=[
            Provider('P', VolumeAction.HIGH, QualityAction.HIGH),
            Provider('OP', VolumeAction.HIGH, QualityAction.HIGH),
        ],
    )

    s.run(4)
    print()
