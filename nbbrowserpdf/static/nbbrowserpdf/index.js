define([
  "jquery",
  "base/js/namespace"
], function($, Jupyter){
  function load(){
    $("<li/>", {id: "downlaod_browserpdf"}).append(
        $("<a/>")
          .text("PDF via Headless Browser (.pdf)")
          .on("click", function(){
            Jupyter.menubar._nbconvert("browserpdf", true);
          })
      )
      .appendTo($("#download_html").parent());
  }

  return {
    load_ipython_extension: load,
    load_jupyter_extension: load,
  };
});
