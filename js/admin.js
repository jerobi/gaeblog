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
        var status = '';

        if (post.status == 1) {
            status = 'pending';
        }

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
                +
                SPAN({ 'class':'gaeb-status' },
                     status
                    )
               ) 
        );
    }

    $('#gaeb-posts').html(markup.join(''));
};

GAEBAdmin.showCover = function() {
    
    if (GAEBAdmin._coverPhoto) {
        $('#gaeb-cover-preview').html(
            TAG('span',
                {'class':'gaeb-cover-preview',
                 'style':'background-image:url('+GAEBAdmin._coverPhoto+')'
                }));
    }
    else {
        $('#gaeb-cover-preview').html('');
    }
};

GAEBAdmin.editForm = function(key) {
    for (var i=0; i < GAEBAdmin._posts.length; i++) {
        var post = GAEBAdmin._posts[i];
        if (post.key == key) {
            console.warn(post);
            GAEBAdmin._editKey = key;
            GAEBAdmin._coverPhoto = post.cover;
            // vitals
            $('#gaeb-title').val(post.title);
            $('#gaeb-published').val(post.published);
            // category & tags
            $('#gaeb-category').val(post.category);
            $('#gaeb-tags').val(post.tags.join(', '));
            // update the editor
            GAEBAdmin._editor.setHTML(post.content);
            GAEBAdmin.showCover();
            break;
        }
    }
    return false;
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
    GAEBAdmin._coverPhoto = null;
    //GAEBAdmin._photos = [];
    GAEBAdmin.enableForm();
    GAEBAdmin.showCover();
};

GAEBAdmin.error = function(message) {
    $('#gaeb-error').html(message);
    $('#gaeb-error').fadeIn();
};

GAEBAdmin.errorClear = function() {
    $('#gaeb-error').html('');
    $('#gaeb-error').fadeOut();
};

GAEBAdmin.submitPost = function(status) {
    var title = $('#gaeb-title').val();
    var published = $('#gaeb-published').val()
    var content = GAEBAdmin._editor.getHTML();

    // grab category and tags
    var category = $('#gaeb-category').val();
    var tags = $('#gaeb-tags').val();
    
    // prevent multiple clicks
    GAEBAdmin.disableForm();

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
        GAEBAdmin.error('Please add a published date');
        return GAEBAdmin.enableForm();
    }

    $.post('/admin/posts',
           {
               'key'        : GAEBAdmin._editKey,
               'cover'      : GAEBAdmin._coverPhoto,
               'title'      : title,
               'content'    : content,
               'status'     : status,
               'published'  : published,
               'category'   : category,
               'tags'       : tags
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
    $.get('/admin/posts', 
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
    GAEBAdmin._coverUpload = false;
    $('#gaeb-video-block').hide();
    $('#gaeb-image-block').fadeToggle();
};

GAEBAdmin.videoToggle = function() {
    $('#gaeb-image-block').hide();
    $('#gaeb-video-block').fadeToggle();
};

GAEBAdmin.coverToggle = function() {
    GAEBAdmin._coverUpload = true;
    $('#gaeb-cover-block').fadeToggle();
};

GAEBAdmin.coverClear = function() {
    GAEBAdmin._coverPhoto = null;
    GAEBAdmin.showCover();
    $('#gaeb-cover-block').fadeToggle();
};


GAEBAdmin.addYoutube = function() {

    // grab the video url from the form
    var video_url = $('#youtube').val();

    // if the user puts in the page url instead of the embed - convert it
    var re = /v\=(\S+)/i;
    var ma = re.exec(video_url);
    if (ma) {
        video_url = "https://www.youtube.com/embed/"+ma[1];
    }

    // get the current cursor
    var range = GAEBAdmin._editor.getSelection();
    var html = GAEBAdmin._editor.getHTML();

    // improve by saving off the cursor
    GAEBAdmin._editor.setHTML('<iframe class="gaeb-flv" src="'+video_url+'" frameborder="0" allowfullscreen></iframe>' + html);
    $('#gaeb-video-block').fadeToggle();
};

function addPhoto(photo_key, photo_url) {
    console.warn(photo_key, photo_url);

    // improve by saving all photos to a reusable place

    if (GAEBAdmin._coverUpload) {
        // saev cover photo and display in title area
        GAEBAdmin._coverPhoto = photo_url;
        GAEBAdmin.showCover();
        $('#gaeb-cover-block').fadeToggle();
    }
    else {
        // otherwise add it to the current post text
        var html = GAEBAdmin._editor.getHTML();

        /* improve by inserting at the cursor
        var range = GAEBAdmin._editor.getSelection();
        console.warn(range);
        */

        GAEBAdmin._editor.setHTML('<img src="'+photo_url+'" class="gaeb-fli"/>' + html);
        $('#gaeb-image-block').fadeToggle();
    }

};

$(document).ready(function() {
    GAEBAdmin._posts = [];
    GAEBAdmin._photos = [];
    GAEBAdmin._coverUpload = false;
    GAEBAdmin._coverPhoto = null;
    
    // for some reason the value attribute does not seem to be working
    var d = new Date();
    var m = d.getMonth()+1;
    $('#gaeb-published').val(d.getFullYear() + '-' + m + '-' + d.getDate());

    // hide image and video cells
    $('#gaeb-image-block').hide();
    $('#gaeb-video-block').hide();
    $('#gaeb-cover-block').hide();

    GAEBAdmin._editor = new Quill('#gaeb-editor', {
        modules: {
            'toolbar': { container: '#gaeb-toolbar' },
            'link-tooltip': true
        }
    });
    //GAEBAdmin._editor.addFormat('embed', {'tag':'IFRAME'});

    GAEBAdmin.clearForm();
    GAEBAdmin.getPosts();

});
