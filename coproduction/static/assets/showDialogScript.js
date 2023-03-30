var openDialog = function (event) {
  event.preventDefault();
  var id = "";
  let dialogId = event.target.getAttribute("dialogId");
  var dialog = document.getElementById(dialogId);
  dialog.style.display = "block";
};
var closeDialog = function (event) {
  event.preventDefault();
  let dialogId = event.target.getAttribute("dialogId");
  var dialog = document.getElementById(dialogId);
  dialog.style.display = "none";
};
