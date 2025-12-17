// static/script.js
document.getElementById('chat-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(document.getElementById('chat-form'));
    const message = formData.get('message');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();
        document.getElementById('output').textContent = data.choices[0]?.message?.content || 'Ошибка';
    } catch (error) {
        console.error('[ERROR]', error);
        alert('Ошибка при обработке запроса.');
    }
});