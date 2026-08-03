const pulsantePosizione = document.getElementById("usa-posizione");

pulsantePosizione.addEventListener("click", () => {
    if (!navigator.geolocation) {
        alert("La geolocalizzazione non è supportata dal browser.");
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (posizione) => {
            console.log(posizione);
            // to delete
            const coordinate = posizione.coords
            alert(`Latitudine: ${coordinate.latitude}\nLongitudine: ${coordinate.longitude}`);
        },
        () => {
            alert("Impossibile ottenere la posizione.");
        }
    );
});