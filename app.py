from flask import Flask

app = Flask(__name__)

@app.route('/')
def Index():
    return "Hello flask application"


if __name__ == '__main__':
    app.run(debug=True)