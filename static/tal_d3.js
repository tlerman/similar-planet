// Function to update or initialize the demographic chart
 function createChart1(containerId, width, height, data) {
// function updateChart(data) {
    // Clear any existing content in the chart element
    d3.select(containerId).selectAll("*").remove();
    const margin = {top: 20, right: 100, bottom: 30, left: 90};
            // width = 960 - margin.left - margin.right,
            // height = 500 - margin.top - margin.bottom;

    // Define number format with commas
    const formatNumber = d3.format(",");

    // Set up the SVG container
    const svg = d3.select(containerId).append("svg")
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
            const bar = d3.select(this);
            bar.style("opacity", 0.7);
            // const gender = bar.attr("class").includes("male") ? "male" : "female";
            console.log("gender:", gender);
            // Get the index of the hovered element
            let i = d3.select(this.parentNode).selectAll('rect').nodes().indexOf(this);
            const tooltipText = `Population: ${formatNumber(populationData[i])}`;
            // Determine the x position for the tooltip based on the gender
            let tooltipX;
            if (gender === "male") {
                tooltipX = width / 2 + xScale(d) / 2; // Tooltip for males on the right side
            } else {
                tooltipX = width / 2 - xScale(d) / 2; // Tooltip for females on the left side
                i = i - data.age_groups.length;
            }

            console.log("Tooltip text:", tooltipText);
            // Log the entire population data array to check its contents
            console.log("Population data array:", populationData);
            console.log("i:", i);

                svg.append("text")
                    .attr("class", "tooltip")
                    .attr("x", tooltipX)
                    .attr("y", yScale(data.age_groups[i]) + yScale.bandwidth()/ 1.1 )
                    .attr("text-anchor", "middle")
                    .text(`${formatNumber(populationData[i])}`);
            })
            .on("mouseout", function() {
                d3.select(this).style("opacity", 0.5);
            });

        // Add text labels for percentages
    svg.selectAll(`.text.${gender}`)
        .data(percentData)
        .enter().append("text")
        .attr("class", `text ${gender}`)
        .attr("x", d => gender === 'male' ? width / 2 + xScale(d) + 5 : width / 2 - xScale(d) - 5)
        .attr("y", (d, i) => yScale(data.age_groups[i]) + yScale.bandwidth() / 2 + 5)
        .attr("text-anchor", d => gender === 'male' ? "start" : "end")
        .text(d => `${Math.round(d*100)}%`)
        .style("font-weight", "bold")
        .attr("fill", "#333")
        .attr("font-size", "12px");

        // Add text labels for percentages here if needed
    };

    // Draw bars for male and female data
    drawBars('male', data.male_percent, data.male_population, 'blue');
    drawBars('female', data.female_percent, data.female_population, 'orange');
}


function fetchAndUpdateCharts(selectedCountry) {
    if (!selectedCountry) {
        console.error('No country selected');
        return;  // Stop the function if no country is provided
    }
    fetch(`/data?selected_country=${encodeURIComponent(selectedCountry)}`)
        .then(response => response.json())
        .then(data => {
            // Update chart headers with the selected country name
            document.getElementById('chart-header').textContent = `${selectedCountry}`;

            // Update the charts with the fetched data
            createChart1("#main-chart", 960, 500, data);
            createChart1("#similar-chart1", 460, 250, data); // Assuming you want the same data in a smaller format
        })
        .catch(error => console.error('Error fetching data for:', selectedCountry, error));
}

document.addEventListener('DOMContentLoaded', function() {
    d3.json('/api/countries').then(function(data) {
        const select = d3.select('#country-select');

        // Populate the dropdown with countries
        data.countries.forEach(function(country) {
            select.append('option').text(country).attr('value', country);
        });

        // Automatically load data for the first country in the list, if available
        if (data.countries.length > 0) {
            const randomIndex = Math.floor(Math.random() * data.countries.length);  // Generate a random index
            fetchAndUpdateCharts(data.countries[randomIndex]);
        } else {
            console.log('No countries found.');
        }
    }).catch(error => {
        console.error('Error fetching country list:', error);
    });

    // Setup event listener for country selection changes
    document.getElementById('country-select').addEventListener('change', function() {
        fetchAndUpdateCharts(this.value);
    });
});
