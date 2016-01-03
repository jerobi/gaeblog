var GAEBFeed = GAEBFeed || {};

GAEBFeed.showPosts = function() {
    var markup = [];
    
    for (var i=0; i < GAEBFeed._posts.length; i++) {
        var post = GAEBFeed._posts[i];
        markup.push(
            DIV({ 'class':'gaeb-post',
                },
                DIV({ 'class':'gaeb-title' },
                    post.title
                   ) 
                +
                DIV({ 'class':'gaeb-date' },
                    post.published
                   ) 
                +
                DIV({ 'class':'gaeb-content' },
                    post.content
                   )
                +
                DIV({ 'class':'gaeb-clear' },
                    ''
                   )
               ) 
            
        );
    }

    $('#gaeb-posts').html(markup.join(''));
};

GAEBFeed.getPosts = function() {
    $.get('/published', 
          {},
          function(response) {
              GAEBFeed.response = response;
              console.warn(response.status);
              GAEBFeed._posts = response.data;
              console.warn(GAEBFeed._posts);
              GAEBFeed.showPosts();
          });
};

$(document).ready(function() {
    GAEBFeed._posts = [];
    GAEBFeed.getPosts();
});
