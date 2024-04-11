import altair as alt
import numpy as np
import pandas as pd


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


def get_demographic_data(data, country='Israel'):
    age_groups = ['0 - 4', '5 - 9', '10 - 14', '15 - 19', '20 - 24', '25 - 29', '30 - 34', '35 - 39', '40 - 44', '45 - 49',
                  '50 - 54', '55 - 59', '60 - 64', '65 - 69', '70 - 74', '75 - 79', '80 - 84', '85 - 89', '90 - 94', '95 - 99', '100+']
    age_group_data = data[data['Age'].isin(age_groups)]
    age_group_data = age_group_data[age_group_data['Country'] == country]

    male_population = age_group_data[age_group_data['Sex'] == 'Male']['2020'].to_list()
    female_population = age_group_data[age_group_data['Sex'] == 'Female']['2020'].to_list()

    total_pop = sum(male_population + female_population)
    male_percent = [round(x / total_pop, 4) for x in male_population]
    female_percent = [round(x / total_pop, 4) for x in female_population]

    return age_groups, male_population, female_population, male_percent, female_percent


def plot_demographic_pyramid(age_groups, male_percent, female_percent, selected_country, type):
    df = pd.DataFrame({
        'Age Group': age_groups * 2,
        'Population': np.concatenate([[str(x) for x in male_percent], [str(x) for x in female_percent]]),
        'Gender': ['Male'] * len(age_groups) + ['Female'] * len(age_groups)
    })
    # df['Population'] = df.apply(lambda x: x[:4], axis=0)
    bar = alt.Chart(df).mark_bar().encode(
        y=alt.Y('Age Group:N', sort=age_groups, axis=alt.Axis(title='Age Group')),
        x=alt.X('Population:Q', title=selected_country, axis=alt.Axis(labels=False, ticks=False)),
        color=alt.Color('Gender:N', scale=alt.Scale(range=['#1f77b4', '#ff7f0e']), legend=alt.Legend(title=None)),
        text=alt.Text('Population:N', format='.1%'),  # Display percentage labels on the bars
        tooltip=[
            alt.Tooltip('Population:N', title='Population', format='.1%'),
            alt.Tooltip('Gender:N', title='Gender'),
            alt.Tooltip('Age Group:N', title='Age Group')
        ]
    )
    # Define the text layer for females with positive values
    text_female = bar.transform_filter(
        alt.datum.Gender == 'Female'
    ).transform_calculate(
        positive_population='abs(datum.Population)'  # Calculate the absolute value of the population
    ).mark_text(
        align='center',
        baseline='middle',
        dx=-15  # Position for females
    ).encode(
        text=alt.Text('positive_population:N', format='.1%')  # Use the calculated positive population
    )

    # Define the text layer for males
    text_male = bar.transform_filter(
        alt.datum.Gender == 'Male'
    ).mark_text(
        align='center',
        baseline='middle',
        dx=15  # Positive dx for males
    ).encode(
        text=alt.Text('Population:N', format='.1%')
    )

    # Combine the layers
    width = 800
    height = 400
    if type != 'selected_country':
        width = 200
        height = 130


    # Create a selection that triggers on hover
    hover = alt.selection_single(
        on='mouseover',  # Use mouseover event
        nearest=True,  # Select the nearest point to the mouse cursor
        empty='none',  # Keep the selection when the mouse moves away
        fields=['Age Group']  # Field to match for nearest
    )

    # Invisible points for capturing hover events
    points = bar.mark_point(
        filled=True,
        opacity=0  # Make points invisible
    ).encode(
        size=alt.value(100),  # Increase point size to make it easier to hover over
        tooltip=[alt.Tooltip('Age Group'), alt.Tooltip('Population:Q'), alt.Tooltip('Gender:N')]
    ).add_selection(
        hover
    )

    # Text overlay for displaying population on hover
    text = bar.mark_text(
        align='left',
        dx=5,  # Offset text to the right of the bar
        dy=0  # Align text vertically in the middle of the bar
    ).encode(
        text=alt.condition(hover, 'Population:Q', alt.value(' ')),  # Only show text if hovered
        opacity=alt.condition(hover, alt.value(1), alt.value(0))  # Make text visible on hover
    )

    # Combine layers
    chart = alt.layer(
        bar,  # Base bar chart
        points,  # For capturing hover events
        text  # Dynamic text overlay
    )


    #chart = alt.layer(bar, text_female, text_male).properties(width=width, height=height)

    return chart


def get_correlation_df(data):
    data2 = data[data['Sex'] == 'Both sexes']
    age_groups = ['0 - 4', '5 - 9', '10 - 14', '15 - 19', '20 - 24', '25 - 29', '30 - 34', '35 - 39', '40 - 44', '45 - 49',
                  '50 - 54', '55 - 59', '60 - 64', '65 - 69', '70 - 74', '75 - 79', '80 - 84', '85 - 89', '90 - 94', '95 - 99', '100+']
    age_group_data2 = data2[data2['Age'].isin(age_groups)]
    del age_group_data2['Sex']
    pivot_df = age_group_data2.pivot(index='Age', columns='Country', values='2020')
    correlation_matrix = pivot_df.corr()

    return correlation_matrix


# Modify the sorting key function to handle '100+' or similar age groups
def sort_age_groups(age_group):
    # Check if age group ends with '+'
    if age_group.endswith('+'):
        # Assign a high value to ensure it sorts last; adjust as needed
        return 999
    else:
        # Convert the first part of the age group to an integer for sorting
        return int(age_group.split('-')[0])