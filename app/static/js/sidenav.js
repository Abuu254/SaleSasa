

// left side

var x =document.getElementById("my_menu_1");
var y =document.getElementById("my_menu_2");
y.style.display = 'none';

function openNav() {
  document.getElementById("mySidenav").setAttribute(
    "style", "left: 0; visibility: visible; transform: none;"
  );
  document.getElementById("mySidenav").setAttribute("aria-hidden", "false");
  document.getElementById("mySidenav").setAttribute("aria-modal", "true");
  document.getElementById("mySidenav").setAttribute("role", "dialog");
  document.getElementById("myRightnav").style.right= "-800px";
  x.style.display = 'none';
  y.style.display = '';
}

function closeNav() {
  document.getElementById("mySidenav").style.left = "-800px";
  x.style.display = '';
  y.style.display = 'none';
}

// right side

var a =document.getElementById("my_user_1");
var b =document.getElementById("my_user_2");
b.style.display = 'none';

function openRight() {
  document.getElementById("myRightnav").setAttribute(
    "style", "right: 0; visibility: visible; transform: none;"
  );
  document.getElementById("myRightnav").setAttribute("aria-hidden", "false");
  document.getElementById("myRightnav").setAttribute("aria-modal", "true");
  document.getElementById("myRightnav").setAttribute("role", "dialog");
  document.getElementById("mySidenav").style.left= "-800px";
  a.style.display = 'none';
  b.style.display = '';
}

function closeRight() {
  document.getElementById("myRightnav").style.right = "-400px";
  a.style.display = '';
  b.style.display = 'none';
}


