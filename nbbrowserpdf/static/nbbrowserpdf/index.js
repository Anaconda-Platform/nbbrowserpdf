define(["jquery"], function($){
  function load(){
    console.log("nbbrowserpdf loaded!");
  }

  return {
    load_ipython_extension: load,
    load_jupyter_extension: load,
  };
});
