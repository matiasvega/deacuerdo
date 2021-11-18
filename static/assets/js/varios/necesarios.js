/* ESTE ARCHIVO CONTIENE JS IMPORTANTE PARA MULTIPLES ARCHIVOS */

$(document).ready(function() {
  $('.select-generico').select2({
    placeholder: "Seleccione una opción",
    language: {
       noResults: function (params) {
         return "No se encontraron resultados.";
       }
     }
  });
});
