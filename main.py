from flask import Flask, render_template, request, redirect, url_for, flash
from flask_wtf import FlaskForm
from sqlalchemy.exc import SQLAlchemyError
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Boolean
from dotenv import load_dotenv
import os


load_dotenv()


app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv('SK')

class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Cafe(db.Model):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String, nullable=False)
    seats: Mapped[str] = mapped_column(String(100))
    has_wifi: Mapped[bool] = mapped_column(Boolean)
    has_sockets: Mapped[bool] = mapped_column(Boolean)
    can_take_calls: Mapped[bool] = mapped_column(Boolean)
    has_toilet: Mapped[bool] = mapped_column(String(100))


    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class CafeForm(FlaskForm):

    name = StringField(validators=[DataRequired()])
    location = StringField(validators=[DataRequired()])
    map_url = StringField(validators=[DataRequired()])
    img_url = StringField(validators=[DataRequired()])
    coffee_price = StringField(validators=[DataRequired()])
    seats = SelectField(choices=[
        ('0-10', '0-10'),
        ('10-20', '10-20'),
        ('20-30', '20-30'),
        ('30-40', '30-40'),
        ('40-50', '40-50'),
        ('50+', '50+')
    ])
    has_wifi = BooleanField()
    has_sockets = BooleanField()
    can_take_calls = BooleanField()
    has_toilet = BooleanField()
    submit = SubmitField()


with app.app_context():
    db.create_all()


def str_to_bool(value):
    return str(value).lower() == 'true'


@app.route('/')
def index():

    wifi = request.args.get('wifi')
    sockets = request.args.get('sockets')
    calls = request.args.get('calls')
    toilets = request.args.get('toilets')

    cafe_data = db.session.execute(db.select(Cafe)).scalars().all()
    cafes = [cafe.to_dict() for cafe in cafe_data]
    total = len(cafes)
    if wifi:
        cafes = [cafe for cafe in cafes if cafe['has_wifi']]
    if sockets:
        cafes = [cafe for cafe in cafes if cafe['has_sockets']]
    if calls:
        cafes = [cafe for cafe in cafes if cafe['can_take_calls']]
    if toilets:
        cafes = [cafe for cafe in cafes if cafe['has_toilet']]
    filtered = len(cafes)

    return render_template('index.html', cafes=cafes, total=total, filtered=filtered)


@app.route('/add', methods=['POST', 'GET'])
def add():
    form = CafeForm()

    if form.validate_on_submit():
        new_cafe = Cafe(name= form.name.data,
                        location= form.location.data,
                        map_url=form.map_url.data,
                        img_url=form.img_url.data,
                        coffee_price=form.coffee_price.data,
                        seats=form.seats.data,
                        has_wifi=form.has_wifi.data,
                        has_sockets=form.has_sockets.data,
                        can_take_calls=form.can_take_calls.data,
                        has_toilet=form.has_toilet.data,
                        )
        try:
            db.session.add(new_cafe)
            db.session.commit()
        except SQLAlchemyError as e:
            flash("Error connecting our database!", "error")
            db.session.rollback()
            print(f'DB Error:{str(e)}')
        else:
            flash("Cafe was added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/delete<cafe_id>')
def delete(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    answer = 'Do you want to delete this Cafe'
    if cafe:
        try:
            db.session.delete(cafe)
            db.session.commit()
        except SQLAlchemyError as e:
            flash("Error connecting our database!", "error")
            db.session.rollback()
            print(f'DB Error:{str(e)}')
        else:
            flash("Cafe was deleted successfully!", "success")
    return redirect(url_for('index'))


@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(debug=True)

