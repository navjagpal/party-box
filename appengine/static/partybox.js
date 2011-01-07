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

function AddSongbox(container, title, thumbnails) {
  var clickWrapper = document.createElement('div');
  clickWrapper.setAttribute('class', 'clickWrapper');
  if (thumbnails.length) {
    var thumbnail = document.createElement('div');
    thumbnail.setAttribute('class', 'songThumb');
    var image = document.createElement('img');
    image.setAttribute('class', 'thumbnail');
    image.setAttribute('src', thumbnails[0]);
    thumbnail.appendChild(image);
    clickWrapper.appendChild(thumbnail);
  }
  var songDetails = document.createElement('div');
  songDetails.setAttribute('class', 'songDetails');
  songDetails.appendChild(document.createTextNode(title));
  clickWrapper.appendChild(songDetails);
  var row = document.createElement('div');
  row.setAttribute('class', 'songBox');
  row.appendChild(clickWrapper);
  container.appendChild(row);
  var clearFix = document.createElement('div');
  clearFix.setAttribute('class', 'clearfix');
  clearFix.appendChild(document.createTextNode(' '));
  row.appendChild(clearFix);
}

