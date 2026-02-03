from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def hello_world(): 
    return "Hello World"


@app.route("/lmao")
def lmao(): 
    return "Lmao"

@app.route("/login")
def login(): 
    if request.method == "POST": 
        pass 
        


if __name__ == '__main__': 
    app.run()