var list = document.getElementById('demo');
var lastid = 0;

function changeText2() {
    var firstname = document.getElementById('firstname').value;
    document.getElementById('boldStuff2').innerHTML = firstname;
    var entry = document.createElement('li');
    entry.appendChild(document.createTextNode(firstname));
    entry.setAttribute('id','item'+lastid);
    var removeButton = document.createElement('button');
    removeButton.appendChild(document.createTextNode("remove"));
    removeButton.setAttribute('onClick','removeName("'+'item'+lastid+'")');
    entry.appendChild(removeButton);
    lastid+=1;
    list.appendChild(entry);
}


function removeName(itemid){
    var item = document.getElementById(itemid);
    list.removeChild(item);
}