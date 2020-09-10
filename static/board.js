var example = document.getElementById("example"),
ctx = example.getContext('2d');
example.width  = 640;
example.height = 480;

let size = 32
let frame_margin_1 = 2
let frame_margin_2 = 5
let square_count_x = 4
let square_count_y = 4

let matrix = [
  [1, 0, 2, 2],
  [2, 0, 1, 1],
  [0, 1, 2, 0],
  [0, 0, 1, 0]
];

pic_X = new Image();
pic_O = new Image();
pic_X.src = 'static/X.png';
pic_O.src = 'static/O.png'


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
   square1.draw(matrix);
square2.draw(matrix);
square3.draw(matrix);
square4.draw(matrix);
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
    if (square1.contains(res.x, res.y)){
        let indexes = square1.getCoords(res.x, res.y)
        document.getElementById("debug").value += (" *0**"+indexes.x+ "**"+indexes.y+"* ");
    }
    else if (square2.contains(res.x, res.y)){
        let indexes = square2.getCoords(res.x, res.y)
        document.getElementById("debug").value += (" *1**"+indexes.x+ "**"+indexes.y+"* ");
    }
        else if (square3.contains(res.x, res.y)){
        let indexes = square3.getCoords(res.x, res.y)
        document.getElementById("debug").value += (" *2**"+indexes.x+ "**"+indexes.y+"* ");
    }
        else if (square4.contains(res.x, res.y)){
        let indexes = square4.getCoords(res.x, res.y)
        document.getElementById("debug").value += (" *3**"+indexes.x+ "**"+indexes.y+"* ");
    }
    else {
        document.getElementById("debug").value += (" missed!");
    }
});