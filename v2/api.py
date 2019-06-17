import pymysql
import base64
from flask import Flask
from flask import jsonify
from flask import render_template

app = Flask(__name__)

try:
    db = pymysql.connect(
              host="localhost",
              user="threadripper",
              passwd="1337",
              db="threadrip",
              port=3306,
              autocommit=True
         )
    cur = db.cursor()
except Exception as e:
    print("=-=-=ERROR=-=-=",
          "DB CONN FAILED!!",
          "=-=-=-=-=-=-=-=", sep="\n")
    exit(1)

@app.route("/", methods=['GET'])
def index():
    total = getTotalImages()
    return render_template("index.html", total=total[0])

@app.route("/api/image/random/", methods=['GET'])
def random():
    query = "SELECT * FROM images ORDER BY RAND() LIMIT 1"
    cur.execute(query)
    val = cur.fetchone()
    val = [ v for v in val ]
    try:
        val.append(base64.b64encode(open(val[2], "rb").read()).decode("UTF-8"))
    except Exception as e:
        random()
    return jsonify(val)

@app.route("/api/image/<id>", methods=['GET'])
def getById(id):
    id = db.escape(id)
    query = "SELECT * FROM images WHERE iid = {}".format(id)
    cur.execute(query)
    if cur.rowcount == 1:
        val = cur.fetchone()
        val = [ v for v in val ]
        try:
            val.append(base64.b64encode(open(val[2], "rb").read()).decode("UTF-8"))
        except Exception as e:
            id = int(id.replace("'", "")) + 1
            getById(id)
    else:
        val = {"error": "No entrys found!"}
    return jsonify(val)

@app.route("/api/comment/random", methods=['GET'])
def getRandomComment():
    query = "SELECT * FROM comments ORDER BY RAND() LIMIT 1"
    cur.execute(query)
    return jsonify(cur.fetchone())

def getTotalImages():
    query = "SELECT COUNT(iid) FROM images"
    cur.execute(query)
    return cur.fetchone()

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
