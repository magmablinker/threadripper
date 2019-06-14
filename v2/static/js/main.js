window.onload = function() {
  loadData("http://127.0.0.1:5000/api/image/random/");
};

function loadData(url) {
  var xhttp = new XMLHttpRequest();
  xhttp.open("GET", url, true);
  xhttp.send();
  xhttp.onreadystatechange = function() {
    if (this.status = 200) {
      window.jsondata = JSON.parse(this.responseText);
      const b64 = jsondata[3];
      var img = document.getElementById("img");
      img.setAttribute('src', "data:image/jpg;base64," + b64)
      img.setAttribute('alt', window.jsondata[2])
    }
  };
}

function newImage(type) {
  var nextId = window.jsondata[0];
  if (type == 0) { // Next image
    nextId++;
  } else { // Previous image
    nextId--;
  }
  loadData("http://127.0.0.1:5000/api/image/" + nextId);
}