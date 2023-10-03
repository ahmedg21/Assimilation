<?php
/**
 * HighChart.php
 * create by bngesp
 * create at 12/02/2023 on project DakAir
 * visite https://github.com/bngesp for more core
 */

class HighChart
{

    private $data;
    private $js;
    private $title;
    private $subtitle;
    private $name;
    private $dataType;
    private $container;

    public function __construct($container, $data, $name, $title, $subtitle = 'Source: DakAir' ,$dataType='pm25')
    {
        $this->data = $data;
        $this->title = $title;
        $this->subtitle = $subtitle;
        $this->name = $name;
        $this->dataType = $dataType;
        $this->container = $container;
    }

 public function getJs()
    {
        $this->js = "
        <script>
            Highcharts.chart('".$this->container."' , {
                chart: {
                    type: 'line'
                },
                title: {
                    text: '".$this->title."'
                },
                subtitle: {
                    text: '".$this->subtitle."'
                },
                xAxis: {
                    categories: [";
        foreach ($this->data as $value) {
            $this->js .= "'".$value['date']."',";
        }
        $this->js .= "]
                },
                yAxis: {
                    title: {
                        text: 'µg/m³'
                    }
                },
                plotOptions: {
                    line: {
                        dataLabels: {
                            enabled: true
                        },
                        enableMouseTracking: false
                    }
                },
                series: [{
                    name: '".$this->name."',
                    data: [";
        foreach ($this->data as $value) {
            $this->js .= $value[$this->dataType].",";
        }
        $this->js .= "]
                }]
            });
        </script>
        ";
        return $this->js;
    }

}