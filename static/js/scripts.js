// JavaScript logic for live updates, chart rendering, and user interaction in the dashboard.

let combinedData = [];
let timeframe = "live";
let liveInterval;

const margin = { top: 20, right: 20, bottom: 30, left: 50 };

function getChartDimensions(container) {
    const containerWidth = document.querySelector(container).clientWidth;
    const containerHeight = document.querySelector(container).clientHeight;
    return {
        width: containerWidth - margin.left - margin.right,
        height: containerHeight - margin.top - margin.bottom,
    };
}

function setupTemperatureChart(container) {
    const { width, height } = getChartDimensions(container);
    d3.select(container).select('svg').remove();

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append('defs')
        .append('clipPath')
        .attr('id', 'clip-temperature')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${height})`);
    svg.append('g').attr('class', 'y-axis temperature-axis');
    svg.append('path').attr('class', 'line temperature-line').attr('clip-path', 'url(#clip-temperature)');
    svg.append('g').attr('class', 'grid');
    return { svg, width, height };
}

function setupHumidityChart(container) {
    const { width, height } = getChartDimensions(container);
    d3.select(container).select('svg').remove();

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append('defs')
        .append('clipPath')
        .attr('id', 'clip-humidity')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${height})`);
    svg.append('g').attr('class', 'y-axis humidity-axis');
    svg.append('path').attr('class', 'line humidity-line').attr('clip-path', 'url(#clip-humidity)');
    svg.append('g').attr('class', 'grid');
    return { svg, width, height };
}

