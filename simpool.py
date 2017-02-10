import random
from collections import defaultdict


class Game(object):
    def __init__(
        self,
        players
    ):
        # players is a list of Player instances
        self.players = players
        # balls will be divided evenly - this assumes there is
        # an even ratio of balls to players
        self.number_of_balls = 15
        # order out will be a list of dicts
        # with how many balls each other player has)
        self.order_out = []
        self.players_that_were_out = []

    @property
    def current_player(self):
        return self.players[0]

    @property
    def current_players_opponents(self):
        return self.players[1:]

    @property
    def current_live_opponents(self):
        return [
            player
            for player in self.current_players_opponents
            if player.balls_on_table
        ]

    def take_next_shot(self):
        # check if a player made a ball
        if random.uniform(0, 1) < self.current_player.chance_to_make_a_ball:
            loser = self.current_player.pick_ball_to_pocket(
                self.current_live_opponents)
            loser.lose_ball()
            if not loser.balls_on_table:

                scoresheet = {
                    player.name: player.balls_on_table
                    for player in self.players
                }
                # import ipdb; ipdb.set_trace()
                self.players_that_were_out.append(loser.name)
                self.order_out.append(scoresheet)
        else:
            self.go_to_next_player()

        # check for scratch
        if random.uniform(0, 1) < self.current_player.chance_to_scratch:
            [
                player.gain_ball()
                for player in self.players if player != self.current_player
            ]
            if self.order_out:

                self.order_out = []

    def go_to_next_player(self):
        self.players = self.players[1:] + self.players[0:1]
        if not self.current_player.balls_on_table:
            self.go_to_next_player()

    def check_for_winner(self):
        player_with_balls_on_table = None
        for player in self.players:
            if player.balls_on_table:
                if player_with_balls_on_table:
                    return False
                player_with_balls_on_table = player
        return player_with_balls_on_table

    def play_game(self):
        self.take_next_shot()
        winner = self.check_for_winner()
        if winner:
            winner_was_out = winner.name in self.players_that_were_out
            return winner, self.order_out, winner_was_out
        return self.play_game()


class Player(object):
    def __init__(
        self, name, chance_to_make_a_ball, chance_to_scratch,
        max_balls=5, starting_balls=5
    ):
        self.name = name
        self.balls_on_table = starting_balls
        self.max_balls = max_balls
        self.starting_balls = starting_balls
        self.chance_to_make_a_ball = chance_to_make_a_ball
        self.chance_to_scratch = chance_to_scratch
        self.was_out = False

    def __repr__(self):
        return "< Player: %s balls: %s>" % (self.name, self.balls_on_table)

    def pick_ball_to_pocket(self, current_players):
        return random.choice([
            player for player in current_players
            for _ in xrange(player.balls_on_table)
        ])

    def set_starting_balls(self, number_of_balls):
        self.max_balls = number_of_balls
        self.balls_on_table = number_of_balls

    def lose_ball(self):
        if self.balls_on_table > 0:
            self.balls_on_table -= 1

    def gain_ball(self):
        if self.balls_on_table < self.max_balls:
            self.balls_on_table += 1


class PlayerZak(Player):
    def pick_ball_to_pocket(self, current_players):
        return sorted(current_players, key=lambda k: k.balls_on_table)[0]


class PlayerEliot(Player):
    def pick_ball_to_pocket(self, current_players):
        return sorted(
            current_players, key=lambda k: k.balls_on_table, reverse=True)[0]


def run_test():

    stats = {
        "winner": defaultdict(int),
        "winner_rank_at_first_out": {},
        "winner_was_out": 0
    }

    rank_at_first_out_stats = stats["winner_rank_at_first_out"]

    for _ in xrange(10000):
        test_players = [
            Player(
                name="neutral",
                chance_to_make_a_ball=.33,
                chance_to_scratch=.05,
                starting_balls=5
            ),
            PlayerZak(
                name="eliot",
                chance_to_make_a_ball=.33,
                chance_to_scratch=.05,
                starting_balls=1
            ),
            Player(
                name="zak",
                chance_to_make_a_ball=.33,
                chance_to_scratch=.05,
                starting_balls=1
            ),
        ]
        game = Game(test_players)
        winner, order_out, winner_was_out = game.play_game()
        stats["winner"][winner.name] += 1
        scores_on_first_out_dict = order_out[0]
        scores_on_first_out = [
            (player, score) for player, score in order_out[0].iteritems()
        ]

        ranked_on_first_out = [
            player
            for player, _ in sorted(
                scores_on_first_out, key=lambda x: x[1], reverse=True)
        ]

        winner_rank = ranked_on_first_out.index(winner.name)

        winner_rank_at_first_out_stats = rank_at_first_out_stats.get(winner.name, {})

        winner_rank_at_first_out_stats = (
            rank_at_first_out_stats.get(winner.name, {})
        )
        winner_rank_at_first_out_stats[winner_rank] = (
            winner_rank_at_first_out_stats.get(winner_rank, 0) + 1
        )

        rank_at_first_out_stats[winner.name] = winner_rank_at_first_out_stats

        difference_at_first_out = (
            scores_on_first_out_dict[ranked_on_first_out[0]] -
            scores_on_first_out_dict[ranked_on_first_out[1]]
        )

        winner_difference_at_first_out = difference_at_first_out
        if winner_rank != 0:
            winner_difference_at_first_out *= -1

        if winner_was_out:
            stats["winner_was_out"] += 1
    return stats
from pprint import pprint
pprint(run_test())























