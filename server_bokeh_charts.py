import json
from flask import Flask, render_template, request
from bokeh.embed import json_item
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.layouts import column
from utils import fetch_and_preproccess_data, get_demographic_data, get_correlation_df, sort_age_groups

app = Flask(__name__)


def plot_demographic_pyramid(age_groups, male_population, female_population, selected_country):
    """Generates a demographic pyramid using Bokeh."""

    # Sorting the age groups while keeping track of populations
    # Create a list of tuples (age_group, male_population, female_population)
    combined = list(zip(age_groups, male_population, female_population))

    # Sort by age group
    sorted_combined = sorted(combined, key=lambda x: sort_age_groups(x[0]))

    # Unpack the sorted tuples back into separate lists
    age_groups_sorted, male_population_sorted, female_population_sorted = zip(*sorted_combined)

    male_population_inverted = [-x for x in male_population_sorted]
    data = {'age_groups': age_groups, 'male_population': male_population, 'female_population': female_population}
    source = ColumnDataSource(data=dict(age_groups=age_groups_sorted, male_population=male_population_inverted, female_population=female_population_sorted))

    #male_population_inverted = [-x for x in male_population]
    #source = ColumnDataSource(data=dict(age_groups=age_groups, male_population=male_population_inverted, female_population=female_population))

    p = figure(y_range=FactorRange(*age_groups_sorted), height=250, title="Population Pyramid",
               toolbar_location=None, tools="")

    # Invert the axis and axis labels to make the pyramid vertical
    p.hbar(right='male_population', y='age_groups', height=0.8, source=source, color="blue")
    p.hbar(right='female_population', y='age_groups', height=0.8, source=source, color="pink")

    p.y_range.range_padding = 0.1
    p.ygrid.grid_line_color = None
    p.axis.minor_tick_line_color = None
    p.outline_line_color = None
    p.legend.location = "top_right"
    p.legend.orientation = "horizontal"

    # Add a central axis line if desired
    p.line(x=[0, 0], y=[-0.5, len(age_groups_sorted) - 0.5], line_width=2)

    return p


@app.route('/', methods=['GET', 'POST'])
def show_chart():
    data = fetch_and_preproccess_data()
    selected_country = request.args.get('selected_country', default='Israel')

    countries = set(data['Country'].to_list())

    correlation_matrix = get_correlation_df(data)
    most_similar_countries = correlation_matrix[selected_country].sort_values(ascending=False)[1:4].index

    age_groups, male_population, female_population, male_percent, female_percent = get_demographic_data(data, selected_country)
    main_chart = plot_demographic_pyramid(age_groups, male_population, female_population, selected_country)

    similar_countries_charts = []
    for similar_country in most_similar_countries:
        age_groups, male_population, female_population, _, _ = get_demographic_data(data, similar_country)
        similar_country_chart = plot_demographic_pyramid(age_groups, male_population, female_population, similar_country)
        similar_countries_charts.append(similar_country_chart)

    # Use Bokeh's layout functions to arrange your charts, e.g., column or row layouts
    final_layout = column(main_chart, *similar_countries_charts)
    final_chart_json = json.dumps(json_item(final_layout, "myplot"))

    return render_template('charts_d3j.html', chart_json=final_chart_json, countries=countries, selected_country=selected_country)


if __name__ == '__main__':
    app.run(debug=True)
