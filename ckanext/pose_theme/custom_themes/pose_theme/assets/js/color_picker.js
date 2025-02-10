jQuery(document).ready(function () {
    function initColorSelector() {
        $( ".pose-theme-color-picker").each(function( index ) {
            $(this).spectrum({
                showInput: true, // shows the color input box, which actually can take hex,  hsl, and rgb
                showPaletteOnly: true, // only shows the color selectors
                hideAfterPaletteSelect: true,
                preferredFormat: "hex", // sets the format of color input box
                palette:[
                    ["#1F76D8","#165CAB","#044187","#07305C","#FFFFFF","#9A9DA1","#616365","#131517"],
                    ["#990000","#B45F06","#BF9000","#38761D","#45818E","#3D85C6","#674EA7","#A64D79"]
                ]
            });
        });
    }
    initColorSelector()
})
