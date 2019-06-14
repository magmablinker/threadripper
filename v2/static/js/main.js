
      window.onload = function(){
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
        if(type == 0) {  // Next image
          nextId++;
        } else { // Previous image
          nextId--;
        }
        loadData("http://127.0.0.1:5000/api/image/" + nextId);
      }

      var modal = document.getElementById("myModal");
      var img = document.getElementById("img");
      var modalImg = document.getElementById("img01");
      var captionText = document.getElementById("caption");
      img.onclick = function(){
        modal.style.display = "block";
        modalImg.src = this.src;
        captionText.innerHTML = this.alt;
      }

      function closeModal() {
        modal.style.display = "none";
      }

      function loadImage() {
        var img = document.getElementById("img");
        modalImg.src = img.src;
      }

      var span = document.getElementsByClassName("close")[0];
      span.onclick = function(){
        modal.style.display = "none";
      }

      document.onkeydown = checkKey;
      function checkKey(e) {
        e = e || window.event;
        if(e.keyCode == "37") {
          newImage(1);
          window.setTimeout(function () {
            loadImage();
          }, 100);
        } else if(e.keyCode == "39") {
          newImage(0);
          window.setTimeout(function () {
            loadImage();
          }, 100);
        } else if(e.keyCode == "27") {
          closeModal();
        }

      }
