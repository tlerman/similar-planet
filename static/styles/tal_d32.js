// Function to update or initialize the demographic chart
function updateChart(data) {
    console.log(data); // Log the fetched data for verification

    // Clear any existing content in the chart element
    d3.select("#chart").selectAll("*").remove();

    const margin = {top: 20, right: 100, bottom: 30, left: 90},
          width = 960 - margin.left - margin.right,
          height = 500 - margin.top - margin.bottom;

    // Define number format with commas
    const formatNumber = d3.format(",");

    // Set up the SVG container
    const svg = d3.select("#chart").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // Create scales
    const xScale = d3.scaleLinear().range([0, width / 2]);
    const yScale = d3.scaleBand().range([height, 0]).padding(0.1);

    // Update scales with the data
    xScale.domain([0, d3.max([...data.male_percent, ...data.female_percent])]);
    yScale.domain(data.age_groups);

    svg.append("g")
       .attr("transform", "translate(-30,0)")
       .call(d3.axisLeft(yScale));

    // General function to draw bars for both male and female data
    const drawBars = (gender, percentData, populationData, color) => {
        svg.selectAll(`.bar.${gender}`)
            .data(percentData)
            .enter().append("rect")
            .attr("class", `bar ${gender}`)
            .attr("x", d => gender === 'male' ? width / 2 : width / 2 - xScale(d))
            .attr("y", (d, i) => yScale(data.age_groups[i]))
            .attr("width", d => xScale(d))
            .attr("height", yScale.bandwidth())
            .attr("fill", color)
            .on("mouseover", function(event, d) {
                d3.select(this).style("opacity", 0.5);
                // Additional tooltip logic can be added here
            })
            .on("mouseout", function() {
                d3.select(this).style("opacity", 1);
                // Hide tooltip logic can be added here
            });

        // Add text labels for percentages here if needed
    };

    // Draw bars for male and female data
    drawBars('male', data.male_percent, data.male_population, 'blue');
    drawBars('female', data.female_percent, data.female_population, 'pink');
}

document.addEventListener('DOMContentLoaded', function() {
    // Fetch the list of countries from the Flask app
    d3.json('/').then(function(data) {
        const select = d3.select('#country-select');

        // Populate the dropdown with countries
        data.countries.forEach(function(country) {
            select.append('option').text(country).attr('value', country);
        });

        // Fetch and display initial chart data for the default or first country
        fetch(`/data?selected_country=${data.countries[0]}`)
            .then(response => response.json())
            .then(data => updateChart(data))
            .catch(error => console.error('Error fetching data:', error));
    });

    // Event listener for when a new country is selected
    document.getElementById('country-select').addEventListener('change', function() {
        var selectedCountry = this.value;
        // Fetch and update the chart for the selected country
        fetch(`/data?selected_country=${selectedCountry}`)
            .then(response => response.json())
            .then(data => updateChart(data))
            .catch(error => console.error('Error fetching data:', error));
    });
});
