/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/
jQuery(document).ready(function () {
  /*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

  var stripePublicKey = jQuery("#id_stripe_public_key").text().slice(1, -1);
  var clientSecret = jQuery("#id_client_secret").text().slice(1, -1);
  var stripe = Stripe(stripePublicKey);
  var elements = stripe.elements();
  var style = {
    base: {
      color: "#000",
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSmoothing: "antialiased",
      fontSize: "16px",
      "::placeholder": {
        color: "#aab7c4",
      },
    },
    invalid: {
      color: "#dc3545",
      iconColor: "#dc3545",
    },
  };
  var card = elements.create("card", { style: style });
  card.mount("#card-element");

  // Handle realtime validation errors on the card element
  card.addEventListener("change", function (event) {
    var errorDiv = document.getElementById("card-errors");
    if (event.error) {
      var html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
      jQuery(errorDiv).html(html);
    } else {
      errorDiv.textContent = "";
    }
  });

  // Handle form submit
  var form = document.getElementById("payment-form");

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    card.update({ disabled: true });
    jQuery("#submit-button").attr("disabled", true);
    jQuery("#payment-form").fadeToggle(100);
    jQuery("#loading-overlay").fadeToggle(100);
    console.log(card);
    var saveInfo = Boolean(jQuery("#id-save-info").attr("checked"));
    console.log(saveInfo);
    // From using {% csrf_token %} in the form
    var csrfToken = jQuery('input[name="csrfmiddlewaretoken"]').val();
    var postData = {
      csrfmiddlewaretoken: csrfToken,
      client_secret: clientSecret,
      save_info: saveInfo,
      email: jQuery.trim(form.email.value),
      name: jQuery.trim(form.full_name.value),
    };
    var url = "/checkout/cache_checkout_data/";

    jQuery
      .post(url, postData)
      .done(function () {
        stripe
          .confirmCardPayment(clientSecret, {
            payment_method: {
              card: card,
              billing_details: {
                name: jQuery.trim(form.full_name.value),
                phone: jQuery.trim(form.phone_number.value),
                email: jQuery.trim(form.email.value),
                address: {
                  line1: jQuery.trim(form.street_address1.value),
                  line2: jQuery.trim(form.street_address2.value),
                  city: jQuery.trim(form.town_or_city.value),
                  country: jQuery.trim(form.country.value),
                  state: jQuery.trim(form.county.value),
                },
              },
            },
            shipping: {
              name: jQuery.trim(form.full_name.value),
              phone: jQuery.trim(form.phone_number.value),
              address: {
                line1: jQuery.trim(form.street_address1.value),
                line2: jQuery.trim(form.street_address2.value),
                city: jQuery.trim(form.town_or_city.value),
                country: jQuery.trim(form.country.value),
                postal_code: jQuery.trim(form.postcode.value),
                state: jQuery.trim(form.county.value),
              },
            },
          })
          .then(function (result) {
            if (result.error) {
              var errorDiv = document.getElementById("card-errors");
              var html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
              jQuery(errorDiv).html(html);
              jQuery("#payment-form").fadeToggle(100);
              jQuery("#loading-overlay").fadeToggle(100);
              card.update({ disabled: false });
              jQuery("#submit-button").attr("disabled", false);
            } else {
              if (result.paymentIntent.status === "succeeded") {
                form.submit();
              }
            }
          });
      })
      .fail(function () {
        // just reload the page, the error will be in django messages
        location.reload();
      });
  });
});
