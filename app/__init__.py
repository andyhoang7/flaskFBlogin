from flask import Flask, redirect, url_for, flash, render_template, jsonify, request
from flask_login import login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .models import db, login_manager, Excerpts, Scores, Token
from .oauth import blueprint
from .cli import create_db
import os
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
login_manager.init_app(app)

migrate = Migrate(app, db)


@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout(): 
    
    deleting_token = Token.query.filter_by(user_id=current_user.id).first()
    if deleting_token:
        db.session.delete(deleting_token)
        db.session.commit()
    logout_user()
    flash("You have logged out")
    
    return redirect(url_for("index"))


@app.route("/")
def index():
    return render_template("home.html")

@app.route('/test')
@login_required
def test():
  return jsonify({
      "success": True, 
      "user_id": current_user.id, 
      "user_name": current_user.name})
  

CORS(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['SECRET_KEY']= 'supersecret'

@app.route('/', methods=['GET'])
def home():
    return jsonify(['Foo', 'Bar'])

@app.route('/excerpts', methods=['GET'])
def list():
    a = Excerpts.query.all()
    resp = []
    for i in a:
        resp.append({"id":i.id,
                     'body':i.body})
    return jsonify(resp)


@app.route('/postscore', methods=['GET', 'POST'])
@login_required
def postscore():
    data = request.get_json()
    score = Scores(
        wpm = data['wpm'],
        time = data['time'],
        error = data['errors'],
        user_id = current_user.id,
        excerp_id = data['excerpt_id']
    )
    db.session.add(score)
    db.session.commit()
    return jsonify({"status":200})
    

@app.route('/thien')
def thien():
    p=["The.",
        "Win.", 
        "Bent.", 
        "Each."]
    for i in p:
        new=Excerpts(body=i)
        db.session.add(new)
        db.session.commit()
    return "ok"

if __name__ == "__main__":
    app.run(debug=True)