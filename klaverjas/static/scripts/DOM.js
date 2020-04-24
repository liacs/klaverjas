"use strict";


let DOM = {};


(function() {
    DOM.create_element = function(type, class_name) {
        const $el = document.createElement(type);
        $el.className = class_name;
        return $el;
    };
})();


export {
    DOM
}
