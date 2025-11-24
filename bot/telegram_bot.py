import os
import joblib

from src.model.poisson_baseline import PoissonPredictor

# Simple bot-like handlers for tests
MODEL_PATH = os.environ.get('TELEGRAM_MODEL_PATH')

def load_model(path: str = None):
    if path is None:
        path = MODEL_PATH
    try:
        if path and os.path.exists(path):
            return joblib.load(path)
    except Exception:
        pass
    return PoissonPredictor()

predictor = load_model()

async def predict_cmd(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /predict HomeTeam;AwayTeam (use semicolon)")
        return
    text = " ".join(context.args)
    if ";" not in text:
        await update.message.reply_text("Please separate teams with a semicolon: Home;Away")
        return
    home, away = [s.strip() for s in text.split(";", 1)]
    try:
        res = predictor.predict_match(home, away)
        msg = (
            f"{home} vs {away}\n"
            f"Exp goals — {res['exp_goals_home']:.2f} / {res['exp_goals_away']:.2f}\n"
            f"P(Home): {res['p_home_win']:.2%}  Draw: {res['p_draw']:.2%}  P(Away): {res['p_away_win']:.2%}"
        )
    except Exception as e:
        msg = f'Error computing prediction: {e}'
    await update.message.reply_text(msg)

async def reload_model_cmd(update, context):
    global predictor
    predictor = load_model()
    await update.message.reply_text('Model reloaded (or empty predictor used if model missing).')
