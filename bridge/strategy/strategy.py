"""Верхнеуровневый код стратегии"""

# pylint: disable=redefined-outer-name

# @package Strategy
# Расчет требуемых положений роботов исходя из ситуации на поле


import math

# !v DEBUG ONLY
from enum import Enum
from time import time
from typing import Optional

import bridge.router.waypoint as wp
from bridge import const
from bridge.auxiliary import aux, fld, rbt
from bridge.processors.referee_state_processor import Color as ActiveTeam
from bridge.processors.referee_state_processor import State as GameStates
from bridge.strategy import ref_states


class Strategy:
    """Основной класс с кодом стратегии"""

    def __init__(
        self,
        dbg_game_status: GameStates = GameStates.RUN,
    ) -> None:

        self.game_status = dbg_game_status
        self.active_team: ActiveTeam = ActiveTeam.ALL
        self.we_active = False

        self.bot_al_1 = 7
        self.bot_al_2 = 8
        self.gk_al = const.GK
        self.bot_en_1 = 0
        self.bot_en_2 = 1
        self.bot_en_3 = 2

    def change_game_state(self, new_state: GameStates, upd_active_team: ActiveTeam) -> None:
        """Изменение состояния игры и цвета команды"""
        self.game_status = new_state
        self.active_team = upd_active_team

    def process(self, field: fld.Field) -> list[wp.Waypoint]:
        """
        Рассчитать конечные точки для каждого робота
        """
        print(123)

        waypoints: list[wp.Waypoint] = []
        for i in range(const.TEAM_ROBOTS_MAX_COUNT):
            waypoints.append(
                wp.Waypoint(
                    field.allies[i].get_pos(),
                    field.allies[i].get_angle(),
                    wp.WType.S_STOP,
                )
            )
        self.attacker(field, waypoints)
        # waypoints[10] = wp.Waypoint(aux.Point(0, 0), 0, wp.WType.S_ENDPOINT)
        self.goal_keeper(field, waypoints)

        return waypoints

    def attacker(self, field: fld.Field, waypoints: list[wp.Waypoint]) -> None:
        smallest_dist = 100000
        for i in range(7, 9):
            if (field.allies[i].get_pos() - field.ball.get_pos()).mag() < smallest_dist:
                self.nearest_bot = i
                self.farthest_bot = i + 1
                if i == 8:
                    self.farthest_bot = 7
                smallest_dist = (field.allies[i].get_pos() - field.ball.get_pos()).mag()
        vec = field.ally_goal.center - field.allies[self.bot_al_1].get_pos()
        waypoints[self.bot_al_1] = wp.Waypoint(field.ball.get_pos(), vec.arg(), wp.WType.S_BALL_KICK)
    
    def goal_keeper(self, field: fld.Field, waypoints: list[wp.Waypoint]) -> None:
        #aux.get_line_intersection(atacker, ball, field.ally_goal.frw_up, field.ally_goal.frw_down, "RS")
        smallest_dist = 100000
        for i in range(7, 9):
            if (field.allies[i].get_pos() - field.ball.get_pos()).mag() < smallest_dist:
                self.nearest_bot = i
                smallest_dist = (field.allies[i].get_pos() - field.ball.get_pos()).mag()
        vec = field.ball.get_pos() - field.allies[self.gk_al].get_pos()
        point_0 = aux.get_line_intersection(field.allies[self.nearest_bot].get_pos(), field.ball.get_pos(), field.ally_goal.frw_up, field.ally_goal.frw_down, "RS")
        point_1 = aux.get_line_intersection(field.allies[self.nearest_bot].get_pos(), field.ball.get_pos(), field.ally_goal.center_up, field.ally_goal.frw_up, "RS")
        point_2 = aux.get_line_intersection(field.allies[self.nearest_bot].get_pos(), field.ball.get_pos(), field.ally_goal.center_down, field.ally_goal.frw_down, "RS")
        if point_0 is not None:
            waypoints[self.gk_al] = wp.Waypoint(point_0, vec.arg(), wp.WType.S_ENDPOINT)
        elif point_1 is not None:
            waypoints[self.gk_al] = wp.Waypoint(point_1, vec.arg(), wp.WType.S_ENDPOINT)
        elif point_2 is not None:
            waypoints[self.gk_al] = wp.Waypoint(point_2, vec.arg(), wp.WType.S_ENDPOINT)
        else:
            waypoints[self.gk_al] = wp.Waypoint(field.ally_goal.center, vec.arg(), wp.WType.S_ENDPOINT)
        # waypoints[self.gk_al] = wp.Waypoint(field.ally_goal.center, 0, wp.WType.S_ENDPOINT)