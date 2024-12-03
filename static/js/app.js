// Initialize constants for DOM elements
const temperatureBox = document.getElementById('temperature-value');
const humidityBox = document.getElementById('humidity-value');
const timeframeDropdown = document.getElementById('timeframe');
const settingsButton = document.getElementById('settings-button');
const popupOverlay = document.getElementById('popup-overlay');
const settingsPopup = document.getElementById('settings-popup');
const saveButton = document.getElementById('save-settings');
const cancelButton = document.getElementById('cancel-settings');

// Live Data Arrays
let liveTemperatureData = [];
let liveHumidityData = [];

// Interval for live data
let liveInterval;

// Chart rendering logic
function renderChart(data) {
    const svg = d3.select('svg');
    svg.selectAll('*').remove(); // Clear existing content

    const width = 800;
    const height = 400;

    const xScale = d3.scaleTime()
        .domain([d3.min(data, d => d.time), d3.max(data, d => d.time)]) // Time scale
        .range([0, width]);

    const yScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value)]) // Y scale based on data values
        .range([height, 0]);

    const line = d3.line()
        .x(d => xScale(d.time)) // Map time to x-axis
        .y(d => yScale(d.value)) // Map value to y-axis
        .curve(d3.curveMonotoneX); // Smooth curve

    svg.append('path')
        .datum(data)
        .attr('d', line)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 2);

    // Add X and Y axes
    svg.append('g')
        .attr('transform', `translate(0, ${height})`)
        .call(d3.axisBottom(xScale)); // Bottom axis for time

    svg.append('g')
        .call(d3.axisLeft(yScale)); // Left axis for value
}

// Handle popup display
function showPopup() {
    popupOverlay.style.display = 'block';
    settingsPopup.style.display = 'block';
}

function hidePopup() {
    popupOverlay.style.display = 'none';
    settingsPopup.style.display = 'none';
}

// Handle settings save
async function saveSettings() {
    const humidifierOn = parseFloat(document.getElementById('humidifier-on').value);
    const humidifierOff = parseFloat(document.getElementById('humidifier-off').value);

    if (isNaN(humidifierOn) || isNaN(humidifierOff)) {
        alert('Input must be numeric');
        return;
    }

    if (humidifierOn >= humidifierOff) {
        alert('Lower threshold must be below upper threshold');
        return;
    }

    try {
        const response = await fetch('/update_thresholds', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lower: humidifierOn,
                upper: humidifierOff,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            alert('Settings saved successfully!');
            hidePopup();
        } else {
            alert(`Error: ${data.error}`);
        }
    } catch (error) {
        alert('Failed to save settings. Please try again.');
    }
}

// Fetch live sensor data
function fetchLiveSensorData() {
    fetch('/sensor_data')
        .then(response => response.json())
        .then(data => {
            const now = new Date();
            
            // Update live data arrays
            const temperatureData = {
                time: now,
                value: parseFloat(data.temperature)
            };
            const humidityData = {
                time: now,
                value: parseFloat(data.humidity)
            };
            
            // Update temperature and humidity displayed values
            temperatureBox.textContent = `${data.temperature} °C`;
            humidityBox.textContent = `${data.humidity} %`;

            // Assuming we are appending data to arrays:
            liveTemperatureData.push(temperatureData);
            liveHumidityData.push(humidityData);

            // Limit the arrays to the last 60 entries for live data
            if (liveTemperatureData.length > 60) liveTemperatureData.shift();
            if (liveHumidityData.length > 60) liveHumidityData.shift();

            // Render the chart with updated data
            renderChart(liveTemperatureData); // For temperature chart
            renderChart(liveHumidityData); // For humidity chart
        })
        .catch(error => console.error('Error fetching live sensor data:', error));
}

// Fetch historical sensor data
function fetchHistoricalSensorData(endpoint) {
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const now = new Date();
            
            // Assuming the server sends data with timestamp
            const temperatureData = data.temperature.map((value, i) => ({
                time: new Date(now.getTime() - (data.temperature.length - i) * 10000), // Adjust time logic
                value: value
            }));
            
            const humidityData = data.humidity.map((value, i) => ({
                time: new Date(now.getTime() - (data.humidity.length - i) * 10000),
                value: value
            }));

            // Render historical data
            renderChart(temperatureData); // Temperature chart
            renderChart(humidityData); // Humidity chart
        })
        .catch(error => console.error('Error fetching historical sensor data:', error));
}

// Handle timeframe change
timeframeDropdown.addEventListener('change', function () {
    const timeframe = this.value;
    clearInterval(liveInterval); // Stop live data interval
    
    if (timeframe === "live") {
        liveInterval = setInterval(fetchLiveSensorData, 1000); // Fetch live data every second
    } else if (timeframe === "1day") {
        fetchHistoricalSensorData('/sensor_data/1day'); // Fetch data for 1 day
    } else if (timeframe === "7day") {
        fetchHistoricalSensorData('/sensor_data/7day'); // Fetch data for 7 days
    }
});

// Event listeners for popup
settingsButton.addEventListener('click', showPopup);
popupOverlay.addEventListener('click', hidePopup);
cancelButton.addEventListener('click', hidePopup);
saveButton.addEventListener('click', saveSettings);

// Start fetching live data by default
liveInterval = setInterval(fetchLiveSensorData, 1000); // Fetch live data every second
