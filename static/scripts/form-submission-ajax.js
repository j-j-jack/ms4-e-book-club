// script to submit each form on edit book clubs page individually
// this is necessary as they are each instances of the model so generate individual forms
jQuery(document).ready(function () {
  let categoryCount = parseInt(
    document.getElementsByClassName("category-count")[0].innerHTML
  );
  jQuery("#form-submission-button").click(function () {
    // the form submission button is used to trigger the submission of form1 which
    // causes a chain reaction!
    console.log("submitting now");
    jQuery("#form1").submit();
  });
  jQuery(document).on("submit", "#form1", function (e) {
    e.preventDefault();
    let overlay = document.getElementById("form-loading-overlay");
    // overlay which has the loading icon and disables pointerevents
    overlay.style.display = "block";
    document.body.style.pointerEvents = "none";
    for (i = 1; i <= categoryCount; i++) {
      let select = document.getElementsByTagName("select")[i - 1];
      // get each form input values using the for loop
      select = select.options[select.selectedIndex].value;
      description = document.getElementsByTagName("textarea")[i - 1].value;
      // call the ajax function
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
        // get the csrftoken from the hidden page input
        document.getElementById("form1").firstElementChild.value,
      book: select,
      description: description,
    },
    success: function (response) {
      console.log("success");
      //once all the forms are submitted the view returns finished as true and the page reloads
      let finished = JSON.parse(response).finished;
      if (finished) {
        window.location = "";
      }
    },
  });
}
