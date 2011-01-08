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

function addSongbox(playlist, container, entry, thumbsUpCallback) {
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
    if (entry.voted) {
      thumbsUpImg.setAttribute('src', '/static/images/voted.png');
    } else {
      thumbsUpImg.setAttribute('src', '/static/images/thumbs-up.png');
      thumbsUpImg.setAttribute('class', 'voteImg');
      thumbsUpImg.onclick = function() {
	thumbsUpCallback(playlist, entry.url, entry.title, entry.thumbnails); 
      }
    }
    thumbsUp.appendChild(thumbsUpImg);
    thumbsUp.appendChild(document.createTextNode(
      entry.count));
    row.appendChild(thumbsUp);
  }

  container.appendChild(row);
  var clearFix = document.createElement('div');
  clearFix.setAttribute('class', 'clearfix');
  clearFix.appendChild(document.createTextNode(' '));
  row.appendChild(clearFix);
}

function addToPlaylist(playlist, url, title, thumbnails) {
  var query = 'p=' + encodeURIComponent(playlist) +
    '&url=' + encodeURIComponent(url) +
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
      // TODO(nav): Update the list differently, maybe using
      // a timer or the channel API.
      doGetPlaylist(playlist);
    }
  }
  req.send(null);
}

function updatePlaylist(playlist, results) {
  var songBoxes = document.getElementById('playlist');
  songBoxes.innerHTML = '';
  for (x in results) {
    addSongbox(playlist, songBoxes, results[x], addToPlaylist);
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
  var ytUrl = 'http://gdata.youtube.com/feeds/api/videos?q=' +
    encodeURIComponent(query) + '&format=5&v=2&alt=jsonc&category=Music&max_results=10' +
    '&orderBy=relevance';
  $.ajax({
    type: "GET",
    url: ytUrl,
    dataType: "jsonp",
    success: function (responseData, textStatus, XMLHttpRequest) {
      if (responseData.data.items) {
	displayVids(playlist, responseData.data.items);
	} else {
	// TODO: no video results
      }
    }
  });
}

function displayVids(playlist, vids) {
  $("#vid-results").empty();
  var vlength = Math.min(vids.length, 10);
  for (var vIdx=0; vIdx<vlength; vIdx++) {
    //var vidItem = $("<div onclick='loadVideo(\""+vids[vIdx].id+"\")' class='vid-item'>");
    var title = vids[vIdx].title;
    title = escape(title);
    var vidItem = $("<div onclick='queueSong(\""+playlist+"\", \""+vids[vIdx].id+"\", \""+title+"\", \""+vids[vIdx].thumbnail.sqDefault+"\");$(\"#vid-results\").hide();' class='vid-item'>");
    vidItem.append($("<img class='vid-img'>").attr("src", vids[vIdx].thumbnail.sqDefault));
    vidItem.append($("<span class='vid-title'>"+vids[vIdx].title+"</span>"));
    $("#vid-results").append(vidItem);
  }
}

function queueSong(playlist, id, title, thumbnail) {
  var thumbnails = [];
  thumbnails.push(thumbnail);
  addToPlaylist(playlist, "http://www.youtube.com/v/" + id + "?enablejsapi=1&playerapiid=ytplayer",
      unescape(title), thumbnails);
}

