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

        #индексы роботов:
        self.bot_al_1 = 0
        self.bot_al_2 = 1
        self.gk_al = const.GK
        self.bot_en_1 = 1
        self.bot_en_2 = 2
        self.bot_gk_en = 3

        global geo_pos

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
        # waypoints[0] = wp.Waypoint(
        #             aux.Point(0, 0),
        #             field.allies[i].get_angle(),
        #             wp.WType.S_ENDPOINT,
        #         )
        # return waypoints
        self.attacker(field, waypoints)
        # waypoints[10] = wp.Waypoint(aux.Point(0, 0), 0, wp.WType.S_ENDPOINT)
        self.goal_keeper(field, waypoints)
        
        # waypoints[7] = wp.Waypoint(aux.Point(0, 0), 0, wp.WType.S_ENDPOINT)

        return waypoints

    def attacker(self, field: fld.Field, waypoints: list[wp.Waypoint]) -> None:
        smallest_dist_al = 100000
        for i in range(0, 2):
            if (field.allies[i].get_pos() - field.ball.get_pos()).mag() < smallest_dist_al:
                self.nearest_bot_al = i
                self.farthest_bot_al = i + 1
                if i == 1:
                    self.farthest_bot_al = 0
                smallest_dist_al = (field.allies[i].get_pos() - field.ball.get_pos()).mag()
        smallest_dist_en = 100000
        for i in range(1, 3):
            if (field.enemies[i].get_pos() - field.ball.get_pos()).mag() < smallest_dist_en:
                self.nearest_bot_en = i
                self.farthest_bot_en = i + 1
                if i == 1:
                    self.farthest_bot_en = 0
                smallest_dist_en = (field.enemies[i].get_pos() - field.ball.get_pos()).mag()
        smallest_dist_al_to_en = 100000
        for i in range(0, 2):
            if (field.enemies[self.nearest_bot_al].get_pos() - field.allies[i].get_pos()).mag() < smallest_dist_al_to_en:
                self.nearest_bot_al_to_en = i
                self.farthest_bot_al_to_en = i + 1
                if i == 1:
                    self.farthest_bot_al_to_en = 0
                smallest_dist_al_to_en = (field.enemies[self.nearest_bot_al].get_pos() - field.allies[i].get_pos()).mag()
        if smallest_dist_al < smallest_dist_en:
            # #Нападение
            # vec = field.enemy_goal.center - field.allies[self.nearest_bot_al].get_pos()
            # if (aux.Point(2250, -300) - field.enemies[self.bot_gk_en].get_pos()).mag() < (aux.Point(2250, 300) - field.enemies[self.bot_gk_en].get_pos()).mag():
            #     vec = aux.Point(2250,  300) - field.allies[self.nearest_bot_al].get_pos()
            #     waypoints[self.nearest_bot_al] = wp.Waypoint(field.ball.get_pos(), vec.arg(), wp.WType.S_BALL_KICK)
            # elif (aux.Point(2250, -300) - field.enemies[self.bot_gk_en].get_pos()).mag() > (aux.Point(2250, 300) - field.enemies[self.bot_gk_en].get_pos()).mag():
            #     vec = aux.Point(2250, -300) - field.allies[self.nearest_bot_al].get_pos()
            #     waypoints[self.nearest_bot_al] = wp.Waypoint(field.ball.get_pos(), vec.arg(), wp.WType.S_BALL_KICK)
            # else:
            #     vec = aux.Point(2250, 300) - field.allies[self.nearest_bot_al].get_pos()
                waypoints[self.nearest_bot_al] = wp.Waypoint(field.ball.get_pos(), vec.arg(), wp.WType.S_BALL_KICK)
        #     rs1 = (field.enemy_goal.center - field.allies[self.farthest_bot_al].get_pos()).mag()
        #     rs2 = (field.enemy_goal.center - field.allies[self.nearest_bot_al].get_pos()).mag()
        #     rs3 = (field.enemies[1].get_pos() - aux.closest_point_on_line(field.allies[self.nearest_bot_al].get_pos(), field.allies[self.farthest_bot_al].get_pos(), field.ball.get_pos())).mag() > 30
        # #     if rs1 < rs2 and rs3:
        # #         vec = field.allies[self.farthest_bot_al].get_pos() - field.allies[self.nearest_bot_al].get_pos()
        # # else:
        # #     attacker = fld.find_nearest_robot(field.ball.get_pos(),field.allies,[const.GK])
        # #     waypoints[attacker.r_id] = wp.Waypoint((field.ball.get_pos()-fld.find_nearest_robot(field.ball.get_pos(),field.enemies,[const.ENEMY_GK]).get_pos()).unity()*200+field.ball.get_pos(),aux.angle_to_point(attacker.get_pos(),field.ball.get_pos()),wp.WType.S_ENDPOINT)
        else:
            #Def
            vec1 = field.enemies[self.nearest_bot_en].get_pos() - field.ball.get_pos()
            waypoints[self.nearest_bot_al_to_en] = wp.Waypoint(field.ball.get_pos(), vec1.arg(), wp.WType.S_BALL_GRAB)
            pos = aux.point_on_line(field.ball.get_pos(), field.enemies[self.farthest_bot_en].get_pos(), 15)
            vec2 = field.ball.get_pos() - pos
            waypoints[self.farthest_bot_al_to_en] = wp.Waypoint(pos, vec2.arg(), wp.WType.S_BALL_GRAB)
    def goal_keeper(self, field: fld.Field, waypoints: list[wp.Waypoint]) -> None:
        #aux.get_line_intersection(atacker, ball, field.ally_goal.frw_up, field.ally_goal.frw_down, "RS")
        vec = field.ball.get_pos() - field.enemies[self.nearest_bot_en].get_pos()
        point_0 = aux.get_line_intersection(field.enemies[self.nearest_bot_en].get_pos(), field.ball.get_pos(), field.ally_goal.frw_up, field.ally_goal.frw_down, "RS")
        point_1 = aux.get_line_intersection(field.enemies[self.nearest_bot_en].get_pos(), field.ball.get_pos(), field.ally_goal.center_up, field.ally_goal.frw_up, "RS")
        point_2 = aux.get_line_intersection(field.enemies[self.nearest_bot_en].get_pos(), field.ball.get_pos(), field.ally_goal.center_down, field.ally_goal.frw_down, "RS")
        if point_0 is not None:
            waypoints[self.gk_al] = wp.Waypoint(point_0, vec.arg(), wp.WType.S_BALL_GRAB)
        elif point_1 is not None:
            waypoints[self.gk_al] = wp.Waypoint(point_1, vec.arg(), wp.WType.S_BALL_GRAB)
        elif point_2 is not None:
            waypoints[self.gk_al] = wp.Waypoint(point_2, vec.arg(), wp.WType.S_BALL_GRAB)
        else:
            waypoints[self.gk_al] = wp.Waypoint(field.ally_goal.center, vec.arg(), wp.WType.S_ENDPOINT)
        # waypoints[self.gk_al] = wp.Waypoint(field.ally_goal.center, 0, wp.WType.S_ENDPOINT)
        if field.is_ball_stop_near_goal:
            
            ang = 
