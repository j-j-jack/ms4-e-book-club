jQuery(document).ready(function () {
  let categoryCount = parseInt(
    document.getElementsByClassName("category-count")[0].innerHTML
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
    for (i = 1; i <= categoryCount; i++) {
      let select = document.getElementsByTagName("select")[i - 1];
      select = select.options[select.selectedIndex].value;
      description = document.getElementsByTagName("textarea")[i - 1].value;
      ajaxFormSubmit(i, select, description);
    }
  });
});

function ajaxFormSubmit(formNumber, select, description) {
  jQuery.ajax({
    type: "POST",
    url: "",
    data: {
      category: formNumber,
      csrfmiddlewaretoken:
        document.getElementById("form1").firstElementChild.value,
      book: select,
      description: description,
    },
    success: function (response) {
      console.log("success");
      let finished = JSON.parse(response).finished;
      if (finished) {
        window.location = "";
      }
    },
  });
}
