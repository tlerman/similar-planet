import json

from flask import Flask, render_template
import altair as alt
from flask import request

from utils import fetch_and_preproccess_data, plot_demographic_pyramid, get_demographic_data, get_correlation_df

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def show_chart():
    # selected_country = request.args.get('selected_country', default='Israel')
    # Load the dataset (here, we use an example dataset)
    data = fetch_and_preproccess_data()
    selected_country = request.args.get('selected_country', default='Israel') # Default selection or use request.args.get for initial GET requests with parameters

    countries = set(data['Country'].to_list())
    #selected_country = list(countries)[0]

    correlation_matrix = get_correlation_df(data)
    most_similar_countries = correlation_matrix[selected_country].sort_values(ascending=False)[1:4].index

    age_groups, male_population, female_population, male_percent, female_percent = get_demographic_data(data, selected_country)
    main_chart = plot_demographic_pyramid(age_groups, male_percent, [-1 * x for x in female_percent], selected_country=selected_country,
                                     type='most_similar_countries').encode().properties(
    width=500,  # Set the desired width
    height=800,  # Adjust height as needed
    title=f'Demographic Pyramid for {selected_country}'
    )


    title_chart = alt.Chart({'values': [{}]}).mark_text(
        align='center',
        baseline='middle',
        text='Similar Countries',
        fontSize=20  # Adjust the font size as needed
    ).properties(
        width=900,  # Match the width of your other charts
        height=60  # Adjust the height as needed to accommodate your title
    )

    similar_countries_charts = []
    for similar_country in most_similar_countries:
        age_groups, male_population, female_population, male_percent, female_percent = get_demographic_data(data, similar_country)
        similar_country_chart = plot_demographic_pyramid(age_groups, male_percent, [-1 * x for x in female_percent], selected_country=similar_country,
                                         type='most_similar_countries').encode().properties(
        width=300,  # Set the desired width
        height=150,  # Adjust height as needed
        title=f'{similar_country}'   # Set the desired height
        )

        similar_countries_charts.append(similar_country_chart)


    main_chart_json = main_chart.to_json()

    smaller_charts_row = alt.hconcat(
        similar_countries_charts[0],
        similar_countries_charts[1],
        similar_countries_charts[2]
        # Optionally, you can specify spacing or configure alignment here
    ).resolve_scale(
        # Adjust scale resolution as needed
        x='independent', y='independent'
    )

    # Concatenate the main chart with the smaller charts
    final_chart = alt.vconcat(
        main_chart,  # The main chart
        title_chart,
        smaller_charts_row,  # The row of smaller charts
        spacing=5
        # Optionally, specify spacing or configure alignment here
    ).resolve_scale(
        # Adjust scale resolution as needed
        x='independent', y='independent'
    ).configure_axisX(grid=False).configure_view(
    strokeWidth=0  # Removes the chart border
)

    final_chart_dict = final_chart.to_dict()
    # Specify the background color in the config
    if 'config' in final_chart_dict:
        final_chart_dict['config']['background'] = '#87CEEB'
    else:
        final_chart_dict['config'] = {'background': '#87CEEB'}

    chart_json = json.dumps(final_chart_dict)
    # source = data.countries()
    # Convert the modified JSON back to a string if necessary
    chart_json_str = json.dumps(chart_json)

    # Filter or manipulate your data as needed
    # For this example, we'll assume the data is ready to go

    return render_template('chart.html', title='Demographic Pyramid', chart_json=chart_json, vega_version=alt.VEGA_VERSION,
                           vegalite_version=alt.VEGALITE_VERSION, vegaembed_version=alt.VEGAEMBED_VERSION, countries=countries,
                           selected_country=selected_country)


if __name__ == '__main__':
    app.run(debug=True)
