const pulsantePosizione = document.getElementById("usa-posizione");

pulsantePosizione.addEventListener("click", () => {
    if (!navigator.geolocation) {
        alert("La geolocalizzazione non è supportata dal browser.");
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (posizione) => {
            const latitudine = posizione.coords.latitude;
            const longitudine = posizione.coords.longitude;

            window.location.href = `/?latitudine=${latitudine}&longitudine=${longitudine}`;
        },
        () => {
            alert("Impossibile ottenere la posizione.");
        },
        {enableHighAccuracy: true}
    );
});