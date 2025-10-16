// Global variables
let tripData = [];
let filteredData = [];
let currentPage = 1;
let rowsPerPage = 10;
let sortCol = -1;
let sortAsc = true;
let anomalyFlags = {}; // Store anomaly detection results

// Initialize when page loads
window.onload = function () {
    loadData();
};

// Load data (replace with actual API call)
function loadData() {
    // Generate sample data - REPLACE THIS with fetch() to your backend API
    tripData = generateSampleTrips();
    filteredData = tripData;
    updateAll();
}


// Generate sample data
function generateSampleTrips() {
    let trips = [];
    let dates = ['2024-01-15', '2024-01-16', '2024-01-17', '2024-01-18'];

    for (let i = 0; i < 150; i++) {
        let dist = Math.random() * 25 + 0.3;
        let dur = Math.random() * 50 + 3;
        let fare = Math.random() * 60 + 3;
        let speed = (dist / (dur / 60));
        let pass = Math.floor(Math.random() * 5) + 1;
        let date = dates[Math.floor(Math.random() * dates.length)];
        let hour = Math.floor(Math.random() * 24);
        let min = Math.floor(Math.random() * 60);

        // Add some anomalies intentionally
        if (i % 20 === 0) {
            fare = Math.random() * 200 + 100; // Very high fare
        }
        if (i % 25 === 0) {
            speed = Math.random() * 100 + 120; // Impossible speed
        }

        trips.push({
            id: 'T' + (1000 + i),
            time: date + ' ' + String(hour).padStart(2, '0') + ':' + String(min).padStart(2, '0'),
            distance: parseFloat(dist.toFixed(2)),
            duration: parseFloat(dur.toFixed(1)),
            fare: parseFloat(fare.toFixed(2)),
            speed: parseFloat(speed.toFixed(2)),
            passengers: pass
        });
    }
    return trips;
}

/* ============================================
   CUSTOM ANOMALY DETECTION ALGORITHM
   ============================================
   This is a manual implementation without using
   built-in functions like sort(), filter(), etc.
   
   Algorithm: IQR (Interquartile Range) Method
   - Manually sort data
   - Calculate Q1 (25th percentile) and Q3 (75th percentile)
   - Calculate IQR = Q3 - Q1
   - Identify outliers as values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
   
   Time Complexity: O(n²) for bubble sort + O(n) for detection = O(n²)
   Space Complexity: O(n) for storing sorted arrays
============================================ */

function runAnomalyDetection() {
    let startTime = performance.now();

    // Detect anomalies in fare
    let fareAnomalies = detectOutliers(tripData, 'fare');

    // Detect anomalies in speed
    let speedAnomalies = detectOutliers(tripData, 'speed');

    // Detect anomalies in fare per km ratio
    let fareRatioAnomalies = detectFareRatioAnomalies(tripData);

    // Combine all anomalies (remove duplicates manually)
    let allAnomalies = combineAnomalies(fareAnomalies, speedAnomalies, fareRatioAnomalies);

    let endTime = performance.now();
    let executionTime = (endTime - startTime).toFixed(2);

    // Update UI
    document.getElementById('anomalyCount').textContent = allAnomalies.length;
    document.getElementById('totalAnalyzed').textContent = tripData.length;

    displayAnomalies(allAnomalies, executionTime);

    // Mark anomalies in global data
    anomalyFlags = {};
    for (let i = 0; i < allAnomalies.length; i++) {
        anomalyFlags[allAnomalies[i].trip.id] = allAnomalies[i];
    }

    updateTable();
}

// Manual outlier detection using IQR method
function detectOutliers(data, field) {
    // Step 1: Extract values manually
    let values = [];
    for (let i = 0; i < data.length; i++) {
        values[i] = data[i][field];
    }

    // Step 2: Manual Bubble Sort (no built-in sort!)
    let sortedValues = manualBubbleSort(values);

    // Step 3: Calculate Q1, Q3, IQR manually
    let n = sortedValues.length;
    let q1Index = Math.floor(n * 0.25);
    let q3Index = Math.floor(n * 0.75);
    let q1 = sortedValues[q1Index];
    let q3 = sortedValues[q3Index];
    let iqr = q3 - q1;

    // Step 4: Calculate bounds
    let lowerBound = q1 - 1.5 * iqr;
    let upperBound = q3 + 1.5 * iqr;

    // Step 5: Find outliers manually
    let outliers = [];
    for (let i = 0; i < data.length; i++) {
        if (data[i][field] < lowerBound || data[i][field] > upperBound) {
            outliers[outliers.length] = {
                trip: data[i],
                reason: field === 'fare' ?
                    'Unusual fare: $' + data[i][field].toFixed(2) + ' (normal range: $' + lowerBound.toFixed(2) + ' - $' + upperBound.toFixed(2) + ')' :
                    'Unusual speed: ' + data[i][field].toFixed(2) + ' km/h (normal range: ' + lowerBound.toFixed(2) + ' - ' + upperBound.toFixed(2) + ' km/h)',
                type: field
            };
        }
    }

    return outliers;
}

