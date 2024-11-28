r"""
model.py

This module defines the England & Wales Model and provides a command-line interface (CLI) to run the simulation.

Classes:

    None

Functions:

    run(\*\*kwargs)

        Runs the model simulation with the specified parameters.

        Parameters:

            - nticks (int): Number of ticks to run the simulation. Default is 365.
            - seed (int): Random seed for the simulation. Default is 20241107.
            - verbose (bool): If True, print verbose output. Default is False.
            - viz (bool): If True, display visualizations to help validate the model. Default is True.
            - pdf (bool): If True, output visualization results as a PDF. Default is False.
            - output (str): Output file for results. Default is None.
            - params (str): JSON file with parameters. Default is None.
            - param (tuple): Additional parameter overrides in the form of (param:value or param=value). Default is an empty tuple.

Usage:

    To run the simulation from the command line (365 ticks, 20241107 seed, show visualizations):

        ``laser``

    To run the simulation with custom parameters, e.g., 5 years, 314159265 seed, output to PDF:

        ``laser --nticks 1825 --seed 314159265 --pdf``
"""

import click
import numpy as np
import pandas as pd
from laser_core.propertyset import PropertySet

from laser_model import Model
from laser_model import Step
from laser_model.england_wales.params import get_parameters
from laser_model.england_wales.scenario import get_scenario
from laser_model.mixing import init_gravity_diffusion


class EnglandWalesModel(Model):
    def __init__(self, scenario: pd.DataFrame, parameters: PropertySet, name: str = "EnglandWalesModel") -> None:
        """
        Initializes the model with the given scenario and parameters.

        Args:

            scenario (pd.DataFrame): The scenario data for the model.
            parameters (PropertySet): The parameters for the model.
            name (str): The name of the model.

        Returns:

            None
        """

        super().__init__(scenario, parameters, name)

        # create the state vector for each of the nodes (3, num_nodes)
        self.nodes.add_vector_property("states", len(self.params.states))  # S, I, R

        # initialize components
        self.components = [Step]

        # initialize the state counts in each node
        self.init_state(scenario, parameters)

    def init_state(self, settlements, params):
        """
        Initializes the state of the model with the given settlement and parameters.

        Args:
            settlement_s (pd.DataFrame): The settlement data for the model.
            params (PropertySet): The parameters for the model.

        Returns:
            None
        """

        population = settlements.population.astype(int)
        births = settlements.births.astype(int)

        num = population
        susc = births * 2
        inf = susc / 26.0 / 2.0
        inf = inf.astype(self.nodes.states.dtype)  # correct type

        # self.nodes.states[0,?]
        self.nodes.states[:, :] = np.array([susc, inf, num - susc - inf], dtype=self.nodes.states.dtype)  # S

        params.population = population
        params.births = births
        params.biweek_avg_births = params.demog_scale * births / 26.0
        params.biweek_death_prob = params.demog_scale * births / num / 26.0

        params.mixing = init_gravity_diffusion(settlements, params.mixing_scale, params.distance_exponent)

        return

    def plot(self, fig=None):
        yield None


@click.command()
@click.option("--nticks", default=365, help="Number of ticks to run the simulation")
@click.option("--seed", default=20241107, help="Random seed")
@click.option("--verbose", is_flag=True, help="Print verbose output")
@click.option("--viz", is_flag=True, default=True, help="Display visualizations  to help validate the model")
@click.option("--pdf", is_flag=True, help="Output visualization results as a PDF")
@click.option("--output", default=None, help="Output file for results")
@click.option("--params", default=None, help="JSON file with parameters")
@click.option("--param", "-p", multiple=True, help="Additional parameter overrides (param:value or param=value)")
def run(**kwargs):
    """
    Run the model simulation with the given parameters.

    This function initializes the model with the specified parameters, sets up the
    components of the model, seeds initial infections, runs the simulation, and
    optionally visualizes the results.

    Parameters:
        **kwargs: Arbitrary keyword arguments containing the parameters for the simulation.

            Expected keys include:
                - "nticks": (int) Number of ticks to run the simulation.
                - "seed": (int) Random seed for the simulation.
                - "verbose": (bool) Whether to print verbose output.
                - "viz": (bool) Whether to visualize the results.
                - "pdf": (bool) Whether to output visualization results as a PDF.
                - "output": (str) Output file for results.
                - "params": (str) JSON file with parameters.
                - "param": (tuple) Additional parameter overrides in the form of (param:value or param=value).

    Returns:
        None
    """

    # initialize
    scenario = get_scenario()
    parameters = get_parameters(kwargs)
    model = EnglandWalesModel(scenario, parameters)
    # add phases
    model.components = [Step]

    # run the model
    model.run()

    if parameters["viz"]:
        model.visualize(pdf=parameters["pdf"])

    return


if __name__ == "__main__":
    ctx = click.Context(run)
    ctx.invoke(run, nticks=365, seed=20241107, verbose=True, viz=True, pdf=False)
