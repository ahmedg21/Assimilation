<?php
/**
 * Api.php
 * create by bngesp
 * create at 12/02/2023 on project DakAir
 * visite https://github.com/bngesp for more core
 */

class Api
{
    // ctreate singleton acees to db

    private $db;

    private static $api=null;

    private function __construct()
    {
        $this->db = new PDO('mysql:host=localhost;dbname=pollution;charset=utf8', 'root', '150421Ah');
        $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }

    public static function getInstence()
    {
        if(self::$api==null)
        {
            self::$api = new Api();
        }
        return self::$api;
    }

    public function getDb()
    {
        return $this->db;
    }

    public function get($table="data", $order="asc")
    {
        // selection from table where date > 2018-11-11 order by id asc
        $sql = "SELECT * FROM $table WHERE event > '2023-02-20' order by id ".$order;
        //$sql = "SELECT * FROM $table  order by id ".$order;
        $stmt = $this->db->prepare($sql);
        $stmt->execute();
        $data = $stmt->fetchAll(PDO::FETCH_ASSOC);
        return $data;
    }

     public function getLastData(){
        $sql = "SELECT * FROM data WHERE event > '2023-02-20' order by id desc limit 1";
        $stmt = $this->db->prepare($sql);
        $stmt->execute();
        $data = $stmt->fetchAll(PDO::FETCH_ASSOC);
        return $data;
    }

    public function insert($table, $data)
    {
        $sql = "INSERT INTO $table (pm01, pm25, pm10, temperature, humidity) VALUES (:pm01, :pm25, :pm10, :temperature, :humidity)";
        $stmt = $this->db->prepare($sql);
        $stmt->bindParam(':pm01', $data[0]);
        $stmt->bindParam(':pm25', $data[1]);
        $stmt->bindParam(':pm10', $data[2]);
        $stmt->bindParam(':temperature', $data[3]);
        $stmt->bindParam(':humidity', $data[4]);
        $stmt->execute();
        return "ok";
    }

    // function to get All data from table return json
    public function getAll($table="data")
    {
        $data = $this->get($table);
        return json_encode($data);
    }

    // get All tyde data(type on param) and return json with value and timestamp
    public function getAllType($type="pm25",$table="data")
    {
        $data = $this->get($table);
        $result = [];
        foreach ($data as $key => $value) {
            $date = $value["event"];
            $result[] = [
                strtotime($date)*1000,
                $value[$type]+0
                // date is sql date format change to timestamp
            ];
        }
        return json_encode($result);
    }
}