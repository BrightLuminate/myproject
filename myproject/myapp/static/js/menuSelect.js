
function setActiveMenu(index){
    // $(menus[index]).removeClass( "menu_on" );

    const menus = $('a.menu')
    $(menus[index]).removeClass( "menu" );
    $(menus[index]).addClass("menu_on")
}
