import sys

from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
import requests


app = Flask(__name__, template_folder='template')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
db = SQLAlchemy(app)

api_key = '7d88d02a0cfb736a54ca5b817142b185'
url = 'http://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
dict_with_weather_info = {}


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True, nullable=True)

    def __repr__(self):
        return f'City: {self.id}, {self.name}'


db.create_all()


@app.route('/add', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def start():
    if request.method == 'POST':
        city = request.form['city_name']
        response = requests.get(url.format(city, api_key))
        if response.status_code != 200:
            flash("The city doesn't exist!")
            return redirect('/')
        response = response.json()
        city_name = response['name']
        celsius = round(float(response['main']['temp']) - 273.15)
        weather = response['weather'][0]['description']
        dict_with_weather_info.update({city_name: [weather, celsius]})
        new_city = City(name=city_name)

        try:
            db.session.add(new_city)
            db.session.commit()
        except exc.IntegrityError:
            flash("The city has already been added to the list!")

    return render_template('template_name.html', weather=dict_with_weather_info)


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    delete_city = City.query.filter_by(name=city_id).first()
    dict_with_weather_info.pop(delete_city.name)

    db.session.delete(delete_city)
    db.session.commit()
    return render_template('template_name.html', weather=dict_with_weather_info)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run(debug=True)
