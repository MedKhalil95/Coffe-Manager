if (typeof profitData !== "undefined") {

    const ctx = document.getElementById("profitChart");

    new Chart(ctx, {
        type: "line",
        data: {
            labels: profitData.labels,
            datasets: [{
                label: "Profit",
                data: profitData.values,
                borderWidth: 3,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            }
        }
    });
}
