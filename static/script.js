document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('send-button').addEventListener('click', async function() {
        let userInput = document.getElementById('user-input').value;
        if (userInput.trim() !== '') {
            addUserMessage(userInput);
            document.getElementById('user-input').value = '';

            // Add a loading message
            let loadingMessageDiv = addLoadingMessage();

            try {
                const response = await fetch('/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_input: userInput }),
                });
                const output = await response.json();
                simulateBotResponse(output, loadingMessageDiv);
            } catch (error) {
                console.error(error);
                // Remove loading message if there's an error
                loadingMessageDiv.remove();
            }
        }
    });

    document.getElementById('user-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            document.getElementById('send-button').click();
        }
    });
});

function addUserMessage(message) {
    let chatContainer = document.getElementById('chat-container');
    let userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user-message';
    userMessageDiv.innerHTML = `<p>${message}</p>`;
    chatContainer.appendChild(userMessageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

const loadscreen = `<style>
  .loading-dots {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 50px;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #333;
    margin: 0 5px;
    animation: pulse 1s infinite;
  }

  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.5);
    }
    100% {
      transform: scale(1);
    }
  }

  .loading-dots span:nth-child(1) {
    animation-delay: 0s;
  }

  .loading-dots span:nth-child(2) {
    animation-delay: 0.2s;
  }

  .loading-dots span:nth-child(3) {
    animation-delay: 0.4s;
  }
</style>

<div class="loading-dots">
  <span class="dot"></span>
  <span class="dot"></span>
  <span class="dot"></span>
</div>`

function addLoadingMessage() {
    let chatContainer = document.getElementById('chat-container');
    let loadingMessageDiv = document.createElement('div');
    loadingMessageDiv.className = 'message bot-message loading';
    loadingMessageDiv.innerHTML = loadscreen;
    chatContainer.appendChild(loadingMessageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return loadingMessageDiv;
}

function simulateBotResponse(response, loadingMessageDiv) {
    const outputValue = response.output;
    console.log(outputValue);
    
    setTimeout(() => {
        // Replace loading message with actual response
        loadingMessageDiv.innerHTML = `<p>${outputValue}</p>`;
        let chatContainer = document.getElementById('chat-container');
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }, 1000);
}