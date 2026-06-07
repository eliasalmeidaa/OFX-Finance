document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('hamburger-btn');
    if (btn) {
        btn.addEventListener('click', function () {
            document.querySelector('header nav').classList.toggle('nav-open');
        });
    }
});
