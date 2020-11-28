import * as tf from '@tensorflow/tfjs';

let mouse_down = false;

function toggle_grid(target) {
    if (target.className === 'wall') {
        target.className = 'unvisited';
    } else {
        target.className = 'wall';
    }
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

const MODEL_URL = '../../../../trainer/model.json';
const model = await tf.loadLayersModel(MODEL_URL);
			
const prediction = model.predict(maze);

$("#run_algo").click(function() {
	console.log(prediction);
});
