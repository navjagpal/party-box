// Upon loading, the Google APIs JS client automatically invokes this callback.
googleApiClientReady = function() {
  console.log('ApiClientReady');
  // Load the client interfaces for the YouTube Analytics and Data APIs, which
  // are required to use the Google APIs JS client. More info is available at
  // https://developers.google.com/api-client-library/javascript/dev/dev_jscript#loading-the-client-library-and-the-api
  gapi.client.load('youtube', 'v3', function() {
    console.log('YouTube API loaded');
  });
}

function doGetPlaylist(playlist) {
  var req = new XMLHttpRequest();
  var query = 'p=' + encodeURIComponent(playlist);
  req.open('GET', '/youtube/playlist?' + query, true);
  req.onreadystatechange = function() {
    if (req.readyState == 4 && req.status == 200) {
      var response = JSON.parse(req.responseText);
      updatePlaylist(playlist, response);
    }
  }
  req.send(null);
}

function createSongbox(playlist, entry) {
  var clickWrapper = document.createElement('div');
  clickWrapper.setAttribute('class', 'clickWrapper');
  if (entry.thumbnails.length) {
    var thumbnail = document.createElement('div');
    thumbnail.setAttribute('class', 'songThumb');
    var image = document.createElement('img');
    image.setAttribute('class', 'thumbnail');
    image.setAttribute('src', entry.thumbnails[0]);
    thumbnail.appendChild(image);
    clickWrapper.appendChild(thumbnail);
  }
  var songDetails = document.createElement('div');
  songDetails.setAttribute('class', 'songDetails');
  songDetails.appendChild(document.createTextNode(entry.title));
  clickWrapper.appendChild(songDetails);
  var row = document.createElement('div');
  row.setAttribute('class', 'songBox');
  row.setAttribute('id', 'songBox-' + entry.id);
  row.appendChild(clickWrapper);

  var thumbsUp = document.createElement('div');
  thumbsUp.setAttribute('class', 'thumbs thumbUpSong');
  var thumbsUpImg = document.createElement('img');
  if (entry.voted) {
    thumbsUpImg.setAttribute('src', '/static/images/voted.png');
  } else if (!entry.nowPlaying && !entry.random) {
    thumbsUpImg.setAttribute('src', '/static/images/thumbs-up.png');
    thumbsUpImg.setAttribute('class', 'voteImg');
    thumbsUpImg.onclick = function() {
      addToPlaylist(playlist, entry.id, entry.title, entry.thumbnails); 
    }
  }
  thumbsUp.appendChild(thumbsUpImg);
  // Random songs don't have counts.
  if (entry.count != undefined) {
    thumbsUp.appendChild(document.createTextNode(
      entry.count));
  }
  row.appendChild(thumbsUp);

  var clearFix = document.createElement('div');
  clearFix.setAttribute('class', 'clearfix');
  clearFix.appendChild(document.createTextNode(' '));
  row.appendChild(clearFix);
  return row;
}

function addSongbox(playlist, container, entry) {
  container.appendChild(createSongbox(playlist, entry));
}

function addToPlaylist(playlist, id, title, thumbnails) {
  var query = 'p=' + encodeURIComponent(playlist) +
    '&id=' + encodeURIComponent(id) +
    '&title=' + encodeURIComponent(title);
  if (thumbnails.length)
    query = query + '&thumbnail=' + encodeURIComponent(thumbnails[0]);
  var req = new XMLHttpRequest();
  req.open('GET', '/youtube/add?' + query, true);
  req.onreadystatechange = function() {
    if (req.readyState == 4 && req.status == 200) {
      var response = JSON.parse(req.responseText);
      if (response.message) {
	alert(response.message);
      }
      updateOrAddSongbox(playlist, response.entry);
    }
  }
  req.send(null);
}

function updateOrAddSongbox(playlist, entry) {
  var songBox = document.getElementById('songBox-' + entry.id);
  if (songBox == undefined) {
    var songBoxes = document.getElementById('playlist');
    addSongbox(playlist, songBoxes, entry);
  } else {
    songBox.parentNode.replaceChild(createSongbox(playlist, entry),
      songBox); 
  }
}

function updatePlaylist(playlist, results) {
  var songBoxes = document.getElementById('playlist');
  songBoxes.innerHTML = '';
  for (x in results) {
    addSongbox(playlist, songBoxes, results[x]);
  }
}

function getHeight() {
  // -25px for the margins / paddings
  return $(window).height() - $("#grBoxHeader").height() - 
	 $("#videoPlayerHeader").height() - 20;
}

function getWidth() {
  // -something for the margins / paddings
  return $(window).width() - $("#rightContent").width() - 25;
} 

function adjustVideoSize() {
  $("#ytplayerObj").attr("height", getHeight()); 
  $("#ytplayerObj").attr("width", getWidth()); 
}

function adjustSize() {
  var height = $(window).height() - $('#grBoxHeader').height();
  var width = $(window).width();
  $("#videoPlayerBox").css("height", getHeight() + 35);
  $("#videoPlayerBox").css("width", getWidth());
  $("#mainContent").css("width", width);
  $("#mainContent").css("height", height);
  $("#songBoxes").css("height", height - $("#adsense").height() - 15);
  adjustVideoSize();  
}

function getQRCode(url) {
  return 'http://qrcode.kaywa.com/img.php?s=8&d=' +
    encodeURIComponent(url);
}

function ytsearch(playlist, query) {
  var request = gapi.client.youtube.search.list({
    key: 'AIzaSyA8OdrL9Xh0ebjKWOMVrnzRP_pw9TaTuws',
    q: query,
    videoCategoryId: 10,
    type: 'video',
    part: 'id,snippet'
  });
  request.execute(function(response) {
    console.log(JSON.stringify(response.result));
    console.log('Result length:' + response.result.items.length);
    $("#vid-results").empty();
    for (var i = 0; i < response.result.items.length; i++) {
      var item = response.result.items[i];
      var title = item.snippet.title;
      var videoId = item.id.videoId;
      var thumbnail = item.snippet.thumbnails.default.url;
      var vid = document.createElement('div');
      vid.setAttribute('class', 'vid-item');
      vid.addEventListener('click', function() {
        queueSong(playlist, videoId, title, thumbnail);
        $('#vid-results').hide(); 
      });
      var thumbnailImage = document.createElement('img');
      thumbnailImage.setAttribute('class', 'vid-img');
      thumbnailImage.setAttribute('src', thumbnail);
      vid.appendChild(thumbnailImage);
      var titleSpan = document.createElement('span');
      titleSpan.setAttribute('class', 'vid-title');
      titleSpan.appendChild(document.createTextNode(title));
      vid.appendChild(titleSpan);
      $('#vid-results').append(vid);
    }
  });
}

function queueSong(playlist, id, title, thumbnail) {
  var thumbnails = [];
  thumbnails.push(thumbnail);
  addToPlaylist(playlist, id, unescape(title), thumbnails);
}

