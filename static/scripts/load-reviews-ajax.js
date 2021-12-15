jQuery(document).ready(function () {
  let loadRound = 0;
  jQuery("#load-more").click(function () {
    loadRound += 1;
    jQuery.ajax({
      url: "",
      type: "get",
      data: {
        load_round: loadRound,
      },
      success: function (response) {
        try {
          let reviewTitle;
          let reviewRating;
          let reviewBody;
          jsonResponse = JSON.parse(response.items);
          let template = ``;
          for (var item in jsonResponse) {
            let errorExists = false;
            template = `<div class="row">
              <div class="col" style="border-bottom: 1px solid black">`;
            try {
              reviewTitle = jsonResponse[item].fields.title;
              template += `<h5>${reviewTitle}</h5>`;
            } catch (err) {
              console.log(err.message);
            }
            if (reviewTitle == undefined || reviewTitle == null) {
              errorExists = true;
            }

            try {
              reviewRating = jsonResponse[item].fields.rating;
              template += `<small class="text-muted"><i class="fas fa-star mr-1"></i> ${reviewRating} / 5</small>`;
            } catch (err) {
              console.log(err.message);
            }
            if (reviewRating == undefined || reviewRating == null) {
              errorExists = true;
            }

            try {
              reviewBody = jsonResponse[item].fields.review_body;
              template += `<p>${reviewBody}</p>`;
            } catch (err) {
              console.log(err.message);
            }
            if (reviewBody == undefined || reviewBody == null) {
              errorExists = true;
            }

            if (errorExists == false) {
              template += `</div>
                            </div>`;
            } else {
              template = ``;
            }
            jQuery("#ajax-response").append(template);
          }
        } catch (err) {
          console.log(err.message);
        }
        jsonResponseLength = Object.keys(jsonResponse).length;
        if (jsonResponseLength < 5) {
          jQuery("#load-more-container").attr("style", " display:none");
        }
      },
    });
  });
});