function setupCO2Chart(container) {
    const { width, height } = getChartDimensions(container);
    d3.select(container).select('svg').remove();

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append('defs')
        .append('clipPath')
        .attr('id', 'clip-co2')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${height})`);
    svg.append('g').attr('class', 'y-axis co2-axis');
    svg.append('path').attr('class', 'line co2-line').attr('clip-path', 'url(#clip-co2)');
    svg.append('g').attr('class', 'grid');

    return { svg, width, height };
}

function setupThermocoupleChart(container) {
    const { width, height } = getChartDimensions(container);
    d3.select(container).select('svg').remove();

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    svg.append('defs')
        .append('clipPath')
        .attr('id', 'clip-thermocouple')
        .append('rect')
        .attr('width', width)
        .attr('height', height);

    svg.append('g').attr('class', 'x-axis').attr('transform', `translate(0,${height})`);
    svg.append('g').attr('class', 'y-axis thermocouple-axis');
    svg.append('path').attr('class', 'line thermocouple-line').attr('clip-path', 'url(#clip-thermocouple)');
    svg.append('g').attr('class', 'grid');

    return { svg, width, height };
}

let temperatureChart = setupTemperatureChart('#temperature-chart');
let humidityChart = setupHumidityChart('#humidity-chart');
let co2Chart = setupCO2Chart('#co2-chart');
let thermocoupleChart = setupThermocoupleChart('#thermocouple-chart');

function updateTemperatureChart(data) {
    const { svg, width, height } = temperatureChart;
    const now = new Date();
    const x = d3.scaleTime()
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60000 : (timeframe === "1day" ? 86400000 : 604800000))), now])
        .range([0, width]);

    const yTemp = d3.scaleLinear()
        .domain([d3.min(data, d => d.temperature) - 1, d3.max(data, d => d.temperature) + 1])
        .range([height, 0]);

    const temperatureLine = d3.line()
        .x(d => x(d.time))
        .y(d => yTemp(d.temperature));

    svg.select('.x-axis').call(d3.axisBottom(x));
    svg.select('.temperature-axis').call(d3.axisLeft(yTemp).ticks(5).tickFormat(d => `${d}°C`));
    svg.select('.temperature-line').datum(data).attr('d', temperatureLine).attr('stroke', 'steelblue');
    svg.select('.grid').call(d3.axisLeft(yTemp).tickSize(-width).tickFormat(''));
}

function updateHumidityChart(data) {
    const { svg, width, height } = humidityChart;
    const now = new Date();
    const x = d3.scaleTime()
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60000 : (timeframe === "1day" ? 86400000 : 604800000))), now])
        .range([0, width]);

    const yHumid = d3.scaleLinear()
        .domain([d3.min(data, d => d.humidity) - 5, d3.max(data, d => d.humidity) + 5])
        .range([height, 0]);

    const humidityLine = d3.line()
        .x(d => x(d.time))
        .y(d => yHumid(d.humidity));

    svg.select('.x-axis').call(d3.axisBottom(x));
    svg.select('.humidity-axis').call(d3.axisLeft(yHumid).ticks(5).tickFormat(d => `${d}%`));
    svg.select('.humidity-line').datum(data).attr('d', humidityLine).attr('stroke', 'rgb(255, 153, 0)');
    svg.select('.grid').call(d3.axisLeft(yHumid).tickSize(-width).tickFormat(''));
}

function updateCO2Chart(data) {
    const { svg, width, height } = co2Chart;
    const now = new Date();
    const x = d3.scaleTime()
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60000 : (timeframe === "1day" ? 86400000 : 604800000))), now])
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([d3.min(data, d => d.co2) - 50, d3.max(data, d => d.co2) + 50])
        .range([height, 0]);

    const line = d3.line()
        .x(d => x(d.time))
        .y(d => y(d.co2));

    svg.select('.x-axis').call(d3.axisBottom(x));
    svg.select('.co2-axis').call(d3.axisLeft(y).ticks(5).tickFormat(d => `${d} ppm`));
    svg.select('.co2-line').datum(data).attr('d', line).attr('stroke', 'rgb(175, 122, 161)');
    svg.select('.grid').call(d3.axisLeft(y).tickSize(-width).tickFormat(''));
}

function updateThermocoupleChart(data) {
    const { svg, width, height } = thermocoupleChart;
    const now = new Date();
    const x = d3.scaleTime()
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60000 : (timeframe === "1day" ? 86400000 : 604800000))), now])
        .range([0, width]);

    const validData = data.filter(d => d.thermocouple !== null);
    const y = d3.scaleLinear()
        .domain(validData.length > 0 ? [d3.min(validData, d => d.thermocouple) - 1, d3.max(validData, d => d.thermocouple) + 1] : [20, 30])
        .range([height, 0]);

    const line = d3.line()
        .x(d => x(d.time))
        .y(d => y(d.thermocouple))
        .defined(d => d.thermocouple !== null);

    svg.select('.x-axis').call(d3.axisBottom(x));
    svg.select('.thermocouple-axis').call(d3.axisLeft(y).ticks(5).tickFormat(d => `${d} °C`));
    svg.select('.thermocouple-line').datum(data).attr('d', line).attr('stroke', 'rgb(255, 99, 132)');
    svg.select('.grid').call(d3.axisLeft(y).tickSize(-width).tickFormat(''));
}


function fetchLiveSensorData() {
    fetch('/sensor_data')
        .then(response => response.json())
        .then(data => {
            const now = new Date();
            combinedData.push({
                time: now,
                temperature: parseFloat(data.temperature.toFixed(1)),
                humidity: parseFloat(data.humidity.toFixed(1)),
                co2: parseFloat(data.co2),
                thermocouple: data.thermocouple !== null ? parseFloat(data.thermocouple.toFixed(1)) : null
            });
            if (combinedData.length > 60) combinedData.shift();

            // Update top boxes
            document.getElementById('temperature-value').textContent = `${data.temperature.toFixed(1)} °C`;
            document.getElementById('humidity-value').textContent = `${data.humidity.toFixed(1)} %`;

            // Handle CO2 value persistence between reads
            if (!window.lastCO2Value) window.lastCO2Value = "--";
            if ('co2' in data && data.co2 !== null) {
                window.lastCO2Value = data.co2;
            }
            document.getElementById('co2-value').textContent = `${window.lastCO2Value} ppm`;

            // Handle thermocouple value
            if (!window.lastThermocoupleValue) window.lastThermocoupleValue = "--";
            if ('thermocouple' in data && data.thermocouple !== null) {
                window.lastThermocoupleValue = data.thermocouple.toFixed(1);
            }
            document.getElementById('thermocouple-value').textContent = `${window.lastThermocoupleValue} °C`;

            // Update live charts
            updateTemperatureChart(combinedData);
            updateHumidityChart(combinedData);
            updateCO2Chart(combinedData);
            updateThermocoupleChart(combinedData);
        })
        .catch(error => console.error('Error fetching live sensor data:', error));
}

function fetchHistoricalSensorData(endpoint) {
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const now = new Date();
            const intervalMs = 10000;  // Assumes 10-second logging interval
            const recordCount = data.temperature.length;

            combinedData = data.temperature.map((tempValue, i) => ({
                time: new Date(now.getTime() - (recordCount - i) * intervalMs),
                temperature: parseFloat(tempValue.toFixed(1)),
                humidity: parseFloat(data.humidity[i].toFixed(1)),
                co2: data.co2 && data.co2[i] !== null ? parseFloat(data.co2[i].toFixed(0)) : null,
                thermocouple: data.thermocouple && data.thermocouple[i] !== null ? parseFloat(data.thermocouple[i].toFixed(1)) : null
            }));

            // Update top boxes with placeholders
            document.getElementById('temperature-value').textContent = "-- °C";
            document.getElementById('humidity-value').textContent = "-- %";
            document.getElementById('co2-value').textContent = "-- ppm";
            document.getElementById('thermocouple-value').textContent = "-- °C";

            // Update charts
            updateTemperatureChart(combinedData);
            updateHumidityChart(combinedData);
            updateCO2Chart(combinedData);
            updateThermocoupleChart(combinedData);
        })
        .catch(error => console.error('Error fetching historical sensor data:', error));
}


function fetchRelayState() {
    fetch('/relay_state')
        .then(response => response.json())
        .then(data => {
            const relayState = data.relay_state === 0 ? "ON" : "OFF";
            document.getElementById('relay-state-value').textContent = relayState;
            const relayStateBox = document.getElementById('relay-state-box');
            relayStateBox.style.backgroundColor = relayState === "ON" ? "#4CAF50" : "#FF5733";
        })
        .catch(error => console.error('Error fetching relay state:', error));
}

let historicalInterval;

// Start or restart live top-box updates (every second)
function startLiveBoxUpdates() {
    clearInterval(liveInterval);
    liveInterval = setInterval(() => {
        fetchLiveSensorData(); // Updates top boxes and pushes to combinedData
        fetchRelayState();     // Also keep relay state updated
    }, 1000);
}

// Set up event listener for timeframe changes
document.getElementById('timeframe').addEventListener('change', function () {
    clearInterval(historicalInterval); // clear previous chart update timer
    timeframe = this.value;

    if (timeframe === "live") {
        combinedData = []; // Clear combinedData and restart it fresh to match live window
        startLiveBoxUpdates();              // restart live updates
    } else if (timeframe === "1day") {
        fetchHistoricalSensorData('/sensor_data/1day');
        historicalInterval = setInterval(() => {
            fetchHistoricalSensorData('/sensor_data/1day');
        }, 10000); // refresh chart every 10 sec
    } else if (timeframe === "7day") {
        fetchHistoricalSensorData('/sensor_data/7day');
        historicalInterval = setInterval(() => {
            fetchHistoricalSensorData('/sensor_data/7day');
        }, 10000); // refresh chart every 10 sec
    }
});

liveInterval = setInterval(fetchLiveSensorData, 1000);
setInterval(fetchRelayState, 2000);
startLiveBoxUpdates(); // Begin top box updates on load

let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        temperatureChart = setupTemperatureChart('#temperature-chart');
        humidityChart = setupHumidityChart('#humidity-chart');
        updateTemperatureChart(combinedData);
        updateHumidityChart(combinedData);
    }, 100);
});

document.addEventListener('DOMContentLoaded', () => {
    const settingsButton = document.getElementById('settings-button');
    const modal = document.getElementById('settings-modal');
    const closeModal = document.getElementById('close-modal');
    const saveSettingsButton = document.getElementById('save-settings');
    const humidifierOnInput = document.getElementById('humidifier-on');
    const humidifierOffInput = document.getElementById('humidifier-off');
    const debounceDelayInput = document.getElementById('debounce-delay');
    const sensorFailLimitInput = document.getElementById('sensor-fail-limit');

    settingsButton.addEventListener('click', () => {
        fetch('/config')
            .then(response => response.json())
            .then(config => {
                humidifierOnInput.value = config.lower;
                humidifierOffInput.value = config.upper;
                debounceDelayInput.value = config.debounce_delay;
                sensorFailLimitInput.value = config.sensor_fail_limit;

                // Set the correct toggle for mode
                document.getElementById(`mode-${config.mode.toLowerCase()}`).checked = true;
                document.getElementById('alert-threshold').value = config.alert_threshold || 15; //get alert threshold into settings modal (default to 15 sec if not set)
                document.getElementById('alert-cooldown').value = config.alert_cooldown; //get alert cooldown into settings modal

                modal.style.display = 'block';
            })
            .catch(error => console.error('Error fetching configuration:', error));
    });

    closeModal.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    saveSettingsButton.addEventListener('click', () => {
        const humidifierOn = parseFloat(humidifierOnInput.value);
        const humidifierOff = parseFloat(humidifierOffInput.value);
        const debounceDelay = parseFloat(debounceDelayInput.value);
        const sensorFailLimit = parseFloat(sensorFailLimitInput.value);
        const mode = document.querySelector('input[name="mode"]:checked').value;
        const alertThreshold = parseFloat(document.getElementById('alert-threshold').value);
        const alertCooldown = parseFloat(document.getElementById('alert-cooldown').value);

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

        if (isNaN(alertThreshold) || alertThreshold < 0) {
            alert('Alert threshold must be a positive number');
            return;
        }

        if (isNaN(alertCooldown) || alertCooldown < 1) {
            alert('Alert cooldown must be a positive number');
            return;
        }

        fetch('/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                lower: humidifierOn,
                upper: humidifierOff,
                debounce_delay: debounceDelay,
                sensor_fail_limit: sensorFailLimit,
                mode: mode,
                alert_threshold: alertThreshold,
                alert_cooldown: alertCooldown
            }),
        })
            .then(response => response.json())
            .then(data => {
                modal.style.display = 'none';
                showSnackbar("Settings saved");
            })
            .catch(error => {
                console.error('Error saving configuration:', error);
                alert('Failed to save settings. Please try again.');
            });
    });

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});

// Snackbar notification for settings saved pop up
function showSnackbar(message) {
    const snackbar = document.getElementById('snackbar');
    snackbar.textContent = message;
    snackbar.classList.add('show');

    setTimeout(() => {
        snackbar.classList.remove('show');
    }, 2000);
}
