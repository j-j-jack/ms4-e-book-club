jQuery(document).ready(function () {
  jQuery(".star-rating").each(function () {
    jQuery(this).click(function () {
      // use data attribute on star icons to set set color of stars
      // and set the value of the input on the form
      let starValue = jQuery(this).data("star");
      jQuery("#id_rating").val(starValue);
      for (let i = 1; i < 6; i++) {
        currentStar = ".star-" + i;
        if (i <= starValue) {
          jQuery(`${currentStar}`).attr("style", "color: yellow");
        } else {
          jQuery(`${currentStar}`).attr("style", "color: #BBB");
        }
      }
    });
  });
});
