async function fetch_users() {
    // get from server
    let response = await fetch('/users', {
        method: 'GET',
    });
    let result = await response.json();
    console.log(result);
    // update DOM
    list = document.getElementById("active-users-list");
    var listElement = document.getElementById("list-element");
    if (listElement){
        while(listElement.firstChild) listElement.removeChild(listElement.firstChild);
    }
    else {
        listElement = document.createElement('ul');
        listElement.id = "list-element";
        list.appendChild(listElement);
    }
    for (var i = 0; i < result.length; i++) {
        listItem = document.createElement('li');
        listItem.innerHTML = result[i].login + "   |   " + result[i].created_at;
        listElement.appendChild(listItem);
    }
}

let timerId = setInterval(fetch_users, 10000);
fetch_users();
