(function(_jq) { 
    "use strict";
    _0xc6e8x7();
    _0xc6e8x6();
    window["sr"] = new scrollReveal(); 

    if (_jq(".menu-trigger")["length"]) {
        _jq(".menu-trigger")["on"]("click", function() { 
            _jq(this)["toggleClass"]("active");
            _jq(".header-area .nav")["slideToggle"](200) 
        }) 
    };

    _jq("a[href*=\\#]:not([href=\\#])")["on"]("click", function() { 
        // if (location["pathname"]["replace"](/^\\/ / , "") == this["pathname"]["replace"](/^\\/ / , "") && location["hostname"] == this["hostname"]) { 
        //     var _0xc6e8x4 = _jq(this["hash"]);
        //     _0xc6e8x4 = _0xc6e8x4["length"] ? _0xc6e8x4 : _jq("[name=" + this["hash"]["slice"](1) + "]");
        //     if (_0xc6e8x4["length"]) { 
        //         var _0xc6e8x5 = _jq(window)["width"]();
        //         if (_0xc6e8x5 < 991) { 
        //             _jq(".menu-trigger")["removeClass"]("active");
        //             _jq(".header-area .nav")["slideUp"](200) 
        //         };
        //         _jq("html,body")["animate"]({ 
        //             scrollTop: (_0xc6e8x4["offset"]()["top"]) - 100 }, 700); 
        //         return false 
        //     } 
        // } 
    }); 

    // if (_jq(".home-seperator")["length"]) { 
    //     _jq(".home-seperator .left-item, .home-seperator .right-item")["imgfix"]() 
    // }; 

    if (_jq(".count-item")["length"]) { 
        _jq(".count-item strong")["counterUp"]({ delay: 10, time: 1000 }) 
    };

    // if (_jq(".blog-post-thumb")["length"]) { 
    //     _jq(".blog-post-thumb .img")["imgfix"]() 
    // }; 

    // if (_jq(".sidebar .box")["length"]) { 
    //     _jq(".sidebar .box")["imgfix"]() }; 

    //     if (_jq(".page-gallery")["length"] && _jq(".page-gallery-wrapper")["length"]) { 
    //         _jq(".page-gallery")["imgfix"]({ scale: 1.1 });
        
    //     _jq(".page-gallery")["magnificPopup"]({ 
    //         type: "image",
    //         gallery: { enabled: true },
    //         zoom: { enabled: true, duration: 300, easing: "ease-in-out" } 
    //     }) 
    // };
    
    _jq(window)["on"]("load", function() { 
        if (_jq(".cover")["length"]) { 
            _jq(".cover")["parallax"]({ 
                imageSrc: _jq(".cover")["data"]("image"), 
                zIndex: "1" 
            }) 
        };
        
        _jq("#preloader")["animate"]({ "opacity": "0" }, 600, function() { 
            setTimeout(function() { 
                if (_jq("#parallax-text")["length"]) { 
                    _jq("#parallax-text")["parallax"]({ 
                        imageSrc: "assets/images/photos/parallax-counter.jpg", 
                        zIndex: "1" 
                    }) 
                }; 

                if (_jq("#counter")["length"]) { 
                    _jq("#counter")["parallax"]({ 
                        imageSrc: "assets/images/photos/parallax-counter.jpg", 
                        zIndex: "1" 
                    }) 
                };
                
                _jq("#preloader")["css"]("visibility", "hidden")["fadeOut"]() }, 300) }) });
    
    _jq(window)["on"]("scroll", function() { _0xc6e8x7() });
    _jq(window)["on"]("resize", function() { _0xc6e8x6() });

    function _0xc6e8x6() { 
        var _0xc6e8x5 = _jq(window)["width"]();
        _jq(".submenu")["on"]("click", function() {
            if (_0xc6e8x5 < 992) { 
                _jq(".submenu ul")["removeClass"]("active");
                _jq(this)["find"]("ul")["toggleClass"]("active") 
            } 
        }) 
    }

    function _0xc6e8x7() { 
        var _0xc6e8x5 = _jq(window)["width"]();
        if (_0xc6e8x5 > 991) { 
            var _0xc6e8x8 = _jq(window)["scrollTop"]();
            if (_0xc6e8x8 >= 30) { 
                _jq(".header-area")["addClass"]("header-sticky");
                _jq(".header-area .dark-logo")["css"]("display", "block");
                _jq(".header-area .light-logo")["css"]("display", "none") 
            } else { 
                _jq(".header-area")["removeClass"]("header-sticky");
                _jq(".header-area .dark-logo")["css"]("display", "none");
                _jq(".header-area .light-logo")["css"]("display", "block") 
            } 
        } 
    } 
})(window["jQuery"])