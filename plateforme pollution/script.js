// Simulez des données de pollution en temps réel et prédictives (remplacez cela par vos données réelles)
const realTimeData = {
    pm25: 25.4,
    pm10: 35.8
};

const predictedData = {
    pm25: 30.2,
    pm10: 40.6
};

// Mettez à jour les valeurs affichées dans le HTML
document.getElementById("pm25-value").textContent = realTimeData.pm25;
document.getElementById("pm10-value").textContent = realTimeData.pm10;
document.getElementById("predicted-pm25").textContent = predictedData.pm25;
document.getElementById("predicted-pm10").textContent = predictedData.pm10;
