import pandas as pd
from flask import Flask, render_template, request, jsonify

from utils import get_demographic_data, get_correlation_df

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


@app.route('/api/countries')
def api_data():
    data = fetch_and_preproccess_data()
    countries = sorted(data['Country'].unique().tolist())
    # You can include more data preprocessing here if needed
    return jsonify({"countries": countries})


@app.route('/data/<selected_country>')
def serve_data(selected_country):
    data = fetch_and_preproccess_data()
    try:
        correlation_df = get_correlation_df(data)
    except KeyError:
        return jsonify({'error': 'Country not found'}), 404

    # selected_country = request.args.get('selected_country', 'Israel')


    correlation_df[selected_country].sort_values()
    sorted_series = correlation_df[selected_country].sort_values()
    chosen_country = sorted_series.index[-1]
    similar_country_1 = sorted_series.index[-2]
    similar_country_2 = sorted_series.index[-3]
    similar_country_3 = sorted_series.index[-4]

    res = []
    for country in [chosen_country, similar_country_1, similar_country_2, similar_country_3]:
        age_groups, male_population, female_population, male_percent, female_percent = get_demographic_data(data, country)
        data_to_send = {
            'age_groups': age_groups,
            'male_percent': male_percent,
            'female_percent': female_percent,
            'male_population': male_population,
            'female_population': female_population
        }
        res.append({'data': data_to_send, 'country_name': country})

    return jsonify(res)


if __name__ == '__main__':
    app.run(debug=True)
