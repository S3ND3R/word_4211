'use strict';

function get_def(word) {
  var data
  var def_display = document.querySelector("#modal-content")
  def_display.innerHTML = ""
  fetch(`/${word.name}`)
    .then(response => {
      return response.json();
    })
    .then( data => {
      const word_d = document.createElement('p')
      word_d.innerHTML = `${word.name}`
      word_d.style.color = "blue";
      word_d.style.fontSize = "large";
      word_d.style.fontWeight = "bold";
      def_display.appendChild(word_d)
      var def_num = 0;
      data.forEach(dict => {
        if (dict.date) {
          const date = document.createElement('h3')
          date.innerHTML = `From-${dict.date}`
          def_display.appendChild(date)
        }
        if (dict.shortdef) {
          dict.shortdef.forEach(def => {
            def_num++
            const entry = document.createElement('p')
            entry.innerHTML = `${def_num}   : ${def}`
            def_display.appendChild(entry)
          })// end inner dict defs
        }
      })// dict loops
      if (def_num < 1) {
        const entry = document.createElement('p')
        entry.innerHTML = `definition not found...`
        def_display.appendChild(entry)
      }
    }) // end .then data
    .catch(err => {
      console.log("ERROR FOUND");
    });
  var box = document.querySelector(".modal")
  box.style.display = "block";
} // end get_def

function close_box() {
  var box = document.querySelector(".modal")
  box.style.display = "none";
}
