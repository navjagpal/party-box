function DoGetPlaylist(playlist, callback) {
  var req = new XMLHttpRequest();
  var query = 'p=' + encodeURIComponent(playlist);
  req.open('GET', '/youtube/playlist?' + query, true);
  req.onreadystatechange = function() {
    if (req.readyState == 4 && req.status == 200) {
      var response = JSON.parse(req.responseText);
      callback(response);
    }
  }
  req.send(null);
}

function AddSongbox(container, entry, thumbsUpCallback) {
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
  row.appendChild(clickWrapper);

  if (thumbsUpCallback != undefined) {
    var thumbsUp = document.createElement('div');
    thumbsUp.setAttribute('class', 'thumbs thumbUpSong');
    var thumbsUpImg = document.createElement('img');
    thumbsUpImg.setAttribute('src', '/static/images/thumbs-up.png');
    thumbsUpImg.onclick = function() {
      thumbsUpCallback(entry.url, entry.title, entry.thumbnails); 
    }
    thumbsUp.appendChild(thumbsUpImg);
    row.appendChild(thumbsUp);
  }

  container.appendChild(row);
  var clearFix = document.createElement('div');
  clearFix.setAttribute('class', 'clearfix');
  clearFix.appendChild(document.createTextNode(' '));
  row.appendChild(clearFix);
}

