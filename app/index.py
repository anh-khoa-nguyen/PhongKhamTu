from flask import render_template
from PhongKhamTu.app import app



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/examine")
def examine():
    return render_template('examine.html')


if __name__ == '__main__':
    app.run(debug=True)



