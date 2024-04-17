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