let combinedData = [];
let timeframe = "live";
let liveInterval;

const margin = { top: 20, right: 60, bottom: 30, left: 50 };
const getChartWidth = () => Math.min(window.innerWidth - margin.left - margin.right, 800);
const height = 300 - margin.top - margin.bottom;

// Setup temperature chart
function setupTemperatureChart(container) {
    const svg = d3.select(container)
        .append('svg')
        .attr('viewBox', `0 0 ${getChartWidth() + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        //.attr('preserveAspectRatio', 'xMidYMid meet')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append('defs')
        .append('clipPath')
        .attr('id', 'clip-temperature')
        .append('rect')
        .attr('width', getChartWidth())
        .attr('height', height);

    svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${height})`);
    svg.append('g').attr('class', 'y-axis temperature-axis');
    svg.append('path').attr('class', 'line temperature-line').attr('clip-path', 'url(#clip-temperature)');
    svg.append('g').attr('class', 'grid');
    return svg;
}

// Setup humidity chart
function setupHumidityChart(container) {
    const svg = d3.select(container)
        .append('svg')
        .attr('viewBox', `0 0 ${getChartWidth() + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        //.attr('preserveAspectRatio', 'xMidYMid meet')
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append('defs')
        .append('clipPath')
        .attr('id', 'clip-humidity')
        .append('rect')
        .attr('width', getChartWidth())
        .attr('height', height);

    svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${height})`);
    svg.append('g').attr('class', 'y-axis humidity-axis');
    svg.append('path').attr('class', 'line humidity-line').attr('clip-path', 'url(#clip-humidity)');
    svg.append('g').attr('class', 'grid');
    return svg;
}

const temperatureChart = setupTemperatureChart('#temperature-chart');
const humidityChart = setupHumidityChart('#humidity-chart');

// Update temperature chart
function updateTemperatureChart(data) {
    const svg = d3.select('#temperature-chart svg g');
    const width = getChartWidth();
    const now = new Date();

    // Scales
    const x = d3.scaleTime()
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60 * 1000 : (timeframe === "1day" ? 24 * 60 * 60 * 1000 : 7 * 24 * 60 * 60 * 1000))), now])
        .range([0, width]);

    const yTemp = d3.scaleLinear()
        .domain([d3.min(data, d => d.temperature) - 1, d3.max(data, d => d.temperature) + 1])
        .range([height, 0]);

    // Line
    const temperatureLine = d3.line()
        .x(d => x(d.time))
        .y(d => yTemp(d.temperature));

    // Update axes
    svg.select('.x-axis').call(d3.axisBottom(x));
    svg.select('.temperature-axis').call(d3.axisLeft(yTemp).ticks(5).tickFormat(d => `${d}°C`));

    // Update line
    svg.select('.temperature-line')
        .datum(data)
        .attr('d', temperatureLine)
        .attr('stroke', 'steelblue');

    // Update grid lines
    svg.select('.grid')
        .call(d3.axisLeft(yTemp).tickSize(-width).tickFormat(''));
}

// Update humidity chart
function updateHumidityChart(data) {
    const svg = d3.select('#humidity-chart svg g');
    const width = getChartWidth();
    const now = new Date();

    // Scales
    const x = d3.scaleTime()
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60 * 1000 : (timeframe === "1day" ? 24 * 60 * 60 * 1000 : 7 * 24 * 60 * 60 * 1000))), now])
        .range([0, width]);

    const yHumid = d3.scaleLinear()
        .domain([d3.min(data, d => d.humidity) - 5, d3.max(data, d => d.humidity) + 5])
        .range([height, 0]);

    // Line
    const humidityLine = d3.line()
        .x(d => x(d.time))
        .y(d => yHumid(d.humidity));

    // Update axes
    svg.select('.x-axis').call(d3.axisBottom(x));
    svg.select('.humidity-axis').call(d3.axisLeft(yHumid).ticks(5).tickFormat(d => `${d}%`));

    // Update line
    svg.select('.humidity-line')
        .datum(data)
        .attr('d', humidityLine)
        .attr('stroke', 'rgb(255, 153, 0)');

    // Update grid lines
    svg.select('.grid')
        .call(d3.axisLeft(yHumid).tickSize(-width).tickFormat(''));
}

// Fetch live sensor data and update charts
function fetchLiveSensorData() {
    fetch('/sensor_data')
        .then(response => response.json())
        .then(data => {
            const now = new Date();

            // Add live data to combinedData array
            combinedData.push({
                time: now,
                temperature: parseFloat(data.temperature.toFixed(1)),
                humidity: parseFloat(data.humidity.toFixed(1))
            });

            // Limit data length
            if (combinedData.length > 60) combinedData.shift();

            // Update the top boxes
            document.getElementById('temperature-value').textContent = `${data.temperature.toFixed(1)} °C`;
            document.getElementById('humidity-value').textContent = `${data.humidity.toFixed(1)} %`;

            // Update the charts
            updateTemperatureChart(combinedData);
            updateHumidityChart(combinedData);
        })
        .catch(error => console.error('Error fetching live sensor data:', error));
}

