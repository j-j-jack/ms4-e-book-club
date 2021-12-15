jQuery(document).ready(function () {
  jQuery("#form-submission-button").click(function () {
    console.log("submitting now");
    jQuery("#form1").submit();
  });
});
