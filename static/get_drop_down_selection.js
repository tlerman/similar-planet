document.getElementById('country-select').addEventListener('change', function() {
    var selectedCountry = this.value;
    // Fetch the data for the selected country
    fetch(`/data?selected_country=${selectedCountry}`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            // Call a function to update your D3.js chart with this new data
            // updateChart(data);
        })
        .catch(error => console.error('Error fetching data:', error));
});

