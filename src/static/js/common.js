// When 'active' class is present in header remove the opacity of the header bar.
if($('.transparent').find('.active')) {
  $('.header').css('background-color', '#2D343A');
  breadcrumb();
}

//https://gist.github.com/jlong/2428561
function breadcrumb(link, text) {
  let parser = document.createElement('a');
  let x = location.href;
    parser.href = x;
  let arrayOfStrings = parser.pathname.substring(1).split('/');
  let breadcrumb = '<li><a href="/" class="home"> </a> /</li>';
  let url = '';

  if(arrayOfStrings) {
    arrayOfStrings.forEach(function(el){
      let tmp = el.charAt(0).toUpperCase() + el.slice(1);
        tmp = tmp.replace("-", " ");
        url += (el === 'recipe') ? 'recipes/' : el + '/';
      breadcrumb += '<li><a href="/' + url.slice(0, -1) + '">' + tmp + '</a> /</li>';
    })
  }
console.log('url', url);
  $('.BreadCrumbs').html(breadcrumb);
}

