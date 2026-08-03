const pulsantePosizione = document.getElementById("usa-posizione");

pulsantePosizione.addEventListener("click", () => {
    if (!navigator.geolocation) {
        alert("La geolocalizzazione non è supportata dal browser.");
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (posizione) => {
            console.log(posizione);
        },
        () => {
            alert("Impossibile ottenere la posizione.");
        }
    );
});