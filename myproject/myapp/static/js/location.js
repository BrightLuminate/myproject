window.onload=function(){
    const ros = new ROSLIB.Ros({
        url: 'ws://192.168.0.11:9090'
    });

    ros.on('error', function(error) { console.log( error ); });
    ros.on('connection', function() { console.log("연결이 잘 되었습니다!"); });

    // Subscribe to Battery Status
    var batteryStatus = new ROSLIB.Topic({
        ros: ros,
        name: '/voltage',
        messageType: 'jetbotmini_msgs/Battery',
    });

    batteryStatus.subscribe(function(e) {
        const battery_per = Math.floor(e.Voltage/12.5*100) ;
        // document.getElementById('battery').innerHTML = battery_per+'%';
        document.getElementsByClassName('battery')[0].innerHTML = battery_per+'%';
        // document.getElementsByClassName('battery')[1].innerHTML = battery_per+'%';
        // document.getElementsByClassName('battery')[2].innerHTML = battery_per+'%';
        // document.getElementsByClassName('battery')[3].innerHTML = battery_per+'%';
        // document.getElementsByClassName('battery')[4].innerHTML = battery_per+'%';
        // document.getElementsByClassName('battery')[5].innerHTML = battery_per+'%';
        // document.getElementsByClassName('battery')[6].innerHTML = battery_per+'%';
        // document.getElementsByClassName('battery')[7].innerHTML = battery_per+'%';
        console.log(e)
    });

    const batteryLevelListener = new ROSLIB.Topic({
        ros : ros,
        name : '/qr',
        messageType : 'std_msgs/String'
    });

    batteryLevelListener.subscribe(function(message) {
        // document.getElementById('qr').innerHTML = message.data;
        document.getElementsByClassName('qr')[0].innerHTML = message.data.split(',')[1];
        // document.getElementsByClassName('qr')[1].innerHTML = message.data.split(',')[1];
        // document.getElementsByClassName('qr')[2].innerHTML = message.data.split(',')[1];
        // document.getElementsByClassName('qr')[3].innerHTML = message.data;
        // document.getElementsByClassName('qr')[4].innerHTML = message.data;
        // document.getElementsByClassName('qr')[5].innerHTML = message.data;
        // document.getElementsByClassName('qr')[6].innerHTML = message.data;
        // document.getElementsByClassName('qr')[7].innerHTML = message.data;
        
        const navPointer = `
        <img class="a" 
        style="position: absolute; z-index: 300; width: 27px; bottom:17px; right: -8px;"
        src="http://127.0.0.1:8000/static/img/location_on.svg"/>
        <i type="button" class="dot_blue_on"></i>
        `
        const navPointer2 = `
        <img class="a" 
        style="position: absolute; z-index: 300; width: 25px; bottom:10px; left: -8.5px;"
        src="http://127.0.0.1:8000/static/img/location_on.svg"/>
        <i type="button" class="dot_blue_on"></i>
        `

        let location_on = document.querySelectorAll(".map_box > div");
        console.log("location_on", location_on)

        location_on.forEach(function(item){
            if(item.classList.contains(message.data.split(',')[1])){
                item.innerHTML = navPointer
            }else{
                item.innerHTML = `<i type="button" class="dot_blue"></i>`
            }
        })
        
        let location_on2 = document.querySelectorAll(".item02 > .map_box > div");
        // console.log("location_on", location_on)

        location_on2.forEach(function(item2){
            if(item2.classList.contains(message.data.split(',')[1])){
                item2.innerHTML = navPointer2
            }else{
                item2.innerHTML = `<i type="button" class="dot_blue"></i>`
            }
        })
 
        // <img class="a" style="position: absolute; z-index: 300; width: 25px; bottom:10px; right: -8.5px;" src="http://127.0.0.1:8000/static/img/location_on.svg"/><i type="button" class="dot_blue"></i>


        console.log(message)
    });
}
