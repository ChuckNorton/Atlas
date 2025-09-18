document.addEventListener('DOMContentLoaded', () => {
    const loginIcon = document.querySelector('#login-icon');
    const mainContentArea = document.querySelector('#main-content-area');
    const fileInfoHeader = document.querySelector('#file-info-header');
    const downloadButton = document.querySelector('#download-button');

    // Função para lidar com o Logout
    async function handleLogout() {
        if (confirm('Deseja fazer logout?')) {
            try {
                // ✅ ALTERADO: Faz uma requisição POST para a API de logout
                const response = await fetch('/api/logout', { method: 'POST' });
                const result = await response.json();

                if (result.success) {
                    // Dispara o evento para a UI ser atualizada em script.js
                    document.dispatchEvent(new CustomEvent('authChange'));
                } else {
                    alert('Erro ao fazer logout.');
                }
            } catch (error) {
                console.error('Logout error:', error);
                alert('Erro de conexão ao tentar fazer logout.');
            }
        }
    }

    // Função para lidar com o envio do formulário de Login
    async function handleLoginSubmit(event) {
        event.preventDefault();
        const password = document.querySelector('#password-input').value;
        const statusP = document.querySelector('#login-status');
        statusP.textContent = 'Verificando...';

        const formData = new FormData();
        formData.append('password', password);

        try {
            // ✅ ALTERADO: A URL da requisição agora aponta para a API
            const response = await fetch('/api/login', { method: 'POST', body: formData });
            
            // O Flask retorna um status 401 (Unauthorized) para senhas erradas
            if (!response.ok) {
                statusP.textContent = 'Senha incorreta.';
                return;
            }

            const result = await response.json();

            if (result.success) {
                statusP.textContent = 'Login bem-sucedido!';
                mainContentArea.innerHTML = '<h1>Acesso Liberado</h1><p>Atualizando interface...</p>';
                // Dispara o evento para a UI ser atualizada em script.js
                document.dispatchEvent(new CustomEvent('authChange'));
            } else {
                 // Este bloco pode ser redundante devido à checagem do response.ok, mas é mantido por segurança.
                statusP.textContent = 'Senha incorreta.';
            }
        } catch (error) {
            statusP.textContent = 'Erro de conexão.';
            console.error('Login error:', error);
        }
    }

    // Event listener principal para o ícone de login/logout
    loginIcon.addEventListener('click', () => {
        if (loginIcon.classList.contains('loggedin')) {
            handleLogout(); // Chama a nova função de logout
            return;
        }

        // Limpa a tela e exibe o formulário de login
        fileInfoHeader.innerHTML = '';
        downloadButton.style.display = 'none';
        mainContentArea.innerHTML = `
            <form id="login-form" class="login-form">
                <input type="password" id="password-input" placeholder="??????" required autofocus>
                <button type="submit">Submit</button>
                <p id="login-status"></p>
            </form>`;

        document.querySelector('#login-form').addEventListener('submit', handleLoginSubmit);
    });
});