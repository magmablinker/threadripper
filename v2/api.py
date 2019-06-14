import pymysql
from flask import Flask
from flask import jsonify

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
    return("Yes")

@app.route("/api/image/random/", methods=['GET'])
def random():
    query = "SELECT * FROM images ORDER BY RAND() LIMIT 1"
    cur.execute(query)
    return jsonify(cur.fetchone())

@app.route("/api/image/<id>", methods=['GET'])
def getById(id):
    id = db.escape(id)
    query = "SELECT * FROM images WHERE iid = {}".format(id)
    cur.execute(query)
    return jsonify(cur.fetchone())

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
