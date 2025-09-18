document.addEventListener('DOMContentLoaded', () => {
    let isLoggedIn = false;

    // --- SELETORES GLOBAIS ---
    const mainContentArea = document.querySelector('#main-content-area');
    const fileInfoHeader = document.querySelector('#file-info-header');
    const rightSidebar = document.querySelector('.right-sidebar');
    const statsTriggers = document.querySelectorAll('#visitor-log-trigger, #download-log-trigger, #upload-log-trigger');
    const loginIcon = document.querySelector('#login-icon');
    const uploadLink = document.querySelector('#upload-link');
    const categoryToggles = document.querySelectorAll('.category-toggle');
    const downloadButton = document.querySelector('#download-button');
    const visitorCountSpan = document.querySelector('#visitor-count');
    const downloadCountSpan = document.querySelector('#download-count');
    const uploadCountSpan = document.querySelector('#upload-count');

    // --- FUNÇÕES DE ATUALIZAÇÃO DA UI ---
    function updateUIForLoginState() {
        document.querySelectorAll('.file-category').forEach(cat => {
            const categoryType = cat.dataset.category;
            if (categoryType !== 'arq') {
                cat.style.display = isLoggedIn ? 'block' : 'none';
            }
        });
        statsTriggers.forEach(trigger => {
            trigger.style.cursor = isLoggedIn ? 'pointer' : 'default';
        });
        loginIcon.classList.toggle('loggedin', isLoggedIn);
        document.querySelectorAll('.file-list').forEach(list => {
            list.innerHTML = '';
            list.style.display = 'none';
            list.previousElementSibling.classList.remove('active');
        });
        mainContentArea.innerHTML = '<h1>Bem-vindo ao Passado</h1><p>Selecione um arquivo para visualizar.</p>';
        fileInfoHeader.innerHTML = '';
        downloadButton.style.display = 'none';
    }

    // --- FUNÇÕES DE DADOS E LÓGICA ---
    function getIconForFile(fileName) {
        const extension = fileName.split('.').pop().toLowerCase();
        let svgIcon = '';
        switch (extension) {
            case 'pdf': svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="file-icon"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm-1 9c0 1.1-.9 2-2 2s-2-.9-2-2V9.5c0-.83.67-1.5 1.5-1.5s1.5.67 1.5 1.5V11zm-3 4h2v2h-2v-2zm4-4h2v2h-2v-2zm-2-4.5c.83 0 1.5.67 1.5 1.5V11h-2V9.5c0-.83.67-1.5 1.5-1.5z"/></svg>'; break;
            case 'txt': svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="file-icon"><path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11zM8 15.01l2 2 2-2V14h-4v1.01zM16 11H8V9h8v2z"/></svg>'; break;
            case 'jpg': case 'jpeg': case 'png': case 'webp': case 'gif': svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="file-icon"><path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/></svg>'; break;
            case 'mp4': case 'mov': case 'avi': case 'mkv': svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="file-icon"><path d="M18 4l2 4h-3l-2-4h-2l2 4h-3l-2-4H8l2 4H7L5 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4h-4z"/></svg>'; break;
            case 'mp3': case 'wav': case 'ogg': case 'flac': svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="file-icon"><path d="M12 3v10.55c-.59-.34-1.27-.55-2-.55-2.21 0-4 1.79-4 4s1.79 4 4 4 4-1.79 4-4V7h4V3h-6z"/></svg>'; break;
            case 'exe': case 'msi': case 'bat': case 'app': svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="file-icon"><path d="M19.43 12.98c.04-.32.07-.64.07-.98s-.03-.66-.07-.98l2.11-1.65c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.3-.61-.22l-2.49 1c-.52-.4-1.08-.73-1.69-.98l-.38-2.65C14.46 2.18 14.25 2 14 2h-4c-.25 0-.46.18-.49.42l-.38 2.65c-.61.25-1.17.59-1.69.98l-2.49-1c-.23-.09-.49 0-.61.22l-2 2.46c-.13.22-.07.49.12.64l2.11 1.65c-.04.32-.07.65-.07.98s.03.66.07.98l-2.11 1.65c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1c.52.4 1.08.73 1.69.98l.38 2.65c.03.24.24.42.49.42h4c.25 0 .46-.18.49-.42l.38-2.65c.61-.25 1.17-.59 1.69-.98l2.49 1c.23.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.65zM12 15.5c-1.93 0-3.5-1.57-3.5-3.5s1.57-3.5 3.5-3.5 3.5 1.57 3.5 3.5-1.57 3.5-3.5 3.5z"/></svg>'; break;
            default: svgIcon = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="file-icon"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-12h2v2h-2v-2zm0 4h2v6h-2v-6z"/></svg>'; break;
        }
        return svgIcon;
    }

    async function updateAllCounts() {
        try {
            const response = await fetch('/api/counts');
            const counts = await response.json();
            visitorCountSpan.textContent = counts.visitors;
            downloadCountSpan.textContent = counts.downloads;
            uploadCountSpan.textContent = counts.uploads;
        } catch (error) { console.error('Erro ao buscar contagens:', error); }
    }

    async function displayLog(logType) {
        mainContentArea.innerHTML = `<h1>Carregando Log de ${logType}...</h1>`;
        fileInfoHeader.innerHTML = '';
        downloadButton.style.display = 'none';
        try {
            const response = await fetch(`/api/logs/${logType}`);
            if (!response.ok) {
                mainContentArea.innerHTML = `<h1>Acesso Negado</h1><p>Você precisa estar logado para ver os logs.</p>`;
                return;
            }
            const logData = await response.json();
            if (logData.length === 0) {
                mainContentArea.innerHTML = `<h1>Nenhum registro encontrado para ${logType}.</h1>`;
                return;
            }
            const hasFileColumn = logType === 'downloads' || logType === 'uploads';
            let tableHTML = `
                <div style="height: 100%; overflow-y: auto;">
                    <table style="width: 100%; text-align: left; border-collapse: collapse;">
                        <thead>
                            <tr>
                                <th style="padding: 8px; border-bottom: 1px solid #ffcc00;">Data/Hora</th>
                                <th style="padding: 8px; border-bottom: 1px solid #ffcc00;">IP</th>
                                ${hasFileColumn ? '<th style="padding: 8px; border-bottom: 1px solid #ffcc00;">Arquivo</th>' : ''}
                                <th style="padding: 8px; border-bottom: 1px solid #ffcc00;">Dispositivo/Navegador</th>
                            </tr>
                        </thead>
                        <tbody>`;
            logData.forEach(log => {
                const fileColumn = hasFileColumn ? `<td style="padding: 8px;">${log.file || 'N/A'}</td>` : '';
                tableHTML += `
                    <tr>
                        <td style="padding: 8px;">${log.datetime}</td>
                        <td style="padding: 8px;">${log.ip}</td>
                        ${fileColumn}
                        <td style="padding: 8px; font-size: 0.8rem;">${log.device}</td>
                    </tr>`;
            });
            tableHTML += '</tbody></table></div>';
            mainContentArea.innerHTML = tableHTML;
        } catch (error) {
            console.error(`Erro ao buscar log de ${logType}:`, error);
            mainContentArea.innerHTML = '<h1>Erro ao carregar o log.</h1>';
        }
    }

    async function handleUpload(event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const statusP = document.querySelector('#upload-status');
        statusP.textContent = 'Enviando...';
        try {
            const response = await fetch('/api/upload', { method: 'POST', body: formData });
            const result = await response.json();
            statusP.textContent = result.message;
            if (result.success) {
                await updateAllCounts();
                document.querySelectorAll('.file-list').forEach(list => {
                    list.innerHTML = '';
                    const toggle = list.previousElementSibling;
                    if(toggle.classList.contains('active')){
                        toggle.click();
                        toggle.click();
                    }
                });
            }
        } catch (error) {
            statusP.textContent = 'Erro de conexão.';
            console.error('Erro no upload:', error);
        }
    }

    // --- INICIALIZAÇÃO E EVENT LISTENERS ---
    async function initializeApp() {
        try {
            const response = await fetch('/api/check_session');
            const session = await response.json();
            isLoggedIn = session.loggedin;
            updateUIForLoginState();
            await updateAllCounts();
            await fetch('/api/tracker', { method: 'POST' });
        } catch (error) { console.error("Erro ao verificar sessão:", error); }
    }

    document.addEventListener('authChange', initializeApp);
    
    uploadLink.addEventListener('click', (event) => {
        event.preventDefault();
        mainContentArea.innerHTML = `
            <form id="file-upload-form" class="upload-form">
                <h2>Upload de Arquivo</h2>
                <input type="file" name="fileToUpload" required>
                <button type="submit">Enviar</button>
                <p id="upload-status"></p>
            </form>`;
        fileInfoHeader.innerHTML = '';
        downloadButton.style.display = 'none';
        document.querySelector('#file-upload-form').addEventListener('submit', handleUpload);
    });

    statsTriggers.forEach(trigger => {
        trigger.addEventListener('click', () => {
            if (isLoggedIn) {
                // ✅ CORREÇÃO: Adiciona 's' para corresponder à API (ex: 'visitor' -> 'visitors')
                const logType = trigger.id.replace('-log-trigger', '') + 's';
                displayLog(logType);
            }
        });
    });

    categoryToggles.forEach(toggle => {
        toggle.addEventListener('click', async () => {
            const fileList = toggle.nextElementSibling;
            const folder = toggle.dataset.folder;
            if (fileList.innerHTML === '' && folder) {
                try {
                    const response = await fetch(`/api/files/${folder}`);
                    if (!response.ok) {
                        fileList.innerHTML = '<li>Acesso negado.</li>';
                        return;
                    }
                    const filesData = await response.json();
                    if (filesData.length === 0) {
                        fileList.innerHTML = '<li>Nenhum arquivo encontrado.</li>';
                    } else {
                        filesData.forEach(fileData => {
                            const icon = getIconForFile(fileData.name);
                            const downloadIconSVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" class="download-icon"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>';
                            const listItem = document.createElement('li');
                            listItem.dataset.folder = folder;
                            listItem.dataset.filename = fileData.name;
                            listItem.dataset.modified = fileData.modified;
                            listItem.innerHTML = `<a href="#">${icon}<span class="file-name">${fileData.name}</span></a> ${downloadIconSVG}`;
                            fileList.appendChild(listItem);
                        });
                    }
                } catch (error) { console.error('Erro ao buscar arquivos:', error); }
            }
            toggle.classList.toggle('active');
            fileList.style.display = fileList.style.display === 'block' ? 'none' : 'block';
        });
    });

    rightSidebar.addEventListener('click', async (event) => {
        const link = event.target.closest('a');
        const downloadIcon = event.target.closest('.download-icon');
        const listItem = event.target.closest('li');

        if (!listItem) return;

        const folder = listItem.dataset.folder;
        const fileName = listItem.dataset.filename;
        const downloadUrl = `/api/download/${folder}/${fileName}`;
        const viewFilePath = `uploads/${folder}/${fileName}`;

        if (downloadIcon) {
            window.location.href = downloadUrl;
            return;
        }

        if (link) {
            event.preventDefault();
            mainContentArea.innerHTML = '<h1>Carregando...</h1>';
            fileInfoHeader.innerHTML = 'Buscando informações de origem...';
            downloadButton.style.display = 'none';

            try {
                const infoResponse = await fetch(`/api/file_info/${fileName}`);
                const fileInfo = await infoResponse.json();
                const modifiedTimestamp = parseInt(listItem.dataset.modified) * 1000;
                const modifiedDate = new Date(modifiedTimestamp).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });

                if (fileInfo.found) {
                    fileInfoHeader.innerHTML = `<strong>Origem:</strong> IP ${fileInfo.ip} | <strong>Upload:</strong> ${fileInfo.datetime} | <strong>Arquivo Modificado:</strong> ${modifiedDate}`;
                } else {
                    fileInfoHeader.innerHTML = `<strong>Origem:</strong> Local | <strong>Arquivo Modificado:</strong> ${modifiedDate}`;
                }
            } catch (e) {
                fileInfoHeader.innerHTML = `Informações de origem indisponíveis.`;
            }

            try {
                const extension = fileName.split('.').pop().toLowerCase();
                let contentSet = false;
                if (['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(extension)) {
                    mainContentArea.innerHTML = `<img src="${viewFilePath}" alt="${fileName}">`;
                    contentSet = true;
                } else if (extension === 'txt') {
                    const response = await fetch(viewFilePath);
                    const textContent = await response.text();
                    mainContentArea.innerHTML = `<pre>${textContent}</pre>`;
                    contentSet = true;
                } else if (extension === 'pdf') {
                    mainContentArea.innerHTML = `<iframe src="${viewFilePath}" width="100%" height="100%"></iframe>`;
                    contentSet = true;
                }
                
                if (contentSet) {
                    downloadButton.href = downloadUrl;
                    downloadButton.style.display = 'flex';
                } else {
                    mainContentArea.innerHTML = `<h1>Visualização não suportada</h1><p>Clique <a href="${downloadUrl}">aqui</a> para baixar o arquivo.</p>`;
                    downloadButton.style.display = 'none';
                }
            } catch (error) { 
                console.error('Erro ao carregar conteúdo:', error);
                mainContentArea.innerHTML = '<h1>Erro ao carregar o conteúdo do arquivo.</h1>';
            }
        }
    });

    initializeApp();
});