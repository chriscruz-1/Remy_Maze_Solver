let mouse_down = false;

function toggle_grid(target) {
    if (target.className === 'wall') {
        target.className = 'unvisited';
    } else {
        target.className = 'wall';
    }
}

function load_map(x) {
    window.location = "fetch_map?i=" + x;
}

window.addEventListener("DOMContentLoaded", function() {
    let params = (new URL(document.location)).searchParams;
    let map_idx = params.get('i');

    if (map_idx != null) {
        return;
    }

    document.querySelectorAll('td').forEach(button => {
        button.onmousedown = (e_down) => {
            mouse_down = true;
            toggle_grid(e_down.target);
        };

        button.onmouseup = (e_up) => {
            mouse_down = false;
        };

        button.onmouseenter = (e_move) => {
            if (mouse_down) {
                toggle_grid(e_move.target);
            }
        }
    });
});

function indexOfMax(arr) {
    if (arr.length === 0) {
        return -1;
    }

    var max = arr[0];
    var maxIndex = 0;

    for (var i = 1; i < arr.length; i++) {
        if (arr[i] > max) {
            maxIndex = i;
            max = arr[i];
        }
    }

    return maxIndex;
}

function update_view(curr_row, curr_col, new_row, new_col) {
    document.getElementById(curr_row + "-" + curr_col).innerHTML = "";
    document.getElementById(curr_row + "-" + curr_col).className = "visited";
    document.getElementById(new_row + "-" + new_col).innerHTML = '<img src="/static/remyBig.png">';
}

function get_new_state(curr_state, curr_row, curr_col, new_row, new_col) {
    let new_state = curr_state.slice();
    new_state[0][curr_row * shape[1] + curr_col] = 0.0;
    new_state[0][new_row * shape[1] + new_col] = 0.3;
    return new_state.slice();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// set speed with sliding bar
function setSpeed() {
    var slider = document.getElementById("speedBar");
    var delay = (100-slider.value)/100 * 500;
    return delay;
}

async function play_game() {
    if (document.getElementById("run_algo").textContent != "Run algo") {
        console.log("Already running or finished.");
        return;
    }

    document.getElementById("run_algo").textContent = "Running";

    let params = (new URL(document.location)).searchParams;
    let map_idx = params.get('i');

    if (map_idx == null) {
        return;
    }

    const model = await tf.loadLayersModel('/static/models/model_m' + map_idx + '/model.json');

    let curr_row = 0;
    let curr_col = 0;
    let game_over = false;
    let curr_state = state.slice();

    while (!game_over) {
        await sleep(setSpeed());
        const result = model.predict(tf.tensor(curr_state, [1, shape[0] * shape[1]], 'float32')).dataSync();
        
        // console.log(JSON.stringify(curr_state))
        // console.log("(" + curr_row + ", " + curr_col + ")  Prob = " + result);

        // if (curr_row == 9 && curr_col == 5) {
        //     break;
        // }

        const argmax = indexOfMax(result);
        let new_row = curr_row;
        let new_col = curr_col

        if (argmax == 0) {
            // GO LEFT
            new_col -= 1;
        } else if (argmax == 1) {
            // GO UP
            new_row -= 1;
        } else if (argmax == 2) {
            // GO RIGHT
            new_col += 1;
        } else if (argmax == 3) {
            // GO DOWN
            new_row += 1;
        } else {
            console.log("?")
        }

        if (curr_state[0][new_row * shape[1] + new_col] == 0.9) {
            game_over = true;
            console.log("Out");
        }
        
        update_view(curr_row, curr_col, new_row, new_col);
        curr_state = get_new_state(curr_state, curr_row, curr_col, new_row, new_col).slice();
        curr_row = new_row;
        curr_col = new_col;
    }

    document.getElementById("run_algo").textContent = "Finished";
}
