function eliminarServicio(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este servicio?')) {
        fetch('/servicios/eliminar/' + id, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al eliminar el servicio');
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar el servicio');
        });
    }
}

function previewServicioImage(input) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const preview = document.getElementById('image-preview');
            if (preview) {
                preview.src = e.target.result;
                preview.style.display = 'block';
            }
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function validarFormularioServicio() {
    const nombre = document.querySelector('input[name="nombre"]');
    const precio = document.querySelector('input[name="precio"]');
    
    if (nombre && nombre.value.trim() === '') {
        alert('El nombre del servicio es requerido');
        return false;
    }
    
    if (precio && (precio.value === '' || parseFloat(precio.value) <= 0)) {
        alert('El precio debe ser mayor a 0');
        return false;
    }
    
    return true;
}