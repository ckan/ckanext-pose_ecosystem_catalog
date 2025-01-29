// Enable JavaScript's strict mode. Strict mode catches some common
// programming errors and throws exceptions, prevents some unsafe actions from
// being taken, and disables some confusing and bad JavaScript features.
"use strict";

function toggleSectionTitlesForm(element) {
    if(element && element.value) {
        var form_elements = document.getElementsByClassName("section-titles-form");
        for(var i = 0; i < form_elements.length; i++) {
            form_elements[i].style.display = element.value === '3' ? 'none' : 'block';
        }
    }
}

document.addEventListener("change", function() {
    var element = document.getElementById("field-custom-homepage-layout");
    toggleSectionTitlesForm(element);
});

document.addEventListener("DOMContentLoaded", function() {
    var element = document.getElementById("field-custom-homepage-layout");
    toggleSectionTitlesForm(element);
});