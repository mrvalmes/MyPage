const audioList = [
    {
        name: "Los Reyes",
        url: "https://losreyes.hvalmes.com/losreyes"
    },
    {
        name: "Villa Gonzalez",
        url: "https://villagonsalez.hvalmes.com/VillaG"
    },
    {
        name: "Ranchito",
        url: "https://ranchitopos.hvalmes.com/ranchito"
    },
    {
        name: "Montecristy",
        url: "https://montecristy.hvalmes.com/mc-franny"
    },
    {
        name: "La Mata Cotui",
        url: "https://lamatacotui.hvalmes.com/LaMata"
    },
    {
        name: "Loma de Cabrera",
        url: "https://lomac.hvalmes.com/loma"
    },
    {
        name: "Villa Vasquez",
        url: "https://villavasquez.hvalmes.com/esperanza"
    },
    {
        name: "Navarrete",
        url: "https://navarrete.hvalmes.com/Navarrete"
    },
    {
        name: "El Janet",
        url: "https://eljanet.hvalmes.com/eljanet"
    },
    {
        name: "Maimon",
        url: "https://maimon.hvalmes.com/maimon"
    },  
    {
        name: "Jim Abajo",
        url: "https://jimabajo.hvalmes.com/Jima01"
    },  
    {
        name: "Fantino",
        url: "https://fantino.hvalmes.com/fantino"
    },  
    {
        name: "Cevicos",
        url: "https://cevicos.hvalmes.com/Cevicos"
    },  
    {
        name: "Cabarete",
        url: "https://cabarete.hvalmes.com/cabarete"
    },  
    {
        name: "Castañuela",
        url: "https://castanuela.hvalmes.com/castanuela"
    },  
    {
        name: "Cotui",
        url: "https://cotui.hvalmes.com/Cotui-01"
    },  
    {
        name: "Las Matas",
        url: "https://lasmatasc.hvalmes.com/lasmatas"
    },  
    {
        name: "Cabrera",
        url: "https://cabrera.hvalmes.com/Cabrera"
    },  
    {
        name: "Rio San Juan",
        url: "https://rsj.hvalmes.com/RioSanJuan"
    },  
    {
        name: "Sabaneta",
        url: "https://sabaneta.hvalmes.com/Sabaneta"
    },  
];

let currentAudio = null;
let currentBtn = null;

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('audio-container');
    if (!container) return;

    audioList.forEach((audio, index) => {
        const card = document.createElement('div');
        card.className = 'audio-card';
        
        card.innerHTML = `
            <div class="audio-info">
                <div class="icon-wrapper">
                    <i class='bx bxs-music'></i>
                </div>
                <h3>${audio.name}</h3>
                <div class="visualizer">
                    <span></span><span></span><span></span><span></span><span></span>
                </div>
            </div>
            <div class="audio-controls">
                <button class="btn-play" data-url="${audio.url}" data-id="${index}">
                    <i class='bx bx-play'></i>
                </button>
                <button class="btn-stop" disabled>
                    <i class='bx bx-stop'></i>
                </button>
            </div>
        `;
        
        container.appendChild(card);
    });
    
    // Event Delegation
    container.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;
        
        if (btn.classList.contains('btn-play')) {
            const url = btn.dataset.url;
            if (btn.classList.contains('playing')) {
                pauseAudio();
            } else {
                playAudio(url, btn);
            }
        } else if (btn.classList.contains('btn-stop')) {
            stopAudio();
        }
    });
});

function playAudio(url, btn) {
    // Si hay otro audio sonando, detenerlo
    if (currentAudio && currentBtn !== btn) {
        stopAudio();
    }
    
    // Si es el mismo audio y está pausado, reanudar
    if (currentAudio && currentAudio.paused && currentBtn === btn) {
        currentAudio.play();
        btn.innerHTML = "<i class='bx bx-pause'></i>";
        btn.classList.add('playing');
        const visualizer = btn.closest('.audio-card').querySelector('.visualizer');
        visualizer.classList.add('active');
        return;
    }

    // Nuevo audio
    currentAudio = new Audio(url);
    currentAudio.play().catch(e => {
        console.error("Error playing audio:", e);
        alert("Error al reproducir el audio. Verifique la conexión.");
        stopAudio();
    });
    
    currentBtn = btn;
    
    // Update UI
    btn.innerHTML = "<i class='bx bx-pause'></i>";
    btn.classList.add('playing');
    const stopBtn = btn.nextElementSibling;
    stopBtn.disabled = false;
    
    // Visualizer effect
    const visualizer = btn.closest('.audio-card').querySelector('.visualizer');
    visualizer.classList.add('active');
    
    currentAudio.onended = () => {
        stopAudio();
    };
}

function pauseAudio() {
    if (currentAudio) {
        currentAudio.pause();
        if (currentBtn) {
            currentBtn.innerHTML = "<i class='bx bx-play'></i>";
            currentBtn.classList.remove('playing');
            const visualizer = currentBtn.closest('.audio-card').querySelector('.visualizer');
            visualizer.classList.remove('active');
        }
    }
}

function stopAudio() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }
    resetControls();
}

function resetControls() {
    document.querySelectorAll('.btn-play').forEach(b => {
        b.innerHTML = "<i class='bx bx-play'></i>";
        b.classList.remove('playing');
    });
    document.querySelectorAll('.btn-stop').forEach(b => b.disabled = true);
    document.querySelectorAll('.visualizer').forEach(v => v.classList.remove('active'));
    currentBtn = null;
}
