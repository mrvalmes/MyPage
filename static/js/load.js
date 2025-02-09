function updateProgress(container, resultado, objetivo) {
	const $percent = container.querySelector(".percent");
	const $circle = container.querySelector(".progress");

	let load = 0;
	let logro = (resultado / objetivo) * 100;

	function update() {
		if (load < logro) {
			load++;
			$percent.innerHTML = `${load}%`;
			$circle.style.background = `conic-gradient(from 0deg at 50% 50%, 
                #6f7bf7 0%, #9bf8f4 ${load}%, #101012 ${load}% 
            )`;
			requestAnimationFrame(update, 50);
		}
	}
	requestAnimationFrame(update, 50);
}

// Llamar la función para varios módulos
document.querySelectorAll(".progress-container").forEach(container => {
	const target = container.getAttribute("data-target");

	if (target === "recarga") {
		updateProgress(container, 180050, 300000); // progreso para recargas
	} else if (target === "CR") {
		updateProgress(container, 80, 100); // progreso para el cr
	}
	else if (target === "codist") {
		updateProgress(container, 5000, 2755); // progreso para el cr
	}
});
