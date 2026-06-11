document.addEventListener("DOMContentLoaded", () => {

    const toggle = document.getElementById("darkModeToggle");

    // LOAD SAVED MODE
    if(localStorage.getItem("darkMode") === "enabled"){

        document.body.classList.add("dark-mode");

        if(toggle){
            toggle.checked = true;
        }
    }

    // TOGGLE MODE
    if(toggle){

        toggle.addEventListener("change", () => {

            if(toggle.checked){

                document.body.classList.add("dark-mode");

                localStorage.setItem(
                    "darkMode",
                    "enabled"
                );

            }else{

                document.body.classList.remove("dark-mode");

                localStorage.setItem(
                    "darkMode",
                    "disabled"
                );
            }
        });
    }

});