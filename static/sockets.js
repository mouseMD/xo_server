let socket = new WebSocket("ws://0.0.0.0:8080/ws");

function send_ready() {
    let ready_message = {
    version: "v1",
    command: "ready",
    parameters: {
        type: "xo_3d",
        opponent: "random"
        }
    };
    let payload = JSON.stringify(ready_message);
    socket.send(payload);
};

function send_move() {
    let move_message = {
    version: "v1",
    command: "move",
    parameters: {
        "square": 0,
        "vertical": 0,
        "horizontal": 0
        }
    };
    let payload = JSON.stringify(move_message);
    socket.send(payload);
};

function send_resign() {
    let resign_message = {
    version: "v1"
    command: "resign"
    };
    let payload = JSON.stringify(resign_message);
    socket.send(payload);
};

function send_offer() {
    let offer_message = {
    version: "v1"
    command: "offer"
    };
    let payload = JSON.stringify(offer_message);
    socket.send(payload);
};

function handle_started(cm_data)
{
    let player_n = cm_data.player_n;
    let opponent_name = cm_data.opponent_name;
    alert(`Game started as ${player_n} player. Opponent name is ${opponent_name}`);
};

function handle_update_state(cm_data)
{
    let board = cm_data.board;
    let player_to_move = cm_data.player_to_move;
    let last_move = cm_data.last_move;
    alert(`Game started updated! Board now is ${board}, player to move is ${player_to_move}. Last move is ${last_move}`);
};

function handle_offered(cm_data)
{
    alert('You were offered a draw');
};

function handle_game_over(cm_data)
{
    let result = cm_data.result;
    let win_pos = cm_data.win_pos;
    alert(`The result is ${result}. Win pos is ${win_pos}`);
}


socket.onopen = function(e)
{
    alert("[open] Connection established");
    send_ready();
};

socket.onmessage = function(e)
{
    alert(`[message] Data received: ${e.data}`);
    let cmd_data = JSON.parse(e.data)
    if (cmd_data.version == "v1")
    {
        switch (cmd_data.command) {
          case 'started':
            handle_started(cmd_data.parameters);
            break;
          case 'update_state':
            handle_update_state(cmd_data.parameters);
            break;
          case 'offered':
            handle_offered(cmd_data.parameters);
            break;
          case 'game_over':
            handle_game_over(cmd_data.parameters);
            break;
    }
    else
    {
        alert("Wrong protocol version!");
    }
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