jQuery(document).ready(function () {
  let categoryCount = parseInt(
    document.getElementsByClassName("category-count")[0]
  );
  jQuery("#form-submission-button").click(function () {
    console.log("submitting now");
    jQuery("#form1").submit();
  });
  jQuery(document).on("submit", "#form1", function (e) {
    e.preventDefault();
    let overlay = document.getElementById("form-loading-overlay");
    overlay.style.display = "block";
    document.body.style.pointerEvents = "none";
    document.style.cursor = "pointer";
    for (i = 1; i <= categoryCount; i++) {
      let select = document.getElementsByTagName("select")[i - 1];
      select = select.options[select.selectedIndex].value;
      ajaxFormSubmit(i, select);
    }
  });
});

function ajaxFormSubmit(formNumber, select) {
  jQuery.ajax({
    type: "POST",
    url: "",
    data: {
      category: formNumber,
      csrfmiddlewaretoken:
        document.getElementById("form1").firstElementChild.value,
      book: select,
    },
    success: function () {
      console.log("success");
    },
  });
}
