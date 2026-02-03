from flask import Flask, request, render_template, redirect


app = Flask(__name__)


# dummy code to show basic flask
@app.route('/')                
def home_page(): 
    return redirect("/login")

# basic POST handling demo 
@app.route("/login", methods=["GET", "POST"])
def login(): 
    if request.method == "POST": 
        name = request.form['username']
        # validate with database here 

        return f"Hello {name}, POST request received"
        # redirect to another page here 
    return render_template("login.html")
        


if __name__ == '__main__': 
    app.run()