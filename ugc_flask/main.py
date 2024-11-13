from flask import (
    Flask,
    render_template,
)

from flask_jwt_extended import (
    jwt_required,
    JWTManager,
    # get_jwt_header,
    # get_jwt,
)

from settings import JWT_PUBLIC_KEY, JWT_ALGORITHM
from api.v1.api import api


app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

app.config['JWT_PUBLIC_KEY'] = JWT_PUBLIC_KEY.read_text()
app.config['JWT_ALGORITHM'] = JWT_ALGORITHM

jwt = JWTManager(app)


@app.route("/")
@jwt_required(optional=True)
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')
