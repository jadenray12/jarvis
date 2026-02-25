document.addEventListener('DOMContentLoaded', () => {
    const contentDiv = document.getElementById('content');
    contentDiv.innerHTML = `
        <h1>Welcome to Our Beautiful Homepage</h1>
        <p>This is a simple and elegant homepage created using JavaScript.</p>
        <button id="greetButton">Say Hello</button>
    `;

    const greetButton = document.getElementById('greetButton');
    greetButton.addEventListener('click', () => {
        alert('Hello, visitor!');
    });
});
