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

let temperatureChart = setupTemperatureChart('#temperature-chart');
let humidityChart = setupHumidityChart('#humidity-chart');

function updateTemperatureChart(data) {
    const { svg, width, height } = temperatureChart;
    const now = new Date();
    const x = d3.scaleTime()
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60 * 1000 : (timeframe === "1day" ? 24 * 60 * 60 * 1000 : 7 * 24 * 60 * 60 * 1000))), now])
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
        .domain([new Date(now.getTime() - (timeframe === "live" ? 60 * 1000 : (timeframe === "1day" ? 24 * 60 * 60 * 1000 : 7 * 24 * 60 * 60 * 1000))), now])
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

function fetchLiveSensorData() {
    fetch('/sensor_data')
        .then(response => response.json())
        .then(data => {
            const now = new Date();
            combinedData.push({
                time: now,
                temperature: parseFloat(data.temperature.toFixed(1)),
                humidity: parseFloat(data.humidity.toFixed(1))
            });
            if (combinedData.length > 60) combinedData.shift();

            document.getElementById('temperature-value').textContent = `${data.temperature.toFixed(1)} °C`;
            document.getElementById('humidity-value').textContent = `${data.humidity.toFixed(1)} %`;
            updateTemperatureChart(combinedData);
            updateHumidityChart(combinedData);
        })
        .catch(error => console.error('Error fetching live sensor data:', error));
}

function fetchHistoricalSensorData(endpoint) {
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            const now = new Date();
            combinedData = data.temperature.map((tempValue, i) => ({
                time: new Date(now.getTime() - (data.temperature.length - i) * 10000),
                temperature: parseFloat(tempValue.toFixed(1)),
                humidity: parseFloat(data.humidity[i].toFixed(1))
            }));

            document.getElementById('temperature-value').textContent = "-- °C";
            document.getElementById('humidity-value').textContent = "-- %";
            updateTemperatureChart(combinedData);
            updateHumidityChart(combinedData);
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

document.getElementById('timeframe').addEventListener('change', function () {
    clearInterval(liveInterval);
    timeframe = this.value;

    if (timeframe === "live") {
        liveInterval = setInterval(fetchLiveSensorData, 1000);
    } else if (timeframe === "1day") {
        fetchHistoricalSensorData('/sensor_data/1day');
    } else if (timeframe === "7day") {
        fetchHistoricalSensorData('/sensor_data/7day');
    }
});

liveInterval = setInterval(fetchLiveSensorData, 1000);
setInterval(fetchRelayState, 2000);

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
                mode: mode
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

    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});
