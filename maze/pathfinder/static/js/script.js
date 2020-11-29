// import * as tf from '@tensorflow/tfjs';

let mouse_down = false;

function toggle_grid(target) {
    if (target.className === 'wall') {
        target.className = 'unvisited';
    } else {
        target.className = 'wall';
    }
}

function initalize() {
    load_map()
    load_model()
}

function load_map(x) {
    window.location = "fetch_map?i=" + x
}

function load_model() {
    fetch('fetch_model?i=1', {
        headers:{
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => {
        return response.json()
    })
    .then(data => {
        console.log(data)
        //Perform actions with the response data from the view
    })
}

window.addEventListener("DOMContentLoaded", function() {
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



console.log(state)

// const MODEL_URL = '../../../../trainer/model.json';
// const model = await tf.loadLayersModel(MODEL_URL);
			
// const prediction = model.predict(maze);

// $("#run_algo").click(function() {
// 	console.log(prediction);
// });
