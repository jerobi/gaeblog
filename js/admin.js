var GAEBAdmin = GAEBAdmin || {};

GAEBAdmin.showPhotos = function() {
    var markup =[];

    for (var i=0; i<GAEBAdmin._photos.length; i++) {
        var photo = GAEBAdmin._photos[i];        
        markup.push(
            THUMB(photo.url, 50)
        );
    }

    $('#postimg').html(markup.join(''));
};

GAEBAdmin.showPosts = function() {
    var markup = [];
    
    for (var i=0; i < GAEBAdmin._posts.length; i++) {
        var post = GAEBAdmin._posts[i];
        markup.push(
            TAG('a',
                { 'class':'gaeb-post',
                  'href':'#',
                  'onclick':"return GAEBAdmin.editForm('"+post.key+"');"
                },
                SPAN({ 'class':'gaeb-aname' },
                     post.title
                    ) 
                +
                SPAN({ 'class':'gaeb-date' },
                     post.published
                    ) 
               ) 
        );
    }

    $('#gaeb-posts').html(markup.join(''));
};

GAEBAdmin.editForm = function(key) {
    for (var i=0; i < GAEBAdmin._posts.length; i++) {
        var post = GAEBAdmin._posts[i];
        if (post.key == key) {
            console.warn(post);
            GAEBAdmin._editKey = key;
            // vitals
            $('#gaeb-title').val(post.title);
            $('#gaeb-published').val(post.published);
            // update the editor
            GAEBAdmin._editor.setHTML(post.content);
            
            //photos
            //GAEBAdmin._photos = [];
            //addPhoto(animal.cover.key, animal.cover.url)
            break;
        }
    }
};

GAEBAdmin.disableForm = function(message) {
    GAEBAdmin.errorClear();
};

GAEBAdmin.enableForm = function() {
    
};

GAEBAdmin.clearForm = function() {
    $('input').val('');
    GAEBAdmin._editor.setHTML('');
    GAEBAdmin._editKey = "";
    //GAEBAdmin._photos = [];
    GAEBAdmin.enableForm();
};

GAEBAdmin.error = function(message) {
    $('#gaeb-error').html(message);
    $('#gaeb-error').fadeIn();
};

GAEBAdmin.errorClear = function() {
    $('#gaeb-error').html('');
    $('#gaeb-error').fadeOut();
};

GAEBAdmin.submitPost = function() {
    var title = $('#gaeb-title').val();
    var published = $('#gaeb-published').val()
    var content = GAEBAdmin._editor.getHTML();
    
    // prevent multiple clicks
    GAEBAdmin.disableForm();

    
    console.warn(title);
    console.warn(content);
    console.warn(published);

    // validate form
    if (title == '') {
        GAEBAdmin.error('Please add a title');
        return GAEBAdmin.enableForm();
    }
    /*
    if (GAEBAdmin._photos.length == 0) {
        $('#error').html('please add a photo');
        return GAEBAdmin.enableForm();
    }
    */
    if (published == '') {
        GAEBAdmin.error('Please add a Title');
        return GAEBAdmin.enableForm();
    }

    $.post('/posts',
           {
               'key'        : GAEBAdmin._editKey,
               // 'cover':cover,
               'title'      : title,
               'content'    : content,
               'published'  : published,
           },
           function(response) {
               GAEBAdmin.addPost(response.data);
               GAEBAdmin.showPosts();
               GAEBAdmin.clearForm();
           });

    return false;
};

GAEBAdmin.addPost = function(post) {
    // if post is already part of our saved posts replace it
    for (var i=0; i < GAEBAdmin._posts.length; i++) {
        var p = GAEBAdmin._posts[i];
        if (p.key == post.key) {
            GAEBAdmin._posts[i] = post;
            return;
        }
    }
    // otherwise add it
    GAEBAdmin._posts.push(post);
}

GAEBAdmin.getPosts = function() {
    $.get('/posts', 
          {},
          function(response) {
              GAEBAdmin.response = response;
              console.warn(response.status);
              GAEBAdmin._posts = response.data;
              console.warn(GAEBAdmin._posts);
              GAEBAdmin.showPosts();
          });
};

GAEBAdmin.imageToggle = function() {
    $('#gaeb-video-block').hide();
    $('#gaeb-image-block').fadeToggle();
};

GAEBAdmin.videoToggle = function() {
    $('#gaeb-image-block').hide();
    $('#gaeb-video-block').fadeToggle();
};

function addPhoto(photo_key, photo_url) {
    console.warn(photo_key, photo_url);
    
    // get the current cursor
    var range = GAEBAdmin._editor.getSelection();
    var html = GAEBAdmin._editor.getHTML();

    console.warn(range);
    console.warn(html);

    // improve by saving off cursor
    GAEBAdmin._editor.setHTML('<img src="'+photo_url+'" class="gaeb-fli"/>' + html);

    /*
    GAEBAdmin._photos = [];
    GAEBAdmin._editor.insertText(5, 'Quill', {
        'italic': true,
        'fore-color': '#ffff00'
    });
    */
};

$(document).ready(function() {
    GAEBAdmin._posts = [];
    GAEBAdmin._photos = [];
    
    // for some reason the value attribute does not seem to be working
    var d = new Date();
    var m = d.getMonth()+1;
    $('#gaeb-published').val(d.getFullYear() + '-' + m + '-' + d.getDate());

    // hide image and video cells
    $('#gaeb-image-block').hide();
    $('#gaeb-video-block').hide();

    GAEBAdmin._editor = new Quill('#gaeb-editor', {
        modules: {
            'toolbar': { container: '#gaeb-toolbar' },
            'link-tooltip': true
        }
    });

    GAEBAdmin.clearForm();
    GAEBAdmin.getPosts();

});
