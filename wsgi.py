from app import app
from app.db import Session


@app.teardown_appcontext
def shutdown_session(exception=None):
    Session.remove()


if __name__ == '__main__':
    app.run(debug=True)