// Fetch historical sensor data and update charts
function fetchHistoricalSensorData(endpoint) {
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const now = new Date();

            // Map combined data
            combinedData = data.temperature.map((tempValue, i) => ({
                time: new Date(now.getTime() - (data.temperature.length - i) * 10000),
                temperature: parseFloat(tempValue.toFixed(1)),
                humidity: parseFloat(data.humidity[i].toFixed(1))
            }));

            // Reset the top boxes
            document.getElementById('temperature-value').textContent = "-- °C";
            document.getElementById('humidity-value').textContent = "-- %";

            // Update the charts
            updateTemperatureChart(combinedData);
            updateHumidityChart(combinedData);
        })
        .catch(error => console.error('Error fetching historical sensor data:', error));
}

// Fetch relay state and update the humidifier state box
function fetchRelayState() {
    fetch('/relay_state')
        .then(response => response.json())
        .then(data => {
            const relayState = data.relay_state === 0 ? "ON" : "OFF";
            document.getElementById('relay-state-value').textContent = relayState;

            // Update the box color based on the relay state
            const relayStateBox = document.getElementById('relay-state-box');
            if (relayState === "ON") {
                relayStateBox.style.backgroundColor = "#4CAF50"; // Green for ON
            } else {
                relayStateBox.style.backgroundColor = "#FF5733"; // Red for OFF
            }
        })
        .catch(error => console.error('Error fetching relay state:', error));
}

// Timeframe change listener
document.getElementById('timeframe').addEventListener('change', function () {
    clearInterval(liveInterval); // Stop live interval when switching to historical

    timeframe = this.value;

    if (timeframe === "live") {
        liveInterval = setInterval(fetchLiveSensorData, 1000);
    } else if (timeframe === "1day") {
        fetchHistoricalSensorData('/sensor_data/1day');
    } else if (timeframe === "7day") {
        fetchHistoricalSensorData('/sensor_data/7day');
    }
});

// Initial live data fetch and update
liveInterval = setInterval(fetchLiveSensorData, 1000);

// Fetch relay state every 2 seconds
setInterval(fetchRelayState, 2000);

// Resize listener to update charts on window resize
window.addEventListener('resize', () => {
    updateTemperatureChart(combinedData);
    updateHumidityChart(combinedData);
});

// Settings modal functionality
document.addEventListener('DOMContentLoaded', () => {
    const settingsButton = document.getElementById('settings-button');
    const modal = document.getElementById('settings-modal');
    const closeModal = document.getElementById('close-modal');
    const saveSettingsButton = document.getElementById('save-settings');
    const humidifierOnInput = document.getElementById('humidifier-on');
    const humidifierOffInput = document.getElementById('humidifier-off');
    const debounceDelayInput = document.getElementById('debounce-delay');
    const sensorFailLimitInput = document.getElementById('sensor-fail-limit');

    // Show the settings modal and load current configuration
    settingsButton.addEventListener('click', () => {
        fetch('/config')
            .then(response => response.json())
            .then(config => {
                humidifierOnInput.value = config.lower;
                humidifierOffInput.value = config.upper;
                debounceDelayInput.value = config.debounce_delay;
                sensorFailLimitInput.value = config.sensor_fail_limit;
                modal.style.display = 'block';
            })
            .catch(error => console.error('Error fetching configuration:', error));
    });

    // Close the settings modal
    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Save settings and validate inputs
    saveSettingsButton.addEventListener('click', () => {
        const humidifierOn = parseFloat(humidifierOnInput.value);
        const humidifierOff = parseFloat(humidifierOffInput.value);
        const debounceDelay = parseFloat(debounceDelayInput.value);
        const sensorFailLimit = parseFloat(sensorFailLimitInput.value);

        if (isNaN(humidifierOn) || isNaN(humidifierOff) || isNaN(debounceDelay) || isNaN(sensorFailLimit)) {
            alert('All inputs must be numeric');
            return;
        }

        if (humidifierOn >= humidifierOff) {
            alert('Lower threshold must be below upper threshold');
            return;
        }

        if (debounceDelay < 0 || sensorFailLimit < 0) {
            alert('Debounce delay and sensor fail limit must be positive numbers');
            return;
        }

        // Send updated configuration to the backend
        fetch('/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lower: humidifierOn,
                upper: humidifierOff,
                debounce_delay: debounceDelay,
                sensor_fail_limit: sensorFailLimit
            }),
        })
            .then(response => response.json())
            .then(data => {
                alert('Settings saved successfully!');
                modal.style.display = 'none';
            })
            .catch(error => {
                console.error('Error saving configuration:', error);
                alert('Failed to save settings. Please try again.');
            });
    });

    // Close modal if user clicks outside of content
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});