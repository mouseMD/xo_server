var example = document.getElementById("example"),
ctx = example.getContext('2d');
example.width  = 640;
example.height = 480;

let size = 25
let frame_margin_1 = 2
let frame_margin_2 = 5
let square_count_x = 4
let square_count_y = 4

function draw_square(start_x, start_y, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y)
{
    let frame_1_start_x = start_x - frame_margin_1
    let frame_2_start_x = start_x - frame_margin_2
    let frame_1_start_y = start_y - frame_margin_1
    let frame_2_start_y = start_y - frame_margin_2
    let board_size_x = size*square_count_x
    let board_size_y = size*square_count_y
    let frame_1_size_x = board_size_x + 2*frame_margin_1
    let frame_1_size_y = board_size_y + 2*frame_margin_1
    let frame_2_size_x = board_size_x + 2*frame_margin_2
    let frame_2_size_y = board_size_y + 2*frame_margin_2


    ctx.strokeRect(frame_1_start_x, frame_1_start_y, frame_1_size_x, frame_1_size_y);
    ctx.strokeRect(frame_2_start_x, frame_2_start_y, frame_2_size_x, frame_2_size_y);
    ctx.fillStyle = '#AF5200'; // меняем цвет клеток

    for (i = 0; i < square_count_x; i += 1)
        for (j = 0; j < square_count_y; j += 1) {
            ctx.fillRect(start_x + i * size, start_y + j * size, size-1, size-1);
        }
}

draw_square(20, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y)
draw_square(180, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y)
draw_square(340, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y)
draw_square(500, 20, size, frame_margin_1, frame_margin_2, square_count_x, square_count_y)


pic = new Image();              // "Создаём" изображение
pic.src    = 'http://habrahabr.ru/i/nocopypast.png';  // Источник изображения, позаимствовано на хабре
pic.onload = function() {    // Событие onLoad, ждём момента пока загрузится изображение
   //ctx.drawImage(pic, 0, 0);  // Рисуем изображение от точки с координатами 0, 0
   //ctx.drawImage(pic, 0, 0, 300, 150);
   //ctx.drawImage(pic, 25, 42, 85, 55, 0, 0, 170, 110);
}

function windowToCanvas(canvas, x, y) {
    var bbox = canvas.getBoundingClientRect();
    return { x: x - bbox.left * (canvas.width / bbox.width),
        y: y - bbox.top * (canvas.height / bbox.height)
    };
}

example.addEventListener('mousedown', function (e) {
    res = windowToCanvas(example, e.clientX, e.clientY);
    document.getElementById("debug").value += (res.x+ "  ");

});