// Manual Bubble Sort implementation
function manualBubbleSort(arr) {
    let sorted = [];
    // Copy array manually
    for (let i = 0; i < arr.length; i++) {
        sorted[i] = arr[i];
    }

    // Bubble sort
    for (let i = 0; i < sorted.length - 1; i++) {
        for (let j = 0; j < sorted.length - i - 1; j++) {
            if (sorted[j] > sorted[j + 1]) {
                // Manual swap
                let temp = sorted[j];
                sorted[j] = sorted[j + 1];
                sorted[j + 1] = temp;
            }
        }
    }

    return sorted;
}

// Detect anomalies in fare/distance ratio
function detectFareRatioAnomalies(data) {
    let anomalies = [];

    for (let i = 0; i < data.length; i++) {
        let ratio = data[i].fare / data[i].distance;

        // Check for suspicious patterns
        if (ratio > 50) { // More than $50 per km
            anomalies[anomalies.length] = {
                trip: data[i],
                reason: 'Suspicious fare ratio: $' + ratio.toFixed(2) + '/km (very high)',
                type: 'ratio'
            };
        } else if (data[i].distance < 0.5 && data[i].fare > 30) {
            anomalies[anomalies.length] = {
                trip: data[i],
                reason: 'Short trip with high fare: ' + data[i].distance + 'km costs $' + data[i].fare,
                type: 'ratio'
            };
        } else if (data[i].speed > 150) {
            anomalies[anomalies.length] = {
                trip: data[i],
                reason: 'Impossible speed: ' + data[i].speed.toFixed(2) + ' km/h',
                type: 'speed'
            };
        }
    }

    return anomalies;
}

// Manually combine arrays and remove duplicates
function combineAnomalies(arr1, arr2, arr3) {
    let combined = [];
    let seen = {};

    // Add from arr1
    for (let i = 0; i < arr1.length; i++) {
        let id = arr1[i].trip.id;
        if (!seen[id]) {
            combined[combined.length] = arr1[i];
            seen[id] = true;
        }
    }

    // Add from arr2
    for (let i = 0; i < arr2.length; i++) {
        let id = arr2[i].trip.id;
        if (!seen[id]) {
            combined[combined.length] = arr2[i];
            seen[id] = true;
        }
    }

    // Add from arr3
    for (let i = 0; i < arr3.length; i++) {
        let id = arr3[i].trip.id;
        if (!seen[id]) {
            combined[combined.length] = arr3[i];
            seen[id] = true;
        }
    }

    return combined;
}

// Display anomalies in UI
function displayAnomalies(anomalies, execTime) {
    let container = document.getElementById('anomalyResults');
    container.innerHTML = '';

    if (anomalies.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #27ae60; padding: 20px;">✓ No anomalies detected! All trips appear normal.</p>';
        return;
    }

    // Show first 9 anomalies
    let displayCount = anomalies.length > 9 ? 9 : anomalies.length;
    for (let i = 0; i < displayCount; i++) {
        let anomaly = anomalies[i];
        let card = document.createElement('div');
        card.className = 'anomaly-card';

        card.innerHTML = `
            <div class="anomaly-card-header">
                <h4>Trip ${anomaly.trip.id}</h4>
                <span class="anomaly-badge">${anomaly.type.toUpperCase()}</span>
            </div>
            <div class="anomaly-details">
                <div><strong>Time:</strong> ${anomaly.trip.time}</div>
                <div><strong>Distance:</strong> ${anomaly.trip.distance} km</div>
                <div><strong>Fare:</strong> $${anomaly.trip.fare}</div>
                <div><strong>Speed:</strong> ${anomaly.trip.speed.toFixed(2)} km/h</div>
                <div class="anomaly-reason">${anomaly.reason}</div>
            </div>
        `;

        container.appendChild(card);
    }

}
