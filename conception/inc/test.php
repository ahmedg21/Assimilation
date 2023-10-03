<?php

/**
 * test.php
 * create by bngesp
 * create at 12/02/2023 on project DakAir
 * visite https://github.com/bngesp for more core
 */

include 'Api.php';
include 'HighChart.php';

// add cors allow all
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: *");
header("Access-Control-Allow-Methods: *");
header("Content-Type: application/json; charset=UTF-8");

$api = Api::getInstence();
if (isset($_GET['type'])) {
    $type = $_GET['type'];
    echo $api->getAllType($type);
} elseif (isset($_GET['tab'])) {
    $el = [];
    $el["data"] = $api->get("data", "desc");
    echo json_encode($el);
} elseif (isset($_GET['global'])) {
    echo json_encode($api->getLastData());
}
