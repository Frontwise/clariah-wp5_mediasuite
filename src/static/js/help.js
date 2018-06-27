/**
 * Enable question mark button and show help
 */

function initHelp(helpTitle, contentUrl){
  
  var initialized = false;
  var container, button, title, close, content;

  // initialize
  function initDOM(){

      if (initialized){
          return true;
      }

      container = document.getElementById('help_container');
      button = document.getElementById('help_button');
      title = document.getElementById('help_title');
      close = document.getElementById('help_close');
      content = document.getElementById('help_content');

      if (!container || !button || !title || !content || !close){
          console.error('Could not find help DOM');
          return false;
      }

      // show help
      button.onclick = ()=>{
          container.style.display = 'block';
      }

      // close help
      close.onclick = ()=>{
          container.style.display = 'none';
      }
      return true;
  }
  
  // load data from the given url to the content container
  function loadData(contentUrl){
      content.innerHTML = "Loading...";
      fetch(contentUrl).then(function(response){
          if (response.status !== 200){
              return 'Could not load the help data. Please make sure it is available at: <a href="'+contentUrl+'">' + contentUrl + '</a>';
          }
          return response.text();
      }).then(function(html){
          content.innerHTML = html;
      }).catch(function(error){
          console.warn(error);
      });
  }

  // init help with given titel and content Url
  if (!initDOM()){
      // an error occured during init
      return;
  }
          
  title.innerHTML = helpTitle;
  loadData(contentUrl);
}