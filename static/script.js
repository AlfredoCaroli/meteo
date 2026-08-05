const pulsantePosizione = document.getElementById("usa-posizione");

pulsantePosizione.addEventListener("click", () => {
    if (!navigator.geolocation) {
        alert("La geolocalizzazione non è supportata dal browser.");
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (posizione) => {

            const form = document.createElement("form");
            form.method = "POST";
            form.action = "/";

            const lat = document.createElement("input");
            lat.type = "hidden";
            lat.name = "latitudine";
            lat.value = posizione.coords.latitude;

            const lon = document.createElement("input");
            lon.type = "hidden";
            lon.name = "longitudine";
            lon.value = posizione.coords.longitude;

            form.appendChild(lat);
            form.appendChild(lon);

            document.body.appendChild(form);
            form.submit();
        },
        (error) => {
            alert(`Codice errore: ${error.code}\n${error.message}`);
        }
    );
});