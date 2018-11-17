"use strict";

var script = function () {

  var gStartDateMS; // the Sunday (day 0) of the first week (week 0) of the term (in milliseconds)


  function init() {
  	console.log('init');
    window.onload = function() {  	
	    processClass('stable', setupSchedTable);
	    processClass('srow', setupSchedRow);
    }
  }

  var processClass = function(name, func) {
    var els = document.getElementsByClassName(name);
    for (var i = 0; i < els.length; i++)
      func(els[i]);
  }

  // construct environment to evaluate function:
  // setup variables and return value.
  var callFunction = function(functxt, vars) {
    var ftxt = vars + " return " + functxt;
    try { 
      var result = new Function(ftxt)();
      return result;
    }
    catch(err) {
      console.log("Error in funciton", ftxt);
      console.log(err);
    }
  }

  var setupSchedTable = function(elem) {
    var date = elem.getAttribute("date");
    date = JSON.parse(date);

    // create date for sunday of the first week (week 0) of the semester
    gStartDateMS = new Date(date[0], date[1] - 1, date[2], 12).getTime();
  }

  var setupSchedRow = function(elem) {
    var arrayTxt = elem.getAttribute("data");
    var localVars = 'm=1; t=2; w=3; r=4; f=5; ';
    var items = callFunction(arrayTxt, localVars);

    // add empty item to the last row if not there.
    if (items.length == 2)
      items.push('')

    // items[0] help form the proper date
    var week = items[0][0]; // the week number of the semester (starting with 0)
    var day = items[0][1];  // the day of the week (monday = 1, tuesday = 2, ...)
    var MSPerDay = 1000*60*60*24;

    // create the date for this day
    var date = new Date( gStartDateMS + (day + week * 7) * MSPerDay );
    var options = { weekday:'short', month: 'short', day: 'numeric'};
    var dateTxt = date.toLocaleDateString('en-US', options);

    // write back the string with proper date formatting back into first column
    items[0] = dateTxt;

    // create table elements
    var output = '';
    for (var i = 0; i < items.length; i++) {
      var item = items[i] ? items[i] : '';
    	output += '<td>' + item + '</td>'; 
    }

    // highlight even weeks
    if (week % 2 == 0)
      elem.classList.add("dark");

    elem.innerHTML = output;
  }


  return { init:init }

}()


