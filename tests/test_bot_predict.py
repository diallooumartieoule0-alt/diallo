import asyncio
import types
from types import SimpleNamespace
import sys
import os

import pytest

# ensure project root is on sys.path so `src` and `bot` packages import correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model.poisson_baseline import PoissonPredictor

import bot.telegram_bot as telegram_bot


class DummyMessage:
    def __init__(self):
        self.replies = []

    async def reply_text(self, text):
        # store the last reply for assertions
        self.replies.append(text)


class DummyUpdate:
    def __init__(self):
        self.message = DummyMessage()


def make_context(arg_str: str):
    # context.args is a list of words the CommandHandler passes
    return SimpleNamespace(args=[arg_str])


def test_predict_cmd_basic():
    # Prepare a tiny fitted predictor so results are deterministic-ish
    df = __import__('pandas').DataFrame([
        {'home_team': 'A', 'away_team': 'B', 'home_goals': 2, 'away_goals': 1},
        {'home_team': 'B', 'away_team': 'A', 'home_goals': 0, 'away_goals': 3},
    ])
    p = PoissonPredictor()
    p.fit(df)

    # Monkeypatch the module-level predictor used by the bot
    telegram_bot.predictor = p

    update = DummyUpdate()
    context = make_context('A;B')

    # Run the async handler
    asyncio.run(telegram_bot.predict_cmd(update, context))

    # Assert that a reply was sent and contains expected fields
    assert update.message.replies, 'No reply sent by predict_cmd'
    text = update.message.replies[-1]
    assert 'A vs B' in text
    assert 'Exp goals' in text
    assert 'P(Home)' in text


def test_predict_cmd_missing_separator():
    # Ensure the command prompts for semicolon separation
    p = PoissonPredictor()
    telegram_bot.predictor = p
    update = DummyUpdate()
    context = make_context('A B')
    asyncio.run(telegram_bot.predict_cmd(update, context))
    assert update.message.replies, 'No reply sent for missing separator'
    assert 'Please separate teams' in update.message.replies[-1]


def test_reload_model_cmd(tmp_path, monkeypatch):
    # create a small model file and point TELEGRAM_MODEL_PATH to it
    df = __import__('pandas').DataFrame([
        {'home_team': 'X', 'away_team': 'Y', 'home_goals': 1, 'away_goals': 0}
    ])
    p = PoissonPredictor()
    p.fit(df)
    model_file = tmp_path / 'poisson_baseline_test.joblib'
    import joblib
    joblib.dump(p, str(model_file))

    monkeypatch.setenv('TELEGRAM_MODEL_PATH', str(model_file))

    update = DummyUpdate()
    context = make_context('')
    # Call reload command which should load the model without error
    asyncio.run(telegram_bot.reload_model_cmd(update, context))
    assert update.message.replies, 'No reply sent by reload_model_cmd'
    assert 'reloaded' in update.message.replies[-1].lower()
