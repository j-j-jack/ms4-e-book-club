$(document).ready(function () {
  $.noConflict();
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
          jsonResponse = JSON.parse(response.items);
          console.log(jsonResponse);
          for (item in jsonResponse) {
            bookName = jsonResponse[item].fields.name;
            bookAuthor = jsonResponse[item].fields.author;
            bookImage = jsonResponse[item].fields.image;
            bookPrice = jsonResponse[item].fields.price;
            bookId = jsonResponse[item].pk;
            bookCategory = jsonResponse[item].fields.category;
            console.log(bookCategory);
            jQuery("#ajax-response").append(`${bookName}<br>`);
            jQuery("#ajax-response").append(`${bookAuthor}<br>`);
            jQuery("#ajax-response").append(`${bookCategory}<br>`);
            jQuery("#ajax-response").append(`${bookPrice}<br>`);
            jQuery("#ajax-response").append(`${bookId}<br>`);
          }
        } catch {
          console.log("oops that didn't work!");
        }
      },
    });
  });
});

let template = `
            <div class="product-container col-10 offset-1">
                <div class="row mt-1 mb-2"></div>
                <div class="row">
                    {% for product in products %}
                        <div class="col-sm-6 col-md-6 col-lg-4 col-xl-3">
                            <div class="card h-100 border-0">
                                {% if product.image %}
                                <a href="{% url 'product_detail' product.id %}">
                                    <img class="card-img-top img-fluid" src="{{ MEDIA_URL }}{{ product.image }}" alt="{{ product.name }}">
                                </a>
                                {% else %}
                                <a href="">
                                    <img class="card-img-top img-fluid" src="{{ MEDIA_URL }}images/noimage.png" alt="{{ product.name }}">
                                </a>
                                {% endif %}
                                <div class="card-body pb-0">
                                    <p class="mb-0">{{ product.name }}</p>
                                </div>
                                <div class="card-footer bg-white pt-0 border-0 text-left">
                                    <div class="row">
                                        <div class="col">
                                            <p class="lead mb-0 text-left font-weight-bold">\${{ product.price }}</p>
                                            {% if product.category %}
                                            <p class="small mt-1 mb-0">
                                                <a class="text-muted" href="{% url 'products' %}?category={{ product.category.name }}">
                                                    <i class="fas fa-tag mr-1"></i>{{ product.category.friendly_name }}
                                                </a>
                                            </p>
                                            {% endif %}
                                            {% if product.rating %}
                                                <small class="text-muted"><i class="fas fa-star mr-1"></i>{{ product.rating }} / 5</small>
                                            {% else %}
                                                <small class="text-muted">No Rating</small>
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {% if forloop.counter|divisibleby:1 %}
                            <div class="col-12 d-sm-none mb-5">
                                <hr>
                            </div>
                        {% endif %}                        
                        {% if forloop.counter|divisibleby:2 %}
                            <div class="col-12 d-none d-sm-block d-md-block d-lg-none mb-5">
                                <hr>
                            </div>
                        {% endif %}
                        {% if forloop.counter|divisibleby:3 %}
                            <div class="col-12 d-none d-lg-block d-xl-none mb-5">
                                <hr>
                            </div>
                        {% endif %}
                        {% if forloop.counter|divisibleby:4 %}
                            <div class="col-12 d-none d-xl-block mb-5">
                                <hr>
                            </div>
                        {% endif %}
                    {% endfor %}
                </div>
            </div>`;
