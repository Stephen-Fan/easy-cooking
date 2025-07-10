document.addEventListener('DOMContentLoaded', function () {
    const foldButtons = document.querySelectorAll('.fold-button');

    foldButtons.forEach(button => {
        button.addEventListener('click', function () {
            const subList = this.nextElementSibling;
            if (subList.style.display === 'block') {
                subList.style.display = 'none';
            } else {
                subList.style.display = 'block';
            }
        });
    });

    let gpdf = document.getElementById("gpdf")
    gpdf.addEventListener("click", function(){
    window.print()
    })
});


// Home Page
function directToHome() {
    window.location.href = '/';
}
document.getElementById("home_icon").addEventListener("click", directToHome);
