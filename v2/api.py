import pymysql
import base64
import os
from flask import Flask
from flask import jsonify
from flask import render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

class DB:
    conn = None

    def connect(self):
        try:
            self.conn = pymysql.connect(
                      host="localhost",
                      user="threadripper",
                      passwd="1337",
                      db="threadrip",
                      port=3306,
                      autocommit=True
                 )
        except Exception as e:
            print("=-=-=ERROR=-=-=",
                  "DB CONN FAILED!!",
                  "=-=-=-=-=-=-=-=", sep="\n")
            exit(1)

    def query(self, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
        except Exception as e:
            self.connect()
            cur = self.conn.cursor()
            cur.execute(query)
        return cur

    def escape(self, value):
        return self.conn.escape(value)

db = DB()
db.connect()

@app.route("/", methods=['GET'])
@limiter.limit("1/second")
def index():
    total = getTotalImages()
    return render_template("index.html", total=total[0])

@app.route("/api/image/random/", methods=['GET'])
def random():
    query = "SELECT * FROM images ORDER BY RAND() LIMIT 1"
    val = db.query(query).fetchone()
    val = [ v for v in val ]
    try:
        if os.path.exists(val[2]) and os.path.isfile(val[2]):
            val.append(base64.b64encode(open(val[2], "rb").read()).decode("UTF-8"))
            val[2] = val[2][(val[2].rfind("/")+1):]
        else:
            return random()
    except Exception as e:
        return random()
    return jsonify(val)

@app.route("/api/image/<id>", methods=['GET'])
@limiter.limit("1/second")
def getById(id):
    id = db.escape(id)
    query = "SELECT * FROM images WHERE iid = {}".format(id)
    cur = db.query(query)
    if cur.rowcount == 1:
        val = cur.fetchone()
        val = [ v for v in val ]
        try:
            val.append(base64.b64encode(open(val[2], "rb").read()).decode("UTF-8"))
            val[2] = val[2][(val[2].rfind("/")+1):]
        except Exception as e:
            id = int(id.replace("'", "")) + 1
            getById(id)
    else:
        val = {"error": "No entrys found!"}
    return jsonify(val)

@app.route("/api/comment/random", methods=['GET'])
@limiter.limit("1/second")
def getRandomComment():
    query = "SELECT * FROM comments ORDER BY RAND() LIMIT 1"
    return jsonify(db.query(query).fetchone())

def getTotalImages():
    query = "SELECT COUNT(iid) FROM images"
    return db.query(query).fetchone()

def main():
    limiter.init_app(app)
    app.run(debug=True)

if __name__ == "__main__":
    main()
