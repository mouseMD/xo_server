let socket = new WebSocket("ws://0.0.0.0:8080/ws");

socket.onopen = function(e)
{
    alert("[open] Connection established");
    socket.send("My name is Denis");
};

socket.onmessage = function(e)
{
    alert(`[message] Data received: ${e.data}`);
};

socket.onclose = function(e)
{
    if (e.wasClean)
    {
        alert(`[close] Connection closed clean, code=${e.code} reason=${e.reason}`);
    }
    else
    {
        alert('[close] Connection interrupted');
    }
};

socket.onerror = function(e)
{
    alert(`[error] ${e.message}`);
};