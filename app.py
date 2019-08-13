from flask import request, render_template, Flask

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("test.html")

@app.route('/your/flask/endpoint', methods=['POST'])
def get_names():
    if request.method == 'POST':
       names = request.get_json()
       for i in names:
            print(names[i])			
    return '', 200

@app.route('/your/flask/2', methods=['POST'])
def fuckd():
    if request.method == 'POST':
        ids = request.get_json()
        for i in ids:
            print(ids[i])		
    return '', 200

if __name__ == "__main__":
    app.run(debug=True)