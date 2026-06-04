// static/js/usuarios.js
function cambiarRolUsuario(idUsuario, nuevoRol) {
    if (confirm('¿Estás seguro de que quieres cambiar el rol de este usuario?')) {
        const form = document.querySelector(`form[action*="/admin/cambiar_rol/${idUsuario}"]`);
        if (form) {
            const select = form.querySelector('select[name="rol"]');
            if (select) {
                select.value = nuevoRol;
            }
            form.submit();
        }
    }
}

function eliminarUsuario(id) {
    if (confirm('¿Estás seguro de que quieres eliminar este usuario? Esta acción no se puede deshacer.')) {
        fetch('/usuarios/eliminar/' + id, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        }).then(response => {
            if (response.ok) {
                location.reload();
            } else {
                alert('Error al eliminar el usuario');
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar el usuario');
        });
    }
}

function validarFormularioUsuario() {
    const nombre = document.querySelector('input[name="nombre"]');
    const correo = document.querySelector('input[name="correo"]');
    const telefono = document.querySelector('input[name="telefono"]');
    const contrasena = document.querySelector('input[name="contrasena"]');
    
    if (nombre && nombre.value.trim() === '') {
        alert('El nombre es requerido');
        return false;
    }
    
    if (correo) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(correo.value)) {
            alert('Por favor ingresa un correo electrónico válido');
            return false;
        }
    }
    
    if (telefono && telefono.value.trim() !== '') {
        const phoneRegex = /^[0-9]{10}$/;
        if (!phoneRegex.test(telefono.value.replace(/\D/g, ''))) {
            alert('El teléfono debe tener 10 dígitos');
            return false;
        }
    }
    
    if (contrasena && contrasena.value !== '') {
        if (contrasena.value.length < 8) {
            alert('La contraseña debe tener al menos 8 caracteres');
            return false;
        }
    }
    
    return true;
}

function formatearTelefono(input) {
    input.value = input.value.replace(/\D/g, '').substring(0, 10);
}

function buscarUsuarios() {
    const searchTerm = document.querySelector('input[name="search"]').value;
    const form = document.querySelector('form[action*="/admin/usuarios"]');
    if (form) {
        form.submit();
    }
}

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const icon = document.querySelector(`[onclick="togglePasswordVisibility('${inputId}')"]`);
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '🙈';
    } else {
        input.type = 'password';
        icon.textContent = '👁️';
    }
}