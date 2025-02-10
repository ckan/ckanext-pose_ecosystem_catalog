$(document).ready(function () {
  $(".variable").slick({
    dots: false,
    arrows: true,
    infinite: true,
    speed: 300,
    focusOnSelect: true,
    slidesToScroll: 1,
    slidesToShow: 4,
    centerMode: false,
    variableWidth: false,
  });

  $(".lazy").slick({
    lazyLoad: "ondemand",
    infinite: true,
  });
});
