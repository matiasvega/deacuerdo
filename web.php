<?php

if ($_REQUEST['action']=='getInfo') {
	if ($_REQUEST['dato']=='deudor' && $_REQUEST['dni']) {
		getDeudor($_REQUEST['dni']);
	}else if ($_REQUEST['dato']=='info') {
		if ($_REQUEST['dni']) {
			getInfo('dni', $_REQUEST['dni']);
		} else if ($_REQUEST['nrocuenta']){
			getInfo('nrocuenta', $_REQUEST['nrocuenta']);
		}
	} else {
		"Error: no existen datos disponibles.";
		die;
	}
} else if ($_REQUEST['action']=='sendInfo') {
		if($_REQUEST['dato']=='informePago'){		
			$entrega = json_decode($_REQUEST['form'], true);
			saveEntregas($entrega);
		} else if($_REQUEST['dato']=='deudor'){
			$deudor = json_decode($_REQUEST['form'], true);
			updateDeudor($deudor);
		} else if($_REQUEST['dato']=='contacto'){
			$contacto = json_decode($_REQUEST['form'], true);
			saveContactos($contacto);
		}
} 



function getInfo($id, $valorId) {
	include "./panel-adm/conexion.php";
	
	//Busco las deudas
	$res = array();
	if ($id=='dni') {
		$condition=sprintf("cli.DNI='%s'", $valorId);
	}else if($id=='nrocuenta'){
		$condition=sprintf("deu.Nro_Cuenta='%s'", $valorId);
	}

	$query=sprintf("
	SELECT 	deu.Id id, 
			deu.Id_Empresa empresa_id,
			deu.Nro_Cuenta nrocuenta, 
			deu.Monto saldo, 
			deu.Vencimiento vencimiento,
			deu.Codigo_barra codbarra,
			'deuda_monetaria' tipo_deuda
    FROM Deudas deu 
		inner join Clientes cli on (deu.Id_Cliente = cli.Id ) 
    where 1=1
    and %s", $condition);
      
    $result = mysqli_query($mysqli, $query);
	
    while($row = mysqli_fetch_assoc($result)){
		$res[] = $row;		
	}
	
	// Busco los equipos a recuperar
	
	if ($id=='dni') {
		$condition=sprintf("cli.DNI='%s'", $valorId);
	}else if($id=='nrocuenta'){
		$condition=sprintf("eq.nro_cuenta='%s'", $valorId);
	}


	$query=sprintf("
	SELECT 	eq.Id id, 
			eq.nro_cuenta nro_cuenta,
			eq.id_equipo nro_serie,
			eq.q_equipos cantidad,
			eq.saldo saldo,
			eq.Id_Empresa empresa_id, 
			eq.servicio servicio, 
			eq.tipo_equipo tipo, 
			eq.modelo_equipo modelo,
			'recupero_equipo' tipo_deuda
    FROM equipos eq 
		inner join Clientes cli on (eq.Id_Cliente = cli.Id ) 
    where 1=1
    and %s", $condition);
       
    $result = mysqli_query($mysqli, $query);
	
    while($row = mysqli_fetch_assoc($result)){
		$res[] = $row;		
	}	
		
	echo trim(json_encode($res));
	
}

function getDeudas($id, $valorId){

    
}

function getEquipos($id, $valorId){

    include "./panel-adm/conexion.php";


	//return trim(json_encode($res));
	return $res;
}

function d($param) {
	sprintf("<pre>%s</pre></br></br>", print_r($param));
}

function dd($param) {
	sprintf("<pre>%s</pre></br></br>", print_r($param));
	die;
}


function getDeudor($dni){

    include "./panel-adm/conexion.php";

	$query=sprintf("
	SELECT 			if (primerIngreso=0, false, true) as 'Primer Ingreso',
					concat(cli.nombre, ' ', cli.apellido) nyap,  
					dni dni,
					Email email,
					Telefono telefono,
					Calle calle,
					Numero numero,
					Piso piso,
					Departamento departamento,
					Barrio bariio,
					Km_Ruta km,
					Manzana manzana,
					Casa_Lote casa_lote,
					Edificio_Torre edicifio_torre,
					Cuerpo_Bloque cuerpo_bloque,
					CP cp					
    FROM Clientes cli
    where cli.DNI='%s' ", $dni);
       
    $result = mysqli_query($mysqli, $query);

    if($row = mysqli_fetch_assoc($result)){
		echo trim(json_encode($row));
	}
}

function updateDeudor($deudor){
	include "./panel-adm/conexion.php";
	$query=sprintf("UPDATE Clientes set primerIngreso=1, email='%s', telefono='%s' where DNI='%s'", $deudor['email'], $deudor['telefono'], $deudor['dni']);

    $result = mysqli_query($mysqli, $query);
}

function saveContactos($contacto) {
	include "./panel-adm/conexion.php";
	$query=sprintf("insert ignore into contacto (dni, fecha, telefono, email) values ('%s', sysdate(), '%s', '%s');", $contacto['dni_deudor'], $contacto['telefono'], $contacto['email']);
    $result = mysqli_query($mysqli, $query);
}

function saveEntregas($entrega) {
        include "./panel-adm/conexion.php";
        $query=sprintf("insert ignore into entregas (dni, lugar, fecha, comprobante, monto, tipoDeuda, idDeuda) values ('%s', '%s', '%s', \"%s\", '%s', '%s', '%s');", $entrega['dni'], $entrega['lugar'], $entrega['fecha'], $entrega['comprobante'], $entrega['monto'], ($entrega['monto']>0)?'monetaria':'equipo', $entrega['id_deuda']);
		$result = mysqli_query($mysqli, $query);

}


?>
