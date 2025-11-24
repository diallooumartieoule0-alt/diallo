from typing import Dict
import numpy as np
import pandas as pd
from scipy.stats import poisson


class PoissonPredictor:
    def __init__(self):
        self.fitted = False
        self.team_home_scored = {}
        self.team_away_scored = {}
        self.team_home_conceded = {}
        self.team_away_conceded = {}
        self.global_home_avg = 1.4
        self.global_away_avg = 1.1

    def fit(self, matches: pd.DataFrame):
        home = matches.groupby('home_team').agg(home_scored=('home_goals','mean'), home_conceded=('away_goals','mean'))
        away = matches.groupby('away_team').agg(away_scored=('away_goals','mean'), away_conceded=('home_goals','mean'))
        for idx, row in home.iterrows():
            self.team_home_scored[idx] = row['home_scored']
            self.team_home_conceded[idx] = row['home_conceded']
        for idx, row in away.iterrows():
            self.team_away_scored[idx] = row['away_scored']
            self.team_away_conceded[idx] = row['away_conceded']
        self.global_home_avg = matches['home_goals'].mean()
        self.global_away_avg = matches['away_goals'].mean()
        self.fitted = True

    def _expected_goals(self, home: str, away: str) -> (float, float):
        h_sc = self.team_home_scored.get(home, self.global_home_avg)
        a_con = self.team_away_conceded.get(away, self.global_away_avg)
        a_sc = self.team_away_scored.get(away, self.global_away_avg)
        h_con = self.team_home_conceded.get(home, self.global_home_avg)
        exp_home = (h_sc + a_con) / 2.0
        exp_away = (a_sc + h_con) / 2.0
        exp_home = max(0.01, float(exp_home))
        exp_away = max(0.01, float(exp_away))
        return exp_home, exp_away

    def predict_match(self, home: str, away: str, max_goals: int = 6) -> Dict:
        lam_h, lam_a = self._expected_goals(home, away)
        probs = np.outer(poisson.pmf(range(0, max_goals+1), lam_h), poisson.pmf(range(0, max_goals+1), lam_a))
        p_home_win = np.tril(probs, -1).sum()
        p_draw = np.trace(probs)
        p_away_win = np.triu(probs, 1).sum()
        return {
            'home_team': home,
            'away_team': away,
            'exp_goals_home': lam_h,
            'exp_goals_away': lam_a,
            'p_home_win': float(p_home_win),
            'p_draw': float(p_draw),
            'p_away_win': float(p_away_win),
        }
