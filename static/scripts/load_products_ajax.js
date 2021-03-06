jQuery(document).ready(function () {
  let loadRound = 0;
  let allCategories = jQuery("#all-categories").text();
  let mediaURL = jQuery("#media-url").text();
  allCategories = JSON.parse(allCategories);
  // productCardCount is used to use the same floating logic as in the template
  let productCardCount = 20;
  jQuery("#load-more").click(function () {
    loadRound += 1;
    // each click increases the load more so the next products are gathered
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
          let bookCategoryName;
          let bookCategoryFriendlyName;
          let bookId;
          jsonResponse = JSON.parse(response.items);
          let template = `
            `;
          // although by design there shouldn't be any errors error handling is implemented
          for (var item in jsonResponse) {
            let errorExists = false;
            productCardCount += 1;
            try {
              bookName = jsonResponse[item].fields.name;
            } catch (err) {
              console.log(err.message);
            }
            if (bookName == undefined || bookName == null) {
              errorExists = true;
            }

            try {
              bookAuthor = jsonResponse[item].fields.author;
            } catch (err) {
              console.log(err.message);
            }
            if (bookAuthor == undefined || bookAuthor == null) {
              errorExists = true;
            }

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
            if (
              bookRating == undefined ||
              bookRating == null ||
              bookRating == ""
            ) {
              bookRating = "No Rating";
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

            try {
              bookPrice = jsonResponse[item].fields.price;
            } catch (err) {
              console.log(err.message);
            }
            if (bookPrice == undefined || bookPrice == null) {
              errorExists = true;
            }

            try {
              bookId = jsonResponse[item].pk;
            } catch (err) {
              console.log(err.message);
            }
            if (bookId == undefined || bookId == null) {
              errorExists = true;
            }

            if (errorExists == false) {
              // intricate patching together of template to match products page
              template += `
                        <div class="product-card col-sm-6 col-md-6 col-lg-4 col-xl-3">
                            <div class="card h-100 border-0">
                                <a href="product_detail/${bookId}">
                                    <img class="card-img-top img-fluid" src="${mediaURL}${bookImage}" alt="${bookName}">
                                </a>
                                <div class="card-body pb-0">
                                    <p class="mb-0">${bookName}</p>
                                </div>
                                <div class="card-footer bg-white pt-0 border-0 text-left">
                                    <div class="row">
                                        <div class="col">
                                            <p class="lead mb-0 text-left font-weight-bold">???${bookPrice}</p>
                                            <p class="small mt-1 mb-0">`;
              if (
                bookCategoryName != undefined ||
                (bookCategoryName != null &&
                  bookCategoryFriendlyName != undefined) ||
                bookCategoryFriendlyName != null
              ) {
                template += `<a class="text-muted" href="?category=${bookCategoryName}">
                                                    <i class="fas fa-tag mr-1"></i>${bookCategoryFriendlyName}
                                                </a>
                                                `;
              } else {
                template += `
                <small class="text-muted"><i class="fas fa-tag mr-1"></i>Uncategorised</small>
                                                
                                                `;
              }
              template += `</p>
                                            <small class="text-muted">${bookRating}</small>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>`;
            } else {
              template += `
                        <div class="col-sm-6 col-md-6 col-lg-4 col-xl-3">
                            <div class="card h-100 border-0">
                                    <img class="card-img-top img-fluid" src="${mediaURL}images/noimage.png" alt="title not found">
                                <div class="card-body pb-0">
                                    <p class="mb-0">Title not found</p>
                                </div>
                                <div class="card-footer bg-white pt-0 border-0 text-left">
                                </div>
                            </div>
                        </div>`;
            }
            // using the productCardCount to implement the horizontal rule logic
            if (productCardCount % 1 == 0) {
              template += `
                            <div class="col-12 d-sm-none mb-5">
                                <hr>
                            </div>`;
            }
            if (productCardCount % 2 == 0) {
              template += `
                            <div class="col-12 d-none d-sm-block d-md-block d-lg-none mb-5">
                                <hr>
                            </div>`;
            }
            if (productCardCount % 3 == 0) {
              template += `
                            <div class="col-12 d-none d-lg-block d-xl-none mb-5">
                                <hr>
                            </div>`;
            }
            if (productCardCount % 4 == 0) {
              template += `
                            <div class="col-12 d-none d-xl-block mb-5">
                                <hr>
                            </div>`;
            }
          }
          jQuery("#ajax-response").append(template);
        } catch (err) {
          console.log(err.message);
        }
        loadMoreOrNot = JSON.parse(response.load_more);
        if (!loadMoreOrNot) {
          // the view defines when the loadmore button is to disappear
          jQuery("#load-more-container").attr("style", " display:none");
        }
      },
    });
  });
});
