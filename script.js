// Global variables
let tripData = [];
let filteredData = [];
let currentPage = 1;
let rowsPerPage = 10;
let sortCol = -1;
let sortAsc = true;

// Initialize when page loads
window.onload = function() {
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
    
    for(let i = 0; i < 150; i++) {
        let dist = Math.random() * 25 + 0.3;
        let dur = Math.random() * 50 + 3;
        let fare = Math.random() * 60 + 3;
        let speed = (dist / (dur / 60));
        let pass = Math.floor(Math.random() * 5) + 1;
        let date = dates[Math.floor(Math.random() * dates.length)];
        let hour = Math.floor(Math.random() * 24);
        let min = Math.floor(Math.random() * 60);
        
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

// Apply filters
function applyFilters() {
    let start = document.getElementById('startDate').value;
    let end = document.getElementById('endDate').value;
    let minDist = parseFloat(document.getElementById('minDistance').value) || 0;
    let maxDist = parseFloat(document.getElementById('maxDistance').value) || 999999;
    let minFare = parseFloat(document.getElementById('minFare').value) || 0;
    let maxFare = parseFloat(document.getElementById('maxFare').value) || 999999;
    let passengers = document.getElementById('passengerCount').value;
    let timeSlot = document.getElementById('timeOfDay').value;
    
    filteredData = tripData.filter(function(trip) {
        let date = trip.time.split(' ')[0];
        let hour = parseInt(trip.time.split(' ')[1].split(':')[0]);
        
        // Date filter
        if(start && date < start) return false;
        if(end && date > end) return false;
        
        // Distance filter
        if(trip.distance < minDist || trip.distance > maxDist) return false;
        
        // Fare filter
        if(trip.fare < minFare || trip.fare > maxFare) return false;
        
        // Passenger filter
        if(passengers) {
            if(passengers === '5' && trip.passengers < 5) return false;
            if(passengers !== '5' && trip.passengers !== parseInt(passengers)) return false;
        }
        
        // Time of day filter
        if(timeSlot === 'morning' && (hour < 6 || hour >= 12)) return false;
        if(timeSlot === 'afternoon' && (hour < 12 || hour >= 18)) return false;
        if(timeSlot === 'evening' && (hour < 18 || hour >= 24)) return false;
        if(timeSlot === 'night' && hour >= 6) return false;
        
        return true;
    });
    
    currentPage = 1;
    updateAll();
}

// Reset filters
function resetFilters() {
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';
    document.getElementById('minDistance').value = '';
    document.getElementById('maxDistance').value = '';
    document.getElementById('minFare').value = '';
    document.getElementById('maxFare').value = '';
    document.getElementById('passengerCount').value = '';
    document.getElementById('timeOfDay').value = '';
    
    filteredData = tripData;
    currentPage = 1;
    updateAll();
}

// Update everything
function updateAll() {
    updateStats();
    drawCharts();
    updateTable();
    updateInsight();
}

// Update stats
function updateStats() {
    let total = filteredData.length;
    let totalFare = 0;
    let totalDist = 0;
    let totalDur = 0;
    
    for(let i = 0; i < filteredData.length; i++) {
        totalFare += filteredData[i].fare;
        totalDist += filteredData[i].distance;
        totalDur += filteredData[i].duration;
    }
    
    document.getElementById('totalTrips').textContent = total;
    document.getElementById('avgFare').textContent = '$' + (totalFare / total).toFixed(2);
    document.getElementById('avgDistance').textContent = (totalDist / total).toFixed(2) + ' km';
    document.getElementById('avgDuration').textContent = (totalDur / total).toFixed(1) + ' min';
}

// Draw all charts
function drawCharts() {
    drawHourChart();
    drawFareChart();
    drawSpeedChart();
}

// Draw hourly chart
function drawHourChart() {
    let hours = new Array(24).fill(0);
    
    for(let i = 0; i < filteredData.length; i++) {
        let h = parseInt(filteredData[i].time.split(' ')[1].split(':')[0]);
        hours[h]++;
    }
    
    let maxVal = Math.max(...hours);
    let container = document.getElementById('hourChart');
    container.innerHTML = '';
    
    let display = [0, 3, 6, 9, 12, 15, 18, 21];
    for(let i = 0; i < display.length; i++) {
        let h = display[i];
        let bar = document.createElement('div');
        bar.className = 'bar';
        let height = (hours[h] / maxVal) * 100;
        bar.style.height = height + '%';
        
        let lbl = document.createElement('div');
        lbl.className = 'bar-label';
        lbl.textContent = h + 'h';
        bar.appendChild(lbl);
        
        let val = document.createElement('div');
        val.className = 'bar-value';
        val.textContent = hours[h];
        bar.appendChild(val);
        
        container.appendChild(bar);
    }
}

// Draw fare chart
function drawFareChart() {
    let ranges = ['0-5', '5-10', '10-15', '15-20', '20+'];
    let fareTotals = [[], [], [], [], []];
    
    for(let i = 0; i < filteredData.length; i++) {
        let d = filteredData[i].distance;
        let f = filteredData[i].fare;
        if(d < 5) fareTotals[0].push(f);
        else if(d < 10) fareTotals[1].push(f);
        else if(d < 15) fareTotals[2].push(f);
        else if(d < 20) fareTotals[3].push(f);
        else fareTotals[4].push(f);
    }
    
    let avgFares = [];
    for(let i = 0; i < fareTotals.length; i++) {
        if(fareTotals[i].length > 0) {
            let sum = 0;
            for(let j = 0; j < fareTotals[i].length; j++) {
                sum += fareTotals[i][j];
            }
            avgFares.push(sum / fareTotals[i].length);
        } else {
            avgFares.push(0);
        }
    }
    
    let maxVal = Math.max(...avgFares);
    let container = document.getElementById('fareChart');
    container.innerHTML = '';
    
    for(let i = 0; i < ranges.length; i++) {
        let bar = document.createElement('div');
        bar.className = 'bar';
        let height = (avgFares[i] / maxVal) * 100;
        bar.style.height = height + '%';
        
        let lbl = document.createElement('div');
        lbl.className = 'bar-label';
        lbl.textContent = ranges[i] + 'km';
        bar.appendChild(lbl);
        
        let val = document.createElement('div');
        val.className = 'bar-value';
        val.textContent = '$' + avgFares[i].toFixed(1);
        bar.appendChild(val);
        
        container.appendChild(bar);
    }
}

// Draw speed chart
function drawSpeedChart() {
    let ranges = ['0-20', '20-40', '40-60', '60-80', '80+'];
    let counts = [0, 0, 0, 0, 0];
    
    for(let i = 0; i < filteredData.length; i++) {
        let s = filteredData[i].speed;
        if(s < 20) counts[0]++;
        else if(s < 40) counts[1]++;
        else if(s < 60) counts[2]++;
        else if(s < 80) counts[3]++;
        else counts[4]++;
    }
    
    let maxVal = Math.max(...counts);
    let container = document.getElementById('speedChart');
    container.innerHTML = '';
    
    for(let i = 0; i < ranges.length; i++) {
        let bar = document.createElement('div');
        bar.className = 'bar';
        let height = (counts[i] / maxVal) * 100;
        bar.style.height = height + '%';
        
        let lbl = document.createElement('div');
        lbl.className = 'bar-label';
        lbl.textContent = ranges[i];
        bar.appendChild(lbl);
        
        let val = document.createElement('div');
        val.className = 'bar-value';
        val.textContent = counts[i];
        bar.appendChild(val);
        
        container.appendChild(bar);
    }
}

// Update table
function updateTable() {
    let start = (currentPage - 1) * rowsPerPage;
    let end = start + rowsPerPage;
    let pageData = filteredData.slice(start, end);
    
    let tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    for(let i = 0; i < pageData.length; i++) {
        let row = tbody.insertRow();
        row.insertCell(0).textContent = pageData[i].id;
        row.insertCell(1).textContent = pageData[i].time;
        row.insertCell(2).textContent = pageData[i].distance.toFixed(2);
        row.insertCell(3).textContent = pageData[i].duration.toFixed(1);
        row.insertCell(4).textContent = pageData[i].fare.toFixed(2);
        row.insertCell(5).textContent = pageData[i].speed.toFixed(2);
        row.insertCell(6).textContent = pageData[i].passengers;
    }
    
    let totalPages = Math.ceil(filteredData.length / rowsPerPage);
    document.getElementById('pageNum').textContent = currentPage;
    document.getElementById('totalPg').textContent = totalPages;
    
    document.getElementById('prevBtn').disabled = (currentPage === 1);
    document.getElementById('nextBtn').disabled = (currentPage === totalPages);
}

// Pagination
function prevPage() {
    if(currentPage > 1) {
        currentPage--;
        updateTable();
    }
}

function nextPage() {
    let totalPages = Math.ceil(filteredData.length / rowsPerPage);
    if(currentPage < totalPages) {
        currentPage++;
        updateTable();
    }
}

// Sort table
function sortBy(col) {
    let fields = ['id', 'time', 'distance', 'duration', 'fare', 'speed', 'passengers'];
    
    if(sortCol === col) {
        sortAsc = !sortAsc;
    } else {
        sortCol = col;
        sortAsc = true;
    }
    
    let field = fields[col];
    
    filteredData.sort(function(a, b) {
        if(a[field] < b[field]) return sortAsc ? -1 : 1;
        if(a[field] > b[field]) return sortAsc ? 1 : -1;
        return 0;
    });
    
    updateTable();
}

// Update insight
function updateInsight() {
    let hourCounts = new Array(24).fill(0);
    
    for(let i = 0; i < filteredData.length; i++) {
        let h = parseInt(filteredData[i].time.split(' ')[1].split(':')[0]);
        hourCounts[h]++;
    }
    
    let maxCount = 0;
    let peakHour = 0;
    for(let i = 0; i < hourCounts.length; i++) {
        if(hourCounts[i] > maxCount) {
            maxCount = hourCounts[i];
            peakHour = i;
        }
    }
    
    let totalTrips = 0;
    for(let i = 0; i < hourCounts.length; i++) {
        totalTrips += hourCounts[i];
    }
    let avgPerHour = totalTrips / 24;
    let multiplier = (maxCount / avgPerHour).toFixed(1);
    
    document.getElementById('mainInsight').textContent = 
        'Peak hour is ' + peakHour + ':00 with ' + maxCount + ' trips (' + 
        multiplier + 'x average). This shows concentrated demand during specific times.';
}