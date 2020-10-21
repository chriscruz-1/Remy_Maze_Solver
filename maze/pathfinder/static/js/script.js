window.addEventListener("DOMContentLoaded", function() {
    console.log("loaded");
    document.querySelectorAll('td').forEach(button => {
        // console.log('hello');
        button.onclick = () => {
            console.log('Clicked');
        };
    });
});