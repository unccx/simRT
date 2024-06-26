import math
import time
from math import ceil, floor
from typing import Optional, Sequence

from simpy.core import SimTime
from tqdm import trange

from simRT.core import task
from simRT.core.processor import PlatformInfo, SpeedType
from simRT.core.task import TaskInfo


class Schedulability:
    @staticmethod
    def DBF(tau: TaskInfo, delta_t: SimTime) -> SimTime:
        """
        Demand Bound Function
        """
        return max(0, (floor((delta_t - tau.deadline) / tau.period) + 1) * tau.wcet)

    @staticmethod
    def LOAD(
        Gamma: Sequence[TaskInfo],
        implicit_deadline: bool = False,
        sampling_rate: float = 0.00001,
        show_progress: bool = False,
    ):
        hyper_period = math.lcm(*[math.ceil(tau.period) for tau in Gamma])

        if implicit_deadline is True:
            delta_t = hyper_period
            return sum(Schedulability.DBF(tau, delta_t) for tau in Gamma) / delta_t

        load = 0
        step = ceil(hyper_period * sampling_rate)
        if show_progress is True:
            for delta_t in trange(1, hyper_period + 1, step, desc="Calculating load"):
                load = max(
                    load,
                    sum(Schedulability.DBF(tau, delta_t) for tau in Gamma) / delta_t,
                )
        else:
            for delta_t in range(1, hyper_period + 1, step):
                load = max(
                    load,
                    sum(Schedulability.DBF(tau, delta_t) for tau in Gamma) / delta_t,
                )
        return load

    @staticmethod
    def G_EDF_sufficient_test(
        Gamma: Sequence[TaskInfo],
        processors: PlatformInfo,
        sampling_rate: float = 0.00001,
        show_progress: bool = False,
    ):
        """
        Sufficient test for multi-core Global-EDF.
        """
        assert (
            len(processors.speed_list) > 1
        ), "This sufficient test is for multi-core platforms"
        speed_list = processors.speed_list

        varphi_max = max(tau.density for tau in Gamma)
        lambda_pi = max(
            sum(speed_list[i + 1 :]) / speed_list[i]
            for i in range(0, len(speed_list) - 1)
        )
        mu = processors.S_m - lambda_pi * varphi_max
        v = max([i + 1 for i in range(0, len(speed_list)) if sum(speed_list[i:]) < mu])

        implicit_deadline = all(
            taskinfo.deadline == taskinfo.period for taskinfo in Gamma
        )

        load = Schedulability.LOAD(
            Gamma, implicit_deadline, sampling_rate, show_progress
        )

        return mu - v * varphi_max >= load
