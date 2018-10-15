window.requestAnimationFrame = window.requestAnimationFrame       ||
                               window.mozRequestAnimationFrame    ||
                               window.webkitRequestAnimationFrame ||
                               window.msRequestAnimationFrame;
window.onload = start;


const width = 177;
const height = 177;
const offset = 6;
const cellSize = 4;
const speed = 30;
const WALL = 0;
const TREE = 1;
const PATH = 2;

var canvas;
var ctx;
var unexplored = [];  // cells to explore
var grid = new Array(width);  // the maze grid
var currPath;  // path of current random walk

function start() {
    init();
    loop();
}

function init() {
    canvas = document.getElementById("wilson");
    ctx = canvas.getContext("2d");
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.translate(offset, offset);

    for (var y = 0; y < height; y += 2) {
        for (var x = 0; x < width; x += 2) {
            unexplored.push([x, y]);
        }
    }

    // initially all cells are walls
    for (var i = 0; i < width; i++) {
        grid[i] = new Array(height).fill(WALL);
    }

    var root = unexplored.shift();
    ctx.fillStyle = "#FFF";
    markCell(root, TREE);

    ctx.fillStyle = "#F0F";
}

function loop() {
    for (var k = 0; k < speed; k++) {
        if (loopErasedRandomWalk()) {
            return;
        }
    }
    window.requestAnimationFrame(loop);
}

function loopErasedRandomWalk() {
    if (currPath == null) {
        // choose a new cell that is not in the tree
        do {
            current = unexplored.shift();
            if (current == null)
                return true;
        } while (inTree(current));
        markCell(current, PATH);
        currPath = [current];
        return;
    }

    var current = currPath[currPath.length - 1];
    var next = randomNeighbour(current);

    if (inPath(next)) {
        var index = findCellIndex(currPath, next);
        ctx.save();
        ctx.fillStyle = "#000";
        for (var i = index + 1; i < currPath.length; i++) {
            markCell(currPath[i], WALL);
            if (i < currPath.length - 1) {
                markSpace(currPath[i], currPath[i+1], WALL);
            }
        }
        markSpace(currPath[index], currPath[index+1], WALL);
        currPath = currPath.slice(0, index + 1);
        ctx.restore();
        return;
    }

    else if (inTree(next)) {
        ctx.save();
        ctx.fillStyle = "#FFF"
        for (var i = 0; i < currPath.length; i++) {
            markCell(currPath[i], TREE);
            if (i < currPath.length - 1) {
                markSpace(currPath[i], currPath[i+1], TREE);
            }
        }
        markSpace(current, next, TREE);
        ctx.restore();
        currPath = null;
    }

    else {  // add this cell to the path
        markCell(next, PATH);
        markSpace(current, next, PATH);
        currPath.push(next);
    }
}

function markCell(cell, value) {
    var [x, y] = cell;
    grid[x][y] = value;
    ctx.fillRect(x * cellSize, (height - y - 1) * cellSize, cellSize, cellSize);
}

function markSpace(c1, c2, value) {
    var x = (c1[0] + c2[0]) / 2;
    var y = (c1[1] + c2[1]) / 2;
    ctx.fillRect(x * cellSize, (height - y - 1) * cellSize, cellSize, cellSize);
}

function getCell(cell) {
    var [x, y] = cell;
    return grid[x][y];
}

function randomNeighbour(cell) {
    var [x, y] = cell;
    var neighbours = [];
    if (x >= 2) {
        neighbours.push([x - 2, y]);
    }
    if (y >= 2) {
        neighbours.push([x, y - 2]);
    }
    if (x <= width -3) {
        neighbours.push([x + 2, y]);
    }
    if (y <= height -3) {
        neighbours.push([x, y + 2]);
    }
    return neighbours[Math.floor(Math.random() * neighbours.length)];
}

function isWall(cell) {
    return getCell(cell) === WALL;
}

function inTree(cell) {
    return getCell(cell) === TREE;
}

function inPath(cell) {
    return getCell(cell) === PATH;
}

function findCellIndex(path, cell) {
    for (var i=0; i<path.length; i++) {
        var item = path[i];
        if (item[0] === cell[0] && item[1] === cell[1]) {
            return i;
        }
    }
    return -1;
}
