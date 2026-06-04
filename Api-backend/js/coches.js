function eliminarCoche(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este coche?')) {
        fetch('/coches/eliminar/' + id, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al eliminar el coche');
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar el coche');
        });
    }
}

function previewCocheImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('coche-image-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            } else {
                const container = input.parentNode;
                const img = document.createElement('img');
                img.id = 'coche-image-preview';
                img.src = e.target.result;
                img.style.maxWidth = '200px';
                img.style.marginTop = '10px';
                img.style.borderRadius = '8px';
                container.appendChild(img);
            }
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function validarFormularioCoche() {
    const marca = document.querySelector('input[name="marca"]');
    const modelo = document.querySelector('input[name="modelo"]');
    const anio = document.querySelector('input[name="anio"]');
    const placa = document.querySelector('input[name="placa"]');
    
    if (marca && marca.value.trim() === '') {
        alert('La marca es requerida');
        return false;
    }
    
    if (modelo && modelo.value.trim() === '') {
        alert('El modelo es requerido');
        return false;
    }
    
    if (anio) {
        const year = parseInt(anio.value);
        const currentYear = new Date().getFullYear();
        if (isNaN(year) || year < 1900 || year > currentYear + 1) {
            alert('El año debe ser válido (1900 - ' + (currentYear + 1) + ')');
            return false;
        }
    }
    
    if (placa && placa.value.trim() === '') {
        alert('La placa es requerida');
        return false;
    }
    
    return true;
}

function formatearPlaca(input) {
    input.value = input.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
}