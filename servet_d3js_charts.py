import altair as alt
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

from utils import get_demographic_data

app = Flask(__name__)


def fetch_and_preproccess_data():
    data = pd.read_csv(f"5_year_age_groups.csv")
    data.replace('..', '0', inplace=True)
    data['2020'] = data['2020'].astype(int)
    age_groups = ['0 - 4', '5 - 9', '10 - 14', '15 - 19', '20 - 24', '25 - 29', '30 - 34', '35 - 39', '40 - 44', '45 - 49',
                  '50 - 54', '55 - 59', '60 - 64', '65 - 69', '70 - 74', '75 - 79', '80 - 84', '85 - 89', '90 - 94', '95 - 99', '100+']
    data = data[data['Age'].isin(age_groups)]
    grouped = data[['Country', '2020']].groupby('Country').sum().reset_index()
    empty_countries_list = grouped[grouped['2020'].astype(int) < 10]['Country'].tolist()
    data = data[~data['Country'].isin(empty_countries_list)]

    return data


@app.route('/')
def index():
    data = fetch_and_preproccess_data()
    countries = sorted(data['Country'].unique().tolist())
    return render_template('index.html', countries=countries)


@app.route('/data')
def serve_data():
    data = fetch_and_preproccess_data()
    selected_country = request.args.get('selected_country', 'Israel')
    age_groups, male_population, female_population, male_percent, female_percent = get_demographic_data(data, selected_country)
    data_to_send = {
        'age_groups': age_groups,
        'male_percent': male_percent,
        'female_percent': female_percent,
        'male_population': male_population,
        'female_population': female_population


    }
    return jsonify(data_to_send)


if __name__ == '__main__':
    app.run(debug=True)