import numpy as np

from laser_model.base import BaseComponent


class Step(BaseComponent):
    def __init__(self, model, verbose: bool = False) -> None:
        super().__init__(model, verbose)

    def __call__(self, model, tick: int) -> None:
        # TODO: implement math in-memory

        # state counts
        states = model.nodes.states

        def cast_type(a, dtype):
            return a.astype(dtype) if a.dtype != dtype else a

        # model parameters
        params = model.params

        # calculate the expected number of new infections
        expected = params.beta * (1 + params.seasonality * np.cos(2 * np.pi * tick / 26.0)) * np.matmul(params.mixing, states[1])
        prob = 1 - np.exp(-expected / states.sum(axis=0))  # probability of infection
        dI = cast_type(np.random.binomial(n=states[0], p=prob), states.dtype)  # number of new infections in S

        states[2] += states[1]  # move I to R (assuming 14 day recovery)
        states[1] = 0  # reset I

        births = cast_type(np.random.poisson(params.biweek_avg_births), states.dtype)  # number of births
        deaths = cast_type(np.random.binomial(n=states, p=params.biweek_death_prob), states.dtype)  # number of deaths

        states[0] += births  # add births to S
        states -= deaths  # remove deaths from each compartment

        states[1] += dI  # add new infections to I
        states[0] -= dI  # remove new infections from S

        return
