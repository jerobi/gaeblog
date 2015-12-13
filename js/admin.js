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
                { 'class':'post',
                  'href':'#',
                  'onclick':"return GAEBAdmin.editForm('"+post.key+"');"
                },
                SPAN({ 'class':'postpic',
                       'style':"background-image:url('"+post.cover.url+"');"
                     }) +
                SPAN({ 'class':'aname' },
                     post.title
                    )
               ) 
        );
    }

    $('#posts').html(markup.join(''));
};

GAEBAdmin.editForm = function(key) {
    for (var i=0; i < GAEBAdmin._posts.length; i++) {
        var post = GAEBAdmin._posts[i];
        if (post.key == key) {
            console.warn(post);
            GAEBAdmin._editKey = key;
            // vitals
            $('#title').val(post.title);
            $('#content').val(post.content);
            $('#published').val(animal.pubdate);
            //photos
            GAEBAdmin._photos = [];
            addPhoto(animal.cover.key, animal.cover.url)
            break;
        }
    }
};

GAEBAdmin.disableForm = function(message) {
    $('#error').html('');
    $('#adder').val(message);
    $('#adder').attr('disabled','disabled');
};

GAEBAdmin.enableForm = function() {
    $('#adder').val("SAVE");
    $('#clearer').val("NEW");
    $('#adder').attr('disabled',null);
};

GAEBAdmin.clearForm = function() {
    $('input').val('');
    $('#content').val('');
    $('#animg').html('');
    GAEBAdmin._editKey = "";
    GAEBAdmin._photos = [];
    GAEBAdmin.enableForm();
};


GAEBAdmin.addAngus = function() {
    var pics = [];
    var cover = '';
    
    // prevent multiple clicks
    GAEBAdmin.disableForm();

    // validate form
    if ($('#name').val() == '') {
        $('#error').html('please add a name');
        return GAEBAdmin.enableForm();
    }
    if (GAEBAdmin._photos.length == 0) {
        $('#error').html('please add a photo');
        return GAEBAdmin.enableForm();
    }
    if ($('#birthdate').val() == '') {
        $('#error').html('please add birthdate');
        return GAEBAdmin.enableForm();
    }
    if ($('#birthweight').val() == '') {
        $('#error').html('please add birthweight');
        return GAEBAdmin.enableForm();
    }

    for (var i = 0; i < GAEBAdmin._photos.length; i++) {
        pics.push(GAEBAdmin._photos[i].key);
        cover = GAEBAdmin._photos[i].key;
    }

    $.post('/animals/angus',
           {
               'key':GAEBAdmin._editKey,
               'pics':pics.join(','),
               'cover':cover,
               'name':$('#name').val(),
               'description':$('#description').val(),
               'number':$('#number').val(),
               'birthdate':$('#birthdate').val(),
               'birthweight':$('#birthweight').val(),
               'stats':GAEBAdmin.makeStats(),
               'lineage':GAEBAdmin.makeLineage()
           },
           function(response) {
               GAEBAdmin.addAnimal(response.data);
               GAEBAdmin.showAnimals();
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
    GAEBAdmin._posts.push(animal);
}

GAEBAdmin.getPosts = function() {
    $.get('/posts', 
          {},
          function(response) {
              console.warn(response);
              GAEBAdmin._posts = response.data;
              GAEBAdmin.showPosts();
          });
};

function addPhoto(photo_key, photo_url) {
    GAEBAdmin._photos.push({'key':photo_key, 'url':photo_url});
    GAEBAdmin.showPhotos();
};

$(document).ready(function() {
    GAEBAdmin._posts = [];
    GAEBAdmin._photos = [];
    GAEBAdmin.clearForm();
    GAEBAdmin.getPosts();

    tinymce.init({
        selector: 'textarea',
        height: 500,
        plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table contextmenu paste code'
        ],
        toolbar: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
        content_css: [
            '//fast.fonts.net/cssapi/e6dc9b99-64fe-4292-ad98-6974f93cd2a2.css',
            '//www.tinymce.com/css/codepen.min.css'
        ]
    });

});
