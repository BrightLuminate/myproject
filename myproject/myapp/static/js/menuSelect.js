
function setActiveMenu(index){

    const menus = $('a.menu')
    $(menus[index]).removeClass("menu")
    $(menus[index]).addClass("menu_on")

    if (index === 0) {
        $("#title").text("모니터링");
    } else if (index === 1) {
        $("#title").text("기기상태");
    } else if (index === 2) {
        $("#title").text("품질관리");
    }
}
