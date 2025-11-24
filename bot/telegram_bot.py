import os
import joblib

from src.model.poisson_baseline import PoissonPredictor

# Simple bot-like handlers for tests
MODEL_PATH = os.environ.get('TELEGRAM_MODEL_PATH')

def load_model(path: str = None):
    if path is None:
        path = MODEL_PATH
    import os
    import time
    import signal
    import sys
    import joblib

    from src.model.poisson_baseline import PoissonPredictor

    # Simple bot-like handlers for tests
    MODEL_PATH = os.environ.get('TELEGRAM_MODEL_PATH')


    def load_model(path: str = None):
        if path is None:
            path = MODEL_PATH
        try:
            if path and os.path.exists(path):
                print(f"[bot] Loading model from: {path}")
                return joblib.load(path)
        except Exception as e:
            print(f"[bot] Failed to load model from {path}: {e}")
        print("[bot] Using empty PoissonPredictor fallback")
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


    def _graceful_exit(signum, frame):
        print(f"[bot] Received signal {signum}, exiting")
        sys.exit(0)


    def main():
        # Support DRY_RUN via env var DRY_RUN=1 or CLI arg --dry-run
        dry_run_env = os.environ.get('DRY_RUN', '0')
        dry_run_arg = '--dry-run' in sys.argv
        dry_run = dry_run_env == '1' or dry_run_arg

        signal.signal(signal.SIGINT, _graceful_exit)
        signal.signal(signal.SIGTERM, _graceful_exit)

        if dry_run:
            print('[bot] Starting in DRY_RUN mode: skipping Telegram connection')
            print('[bot] Predictor summary:')
            try:
                # print a tiny summary to make logs useful for smoke tests
                attrs = getattr(predictor, '__dict__', {})
                print(f"[bot] predictor type: {type(predictor).__name__}")
                print(f"[bot] predictor attrs keys: {list(attrs.keys())}")
            except Exception:
                pass
            # Keep process alive for container smoke tests
            while True:
                time.sleep(3600)

        # Normal mode: attempt to connect to Telegram (if python-telegram-bot installed)
        token = os.environ.get('TELEGRAM_TOKEN')
        if not token:
            print('[bot] TELEGRAM_TOKEN not set. Exiting.')
            sys.exit(1)

        try:
            from telegram import __version__ as _ptb_ver
            from telegram.ext import ApplicationBuilder, CommandHandler

            print(f"[bot] python-telegram-bot version: {_ptb_ver}")
            app = ApplicationBuilder().token(token).build()
            app.add_handler(CommandHandler('predict', predict_cmd))
            app.add_handler(CommandHandler('reload_model', reload_model_cmd))

            print('[bot] Starting Telegram bot...')
            app.run_polling()
        except Exception as e:
            print(f'[bot] Failed to start Telegram bot: {e}')
            sys.exit(1)


    if __name__ == '__main__':
        main()
