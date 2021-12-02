$(document).ready(function () {
  $.noConflict();
  let loadRound = 0;
  let allCategories = jQuery("#all-categories").text();
  allCategories = JSON.parse(allCategories);
  console.log(allCategories);
  let unknownTitleTemplate = ``;
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
          let bookName;
          let bookImage;
          let bookRating;
          let bookCategory;
          let bookCategoryName;
          let bookCategoryFriendlyName;
          let bookId;
          jsonResponse = JSON.parse(response.items);
          console.log(jsonResponse);
          let normaltemplate = `
            <div class="row">
            <div class="product-container col-10 offset-1">
                <div class="row mt-1 mb-2"></div>
                <div class="row">`;
          for (var item in jsonResponse) {
            console.log(item);
            try {
              bookName = jsonResponse[item].fields.name;
            } catch (err) {
              console.log(err.message);
            }
            if (bookName == undefined || bookName == null) {
            }
            bookAuthor = jsonResponse[item].fields.author;
            try {
              bookImage = jsonResponse[item].fields.image;
            } catch (err) {
              console.log(err.message);
            }
            if (bookImage == undefined || bookImage == null) {
              bookImage = "images/noimage.png";
            }
            try {
              bookRating = jsonResponse[item].fields.rating;
            } catch (err) {
              console.log(err.message);
            }
            if (bookRating == undefined || bookRating == null) {
              bookRating = "no rating";
            }
            try {
              categoryNumber = jsonResponse[item].fields.category;
              for (var category in allCategories) {
                if (allCategories[category].pk == categoryNumber) {
                  bookCategoryName = allCategories[category].fields.name;
                  bookCategoryFriendlyName =
                    allCategories[category].fields.friendly_name;
                }
              }
            } catch (err) {
              console.log(err.message);
            }
            bookPrice = jsonResponse[item].fields.price;
            bookId = jsonResponse[item].pk;
            console.log(bookId);
            normaltemplate += `
                        <div class="col-sm-6 col-md-6 col-lg-4 col-xl-3">
                            <div class="card h-100 border-0">
                                <a href="product_detail/${bookId}">
                                    <img class="card-img-top img-fluid" src="/media/${bookImage}" alt="${bookName}">
                                </a>
                                <div class="card-body pb-0">
                                    <p class="mb-0">${bookName}</p>
                                </div>
                                <div class="card-footer bg-white pt-0 border-0 text-left">
                                    <div class="row">
                                        <div class="col">
                                            <p class="lead mb-0 text-left font-weight-bold">€${bookPrice}</p>
                                            <p class="small mt-1 mb-0">
                                                <a class="text-muted" href="?category=${bookCategoryName}">
                                                    <i class="fas fa-tag mr-1"></i>${bookCategoryFriendlyName}
                                                </a>
                                            </p>
                                            ${bookRating}${item}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
            if ((item + 1) % 1 == 0) {
              normaltemplate += `
                            <div class="col-12 d-sm-none mb-5">
                                <hr>
                            </div>`;
            }
            if ((item + 1) % 2 == 0) {
              normaltemplate += `
                            <div class="col-12 d-none d-sm-block d-md-block d-lg-none mb-5">
                                <hr>
                            </div>`;
            }
            if ((item + 1) % 3 == 0) {
              normaltemplate += `
                            <div class="col-12 d-none d-lg-block d-xl-none mb-5">
                                <hr>
                            </div>`;
            }
            if ((item + 1) % 4 == 0) {
              normaltemplate += `
                            <div class="col-12 d-none d-xl-block mb-5">
                                <hr>
                            </div>`;
            }
          }
          normaltemplate += `
            </div>
            </div>
            </div>`;
          jQuery("#ajax-response").append(normaltemplate);
        } catch (err) {
          console.log(err.message);
        }
      },
    });
  });
});
