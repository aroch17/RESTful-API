from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import asc
import random as r

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


with app.app_context():
    db.create_all()
    cafes = db.session.query(Cafe).all()


def make_cafe_json(cafe):
    return {
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "seats": cafe.seats,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "has_sockets": cafe.has_sockets,
        "can_take_calls": cafe.can_take_calls,
        "coffee_price": cafe.coffee_price,
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/random")
def random():
    global cafes
    random_cafe = r.choice(cafes)
    return jsonify(cafe=make_cafe_json(random_cafe))


@app.route("/all")
def get_all():
    global cafes
    cafes_dict = {}
    for cafe in cafes:
        cafes_dict[f"{cafe.id}"] = make_cafe_json(cafe)
    # jsonify() jumbles up the order of cafes_dict
    return jsonify(cafes=cafes_dict)


@app.route("/search")
def search():
    global cafes
    cafes_dict = {}
    # Gets value provided after "?loc="
    loc = request.args.get("loc")
    for cafe in cafes:
        if loc == cafe.location:
            cafes_dict[f"{cafe.id}"] = make_cafe_json(cafe)
    if cafes_dict:
        return jsonify(cafes=cafes_dict)
    return jsonify(
        error={
            "Not Found": "Sorry, we don't have a cafe in that location."
        }
    )


@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route("/update-price/<cafe_id>", methods=["GET", "PATCH"])
def update_price(cafe_id):
    cafe_to_update = db.session.query(Cafe).get(int(cafe_id))
    if cafe_to_update:
        cafe_to_update.coffee_price = request.args.get("new_price")
        db.session.commit()
        return jsonify(success="Successfully updated the price.")
    return jsonify(error={"Not Found": "A cafe with that id does not exist."})


if __name__ == '__main__':
    app.run(debug=True)
