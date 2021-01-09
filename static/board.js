var example = document.getElementById("example"),
ctx = example.getContext('2d');
example.width  = 640;
example.height = 480;

let size = 32
let frame_margin_1 = 2
let frame_margin_2 = 5
let square_count_x = 4
let square_count_y = 4

let matrix1 = [
  [1, 0, 2, 2],
  [2, 0, 1, 1],
  [0, 1, 2, 0],
  [0, 0, 1, 0]
];

let matrix2 = [
  [1, 0, 2, 2],
  [2, 0, 1, 1],
  [0, 1, 2, 0],
  [0, 0, 1, 0]
];

let matrix3 = [
  [1, 0, 2, 2],
  [2, 0, 1, 1],
  [0, 1, 2, 0],
  [0, 0, 1, 0]
];

let matrix4 = [
  [1, 0, 2, 2],
  [2, 0, 1, 1],
  [0, 1, 2, 0],
  [0, 0, 1, 0]
];

pic_X = new Image();
pic_O = new Image();
pic_X.src = 'static/X.png';
pic_O.src = 'static/O.png'

function get_matrix(index, board_data)
{
    // board_data - text string with board position
    // index - square index
    square_string = board_data.substring(16*index, 16*(index+1))
    square_pos = [[],[],[],[]];
    for(var i = 0; i < 16; i++) {
        square_pos[i%4][Math.floor(i/4)] = square_string[i].charCodeAt(0);
    }
    return square_pos
}

class BigSquare{
constructor(start_x, start_y, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y, color) {
    this.start_x = start_x;
    this.start_y = start_y;
    this.size = size;
    this.frame_margin_1 = frame_margin_1;
    this.frame_margin_2 = frame_margin_2;
    this.square_count_x = square_count_x;
    this.square_count_y = square_count_y;
    this.color = color;

    this.frame_1_start_x = this.start_x - this.frame_margin_1;
    this.frame_2_start_x = this.start_x - this.frame_margin_2;
    this.frame_1_start_y = this.start_y - this.frame_margin_1;
    this.frame_2_start_y = this.start_y - this.frame_margin_2;
    this.board_size_x = this.size * this.square_count_x;
    this.board_size_y = this.size * this.square_count_y;
    this.frame_1_size_x = this.board_size_x + 2 * this.frame_margin_1;
    this.frame_1_size_y = this.board_size_y + 2 * this.frame_margin_1;
    this.frame_2_size_x = this.board_size_x + 2 * this.frame_margin_2;
    this.frame_2_size_y = this.board_size_y + 2 * this.frame_margin_2;
}

draw(ar) {
    document.getElementById("debug").value += ar;
    ctx.strokeRect(this.frame_1_start_x, this.frame_1_start_y, this.frame_1_size_x, this.frame_1_size_y);
    ctx.strokeRect(this.frame_2_start_x, this.frame_2_start_y, this.frame_2_size_x, this.frame_2_size_y);
    ctx.fillStyle = this.color; // меняем цвет клеток

    for (let i = 0; i < this.square_count_x; i += 1)
        for (let j = 0; j < this.square_count_y; j += 1) {
            ctx.fillRect(this.start_x + i * this.size, this.start_y + j * this.size, this.size-1, this.size-1);
            if (ar[i][j] == 1) {
                ctx.drawImage(pic_X, this.start_x + i * this.size, this.start_y + j * this.size);
            }
            else if (ar[i][j] == 2) {
                 ctx.drawImage(pic_O, this.start_x + i * this.size, this.start_y + j * this.size);
            }
        }
}

contains(xPos, yPos) {
    return (this.start_x <= xPos) && (this.start_x + this.board_size_x > xPos) &&
            (this.start_y <= yPos) && (this.start_y + this.board_size_y > yPos);
}


getCoords(xPos, yPos) {
    let x_index = Math.floor((xPos - this.start_x) / this.size);
    let y_index = Math.floor((yPos - this.start_y) / this.size);
    return {x: x_index, y: y_index}
}

}


let square1 = new BigSquare(20, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y, '#AF5200');
let square2 = new BigSquare(180, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y, '#AF5200');
let square3 = new BigSquare(340, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y, '#AF5200');
let square4 = new BigSquare(500, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y, '#AF5200');


pic_X.onload = function() {    // Событие onLoad, ждём момента пока загрузится изображение
    square1.draw(matrix1);
    square2.draw(matrix2);
    square3.draw(matrix3);
    square4.draw(matrix4);
}


function windowToCanvas(canvas, x, y) {
    var bbox = canvas.getBoundingClientRect();
    return { x: x - bbox.left * (canvas.width / bbox.width),
        y: y - bbox.top * (canvas.height / bbox.height)
    };
}

example.addEventListener('mousedown', function (e) {
    let res = windowToCanvas(example, e.clientX, e.clientY);
    document.getElementById("debug").value += (" -"+res.x+ "--"+res.y+"- ");
    coords = {
        "square": 0,
        "vertical": 0,
        "horizontal": 0
        }
    if (square1.contains(res.x, res.y)){
        let indexes = square1.getCoords(res.x, res.y)
        coords["square"] = 0;
        coords["vertical"] = indexes.x;
        coords["horizontal"] = indexes.y;
        document.getElementById("debug").value += (" *0**"+indexes.x+ "**"+indexes.y+"* ");
    }
    else if (square2.contains(res.x, res.y)){
        let indexes = square2.getCoords(res.x, res.y)
        coords["square"] = 1;
        coords["vertical"] = indexes.x;
        coords["horizontal"] = indexes.y;
        document.getElementById("debug").value += (" *1**"+indexes.x+ "**"+indexes.y+"* ");
    }
        else if (square3.contains(res.x, res.y)){
        let indexes = square3.getCoords(res.x, res.y)
        coords["square"] = 2;
        coords["vertical"] = indexes.x;
        coords["horizontal"] = indexes.y;
        document.getElementById("debug").value += (" *2**"+indexes.x+ "**"+indexes.y+"* ");
    }
        else if (square4.contains(res.x, res.y)){
        let indexes = square4.getCoords(res.x, res.y)
        coords["square"] = 3;
        coords["vertical"] = indexes.x;
        coords["horizontal"] = indexes.y;
        document.getElementById("debug").value += (" *3**"+indexes.x+ "**"+indexes.y+"* ");
    }
    else {
        document.getElementById("debug").value += (" missed!");
    }
    if (enabled && myMove)
    {
        send_move_coords(coords);
        enabled = false;
        myMove = false;
    }
});

var enabled = false;    // enabled/disable board
var firstPlayer = false; // first/second player
var myMove = false;

function started(player_n, opponent_name)
{
    if (player_n == "second")
    {
        document.getElementById("first_player").textContent  = opponent_name;
        document.getElementById("second_player").textContent = "Me";
        firstPlayer = false;
        myMove = false;
    }
    else
    {
        document.getElementById("first_player").textContent  = "Me";
        document.getElementById("second_player").textContent = opponent_name;
        firstPlayer = true;
        myMove = true;
    }

    enabled = true;
}

function update_state(board, player_to_move, last_move)
{
    if (player_to_move == "second")
    {
        myMove = !firstPlayer;
    }
    else
    {
        myMove = firstPlayer;
    }
    square1.draw(get_matrix(0, board));
    square2.draw(get_matrix(1, board));
    square3.draw(get_matrix(2, board));
    square4.draw(get_matrix(3, board));
}