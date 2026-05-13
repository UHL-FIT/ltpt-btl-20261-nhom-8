import sys

from app.controllers.gui_controller import run_app

__version__ = "1.0.0"

reconfigure_stdout = getattr(sys.stdout, "reconfigure", None)
if callable(reconfigure_stdout):
    reconfigure_stdout(encoding="utf-8")


if __name__ == "__main__":
    run_app()
