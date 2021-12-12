jQuery(document).ready(function () {
  let countrySelected = jQuery("#id_default_country").val();
  if (!countrySelected) {
    jQuery("#id_default_country").css("color", "#aab7c4");
  }
  jQuery("#id_default_country").change(function () {
    countrySelected = jQuery(this).val();
    if (!countrySelected) {
      jQuery(this).css("color", "#aab7c4");
    } else {
      jQuery(this).css("color", "#000");
    }
  });
});
