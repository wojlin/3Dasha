class Charts
{
    constructor()
    {


        this.move_chart_canvas = document.getElementById('move_chart').getContext('2d');
        this.temperature_chart_canvas = document.getElementById('temperature_chart').getContext('2d');
        this.move_chart = null //new Chart(ctx, config);
        this.temperature_chart = null//new Chart(ctx, config);



        let interval = setInterval(function()
        {
            charts.fetchCharts();
        },
        1000);

    }


    fetchCharts()
    {
        this.fetchMoveChart();
        this.fetchTemperatureChart();
    }

    fetchMoveChart()
    {
        api.fetchMoveChart();
    }

    fetchTemperatureChart()
    {
        api.fetchTemperatureChart();
    }

    updateMoveChart(response)
    {
        let json = JSON.parse(response);
        console.log(json);

    }

    updateTemperatureChart(response)
    {

        let json = JSON.parse(response);
        console.log(json);

        if(charts.temperature_chart == null)
        {
            let data = {
                labels: json["data"]["labels"],
                datasets: [
                    {
                        label: 'Bed temperature',
                        data: json["data"]["bed"],
                        fill: true,
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.3)',
                        tension: 0.1,
                        pointStyle: 'transparent',
                        pointRadius: 0
                    },
                    {
                        label: 'Extruder temperature',
                        data: json["data"]["extruder"],
                        fill: true,
                        borderColor: 'rgb(255, 122, 122)',
                        backgroundColor: 'rgba(255, 122, 122, 0.3)',
                        tension: 0.1,
                        pointStyle: 'transparent',
                        pointRadius: 0
                    }
                ]
            };

            // Configuration options for the chart
            let config = {
                type: 'line',
                data: data,
                options: {
                    maintainAspectRatio: false,
                    scales:
                    {
                        xAxes: [
                            {
                                gridLines:
                                {
                                    color: "rgba(255,255,255,0.7)"
                                },
                                ticks:
                                {
                                    fontColor: 'white',
                                    maxTicksLimit: 2,
                                }
                            }
                        ],
                        yAxes: [
                            {
                                gridLines:
                                {
                                    color: "rgba(255,255,255,0.7)"
                                },
                                ticks:
                                {
                                    fontColor: 'white',
                                }
                            }
                        ]
                    },
                    tooltips: {
                        enabled: false,
                    },
                    legend: {
                        labels: {
                            fontColor: "white",
                            fontSize: 12,
                            padding: 2,
                            boxWidth: 15,
                        },

                    },
                    responsive: true,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                        },
                        title: {
                            display: false,
                            text: ''
                        }
                    },
                    events: [],
                }
            };

            charts.temperature_chart = new Chart(charts.temperature_chart_canvas, config);

        }
        else
        {
            
        }
    }




}


const charts = new Charts();


