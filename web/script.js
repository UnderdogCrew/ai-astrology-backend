// API Base URL
const API_BASE_URL = 'http://localhost:8000';

// Global variables
let currentUser = null;
let authToken = localStorage.getItem('authToken');

// Check if user is already logged in
if (authToken) {
    loadUserProfile();
}

// Navigation functions
function showLogin() {
    document.getElementById('login-form').classList.remove('hidden');
    document.getElementById('register-form').classList.add('hidden');
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('chat-interface').classList.add('hidden');
    document.getElementById('user-header').classList.add('hidden');
    document.getElementById('nav-container').classList.remove('hidden');
    
    document.getElementById('nav-login').classList.add('active');
    document.getElementById('nav-register').classList.remove('active');
}

function showRegister() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.remove('hidden');
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('chat-interface').classList.add('hidden');
    document.getElementById('user-header').classList.add('hidden');
    document.getElementById('nav-container').classList.remove('hidden');
    
    document.getElementById('nav-login').classList.remove('active');
    document.getElementById('nav-register').classList.add('active');
}

function showDashboard() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.add('hidden');
    document.getElementById('dashboard').classList.remove('hidden');
    document.getElementById('chat-interface').classList.add('hidden');
    document.getElementById('user-header').classList.remove('hidden');
    document.getElementById('nav-container').classList.add('hidden');
}

function showChat() {
    document.getElementById('login-form').classList.add('hidden');
    document.getElementById('register-form').classList.add('hidden');
    document.getElementById('dashboard').classList.add('hidden');
    document.getElementById('chat-interface').classList.remove('hidden');
    document.getElementById('user-header').classList.remove('hidden');
    document.getElementById('nav-container').classList.add('hidden');
    
    // Load chat history when showing chat
    loadChatHistory();
}

// Form event listeners
document.getElementById('loginForm').addEventListener('submit', handleLogin);
document.getElementById('registerForm').addEventListener('submit', handleRegister);
document.getElementById('updateForm').addEventListener('submit', handleUpdateProfile);

// Chat input event listener
document.getElementById('chat-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Login handler
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const messageDiv = document.getElementById('login-message');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            localStorage.setItem('authToken', authToken);
            messageDiv.innerHTML = '<p class="text-green-600">Login successful!</p>';
            await loadUserProfile();
        } else {
            messageDiv.innerHTML = `<p class="text-red-600">${data.detail}</p>`;
        }
    } catch (error) {
        messageDiv.innerHTML = '<p class="text-red-600">Network error. Please try again.</p>';
        console.error('Login error:', error);
    }
}

// Register handler
async function handleRegister(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('register-name').value,
        email: document.getElementById('register-email').value,
        phone_number: document.getElementById('register-phone').value,
        password: document.getElementById('register-password').value,
        birthdate: document.getElementById('register-birthdate').value,
        birthtime: document.getElementById('register-birthtime').value,
        birth_location: document.getElementById('register-birthlocation').value
    };
    
    const messageDiv = document.getElementById('register-message');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.innerHTML = '<p class="text-green-600">Registration successful! Please login.</p>';
            // Clear form
            document.getElementById('registerForm').reset();
            // Switch to login
            setTimeout(() => {
                showLogin();
            }, 2000);
        } else {
            messageDiv.innerHTML = `<p class="text-red-600">${data.detail}</p>`;
        }
    } catch (error) {
        messageDiv.innerHTML = '<p class="text-red-600">Network error. Please try again.</p>';
        console.error('Registration error:', error);
    }
}

// Load user profile
async function loadUserProfile() {
    if (!authToken) {
        showLogin();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            displayUserProfile();
            showDashboard();
        } else {
            // Token expired or invalid
            localStorage.removeItem('authToken');
            authToken = null;
            showLogin();
        }
    } catch (error) {
        console.error('Error loading profile:', error);
        showLogin();
    }
}

// Display user profile
function displayUserProfile() {
    if (!currentUser) return;
    
    // Update user header
    document.getElementById('user-name').textContent = currentUser.name;
    document.getElementById('user-email').textContent = currentUser.email;
    
    // Display profile information
    const profileInfo = document.getElementById('profile-info');
    profileInfo.innerHTML = `
        <div class="flex justify-between">
            <span class="font-medium text-gray-700">Name:</span>
            <span class="text-gray-900">${currentUser.name}</span>
        </div>
        <div class="flex justify-between">
            <span class="font-medium text-gray-700">Email:</span>
            <span class="text-gray-900">${currentUser.email}</span>
        </div>
        <div class="flex justify-between">
            <span class="font-medium text-gray-700">Phone:</span>
            <span class="text-gray-900">${currentUser.phone_number}</span>
        </div>
        <div class="flex justify-between">
            <span class="font-medium text-gray-700">Member Since:</span>
            <span class="text-gray-900">${new Date(currentUser.created_at).toLocaleDateString()}</span>
        </div>
    `;
    
    // Display birth chart information
    const birthChartInfo = document.getElementById('birth-chart-info');
    birthChartInfo.innerHTML = `
        <div class="flex justify-between">
            <span class="font-medium text-gray-700">Date of Birth:</span>
            <span class="text-gray-900">${new Date(currentUser.birthdate).toLocaleDateString()}</span>
        </div>
        <div class="flex justify-between">
            <span class="font-medium text-gray-700">Time of Birth:</span>
            <span class="text-gray-900">${currentUser.birthtime}</span>
        </div>
        <div class="flex justify-between">
            <span class="font-medium text-gray-700">Birth Location:</span>
            <span class="text-gray-900">${currentUser.birth_location}</span>
        </div>
    `;
    
    // Populate edit form
    populateEditForm();
}

// Populate edit form with current user data
function populateEditForm() {
    if (!currentUser) return;
    
    document.getElementById('edit-name').value = currentUser.name;
    document.getElementById('edit-email').value = currentUser.email;
    document.getElementById('edit-phone').value = currentUser.phone_number;
    document.getElementById('edit-birthdate').value = currentUser.birthdate;
    document.getElementById('edit-birthtime').value = currentUser.birthtime;
    document.getElementById('edit-birthlocation').value = currentUser.birth_location;
}

// Show edit form
function showEditForm() {
    document.getElementById('edit-profile-form').classList.remove('hidden');
}

// Hide edit form
function hideEditForm() {
    document.getElementById('edit-profile-form').classList.add('hidden');
    document.getElementById('update-message').innerHTML = '';
}

// Handle profile update
async function handleUpdateProfile(e) {
    e.preventDefault();
    
    const updateData = {};
    const fields = ['name', 'email', 'phone', 'birthdate', 'birthtime', 'birthlocation'];
    
    fields.forEach(field => {
        const value = document.getElementById(`edit-${field}`).value;
        if (value) {
            // Convert field names to match API
            const apiField = field === 'phone' ? 'phone_number' : 
                           field === 'birthlocation' ? 'birth_location' : field;
            updateData[apiField] = value;
        }
    });
    
    const messageDiv = document.getElementById('update-message');
    
    try {
        const response = await fetch(`${API_BASE_URL}/users`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(updateData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data;
            displayUserProfile();
            hideEditForm();
            messageDiv.innerHTML = '<p class="text-green-600">Profile updated successfully!</p>';
        } else {
            messageDiv.innerHTML = `<p class="text-red-600">${data.detail}</p>`;
        }
    } catch (error) {
        messageDiv.innerHTML = '<p class="text-red-600">Network error. Please try again.</p>';
        console.error('Update error:', error);
    }
}

// Chat functions
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, true);
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        // Use streaming endpoint
        await sendMessageStream(message);
    } catch (error) {
        console.error('Chat error:', error);
        hideTypingIndicator();
        addMessageToChat('Sorry, I encountered an error. Please try again.', false);
    }
}

async function sendMessageStream(message) {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/send-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ message: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Hide typing indicator
        hideTypingIndicator();
        
        // Create AI message container
        const aiMessageId = 'ai-message-' + Date.now();
        createAIMessageContainer(aiMessageId);
        
        // Use EventSource-like approach for better SSE handling
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        console.log('Starting to read stream...');
        
        while (true) {
            const { done, value } = await reader.read();
            
            if (done) {
                console.log('Stream complete');
                break;
            }
            
            // Decode the chunk
            const chunk = decoder.decode(value, { stream: true });
            console.log('Received chunk:', chunk);
            
            buffer += chunk;
            
            // Process complete lines immediately
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer
            
            for (const line of lines) {
                if (line.trim() === '') continue; // Skip empty lines
                
                if (line.startsWith('data: ')) {
                    try {
                        const jsonStr = line.slice(6); // Remove 'data: ' prefix
                        console.log('Parsing JSON:', jsonStr);
                        
                        const data = JSON.parse(jsonStr);
                        console.log('Parsed data:', data);
                        
                        if (data.error) {
                            console.error('Stream error:', data.error);
                            updateAIMessage(aiMessageId, `Error: ${data.error}`, true);
                            return;
                        }
                        
                        if (data.done) {
                            console.log('Stream done signal received');
                            // Remove the cursor when done
                            removeCursor(aiMessageId);
                            return;
                        }
                        
                        if (data.chunk) {
                            console.log('Appending chunk:', data.chunk);
                            // Use setTimeout with 0 delay to ensure immediate rendering
                            setTimeout(() => {
                                appendToAIMessage(aiMessageId, data.chunk);
                            }, 0);
                        }
                    } catch (e) {
                        console.error('Error parsing SSE data:', e, 'Line:', line);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error in sendMessageStream:', error);
        hideTypingIndicator();
        addMessageToChat('Sorry, I encountered an error while streaming the response.', false);
    }
}

function createAIMessageContainer(messageId) {
    const chatMessages = document.getElementById('chat-messages');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'mb-4 text-left';
    messageDiv.id = messageId;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble inline-block px-4 py-2 rounded-lg ai-message';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<span class="cursor-blink">|</span>';
    
    bubble.appendChild(contentDiv);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'text-xs text-gray-500 mt-1 text-left';
    timeDiv.textContent = new Date().toLocaleTimeString();
    
    messageDiv.appendChild(bubble);
    messageDiv.appendChild(timeDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendToAIMessage(messageId, chunk) {
    const messageDiv = document.getElementById(messageId);
    if (!messageDiv) return;
    
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) return;
    
    // Remove cursor if it exists
    const cursor = contentDiv.querySelector('.cursor-blink');
    if (cursor) {
        cursor.remove();
    }
    
    // Create a text node for the chunk to ensure proper text rendering
    const textNode = document.createTextNode(chunk);
    contentDiv.appendChild(textNode);
    
    // Add cursor back
    const newCursor = document.createElement('span');
    newCursor.className = 'cursor-blink';
    newCursor.textContent = '|';
    contentDiv.appendChild(newCursor);
    
    // Force immediate scroll to bottom
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Force a repaint to ensure the chunk is visible immediately
    requestAnimationFrame(() => {
        contentDiv.offsetHeight;
    });
}

function removeCursor(messageId) {
    const messageDiv = document.getElementById(messageId);
    if (!messageDiv) return;
    
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) return;
    
    const cursor = contentDiv.querySelector('.cursor-blink');
    if (cursor) {
        cursor.remove();
    }
}

function updateAIMessage(messageId, message, isError = false) {
    const messageDiv = document.getElementById(messageId);
    if (!messageDiv) return;
    
    const contentDiv = messageDiv.querySelector('.message-content');
    if (!contentDiv) return;
    
    // Remove cursor
    const cursor = contentDiv.querySelector('.cursor-blink');
    if (cursor) {
        cursor.remove();
    }
    
    // Update content
    if (isError) {
        contentDiv.innerHTML = `<span class="text-red-600">${message}</span>`;
    } else {
        contentDiv.innerHTML = formatMessage(message);
    }
    
    // Scroll to bottom
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'mb-4 text-left';
    typingDiv.id = 'typing-indicator';
    
    const indicator = document.createElement('div');
    indicator.className = 'typing-indicator';
    indicator.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    
    typingDiv.appendChild(indicator);
    chatMessages.appendChild(typingDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function formatMessage(message) {
    // Split message into paragraphs
    let paragraphs = message.split('\n\n');
    let formatted = '';
    
    paragraphs.forEach((paragraph, index) => {
        paragraph = paragraph.trim();
        if (paragraph === '') return;
        
        // Check if paragraph contains bullet points
        if (paragraph.includes('\n- ')) {
            const lines = paragraph.split('\n');
            let listItems = [];
            let currentParagraph = '';
            
            lines.forEach(line => {
                line = line.trim();
                if (line.startsWith('- ')) {
                    if (currentParagraph) {
                        formatted += `<p>${formatText(currentParagraph)}</p>`;
                        currentParagraph = '';
                    }
                    listItems.push(formatText(line.substring(2)));
                } else if (line !== '') {
                    if (listItems.length > 0) {
                        formatted += `<ul>${listItems.map(item => `<li>${item}</li>`).join('')}</ul>`;
                        listItems = [];
                    }
                    currentParagraph += (currentParagraph ? ' ' : '') + line;
                }
            });
            
            if (currentParagraph) {
                formatted += `<p>${formatText(currentParagraph)}</p>`;
            }
            if (listItems.length > 0) {
                formatted += `<ul>${listItems.map(item => `<li>${item}</li>`).join('')}</ul>`;
            }
        } else {
            // Regular paragraph, just replace single newlines with <br>
            const formattedParagraph = paragraph.replace(/\n/g, '<br>');
            formatted += `<p>${formatText(formattedParagraph)}</p>`;
        }
    });
    
    return formatted || `<p>${formatText(message)}</p>`;
}

// New function to format text with bold and italic
function formatText(text) {
    // Convert **text** to <strong>text</strong> (bold)
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *text* to <em>text</em> (italic)
    text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    return text;
}

// Update addMessageToChat to accept a timestamp parameter
function addMessageToChat(message, isUser, timestamp = null) {
    const chatMessages = document.getElementById('chat-messages');
    
    // Remove welcome message if it exists
    const welcomeMessage = chatMessages.querySelector('.text-center');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `mb-4 ${isUser ? 'text-right' : 'text-left'}`;
    
    const bubble = document.createElement('div');
    bubble.className = `message-bubble inline-block px-4 py-2 rounded-lg ${isUser ? 'user-message' : 'ai-message'}`;
    
    // Format the message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    if (isUser) {
        // For user messages, preserve line breaks but keep it simple
        contentDiv.innerHTML = message.replace(/\n/g, '<br>');
    } else {
        // For AI messages, apply full formatting
        contentDiv.innerHTML = formatMessage(message);
    }
    
    bubble.appendChild(contentDiv);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = `text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`;
    
    // Use provided timestamp or current time
    const displayTime = timestamp ? new Date(timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
    timeDiv.textContent = displayTime;
    
    messageDiv.appendChild(bubble);
    messageDiv.appendChild(timeDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/messages`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const messages = await response.json();
            const chatMessages = document.getElementById('chat-messages');
            
            // Clear current messages
            chatMessages.innerHTML = '';
            
            if (messages.length === 0) {
                // Show welcome message
                chatMessages.innerHTML = `
                    <div class="text-center text-gray-500">
                        <i class="fas fa-star text-2xl mb-2"></i>
                        <p>Welcome to your personalized astrology chat! Ask me anything about your birth chart, zodiac sign, or astrology in general.</p>
                    </div>
                `;
            } else {
                // Display chat history
                messages.forEach(msg => {
                    // Display user message
                    if (msg.message) {
                        addMessageToChat(msg.message, true, msg.created_at);
                    }
                    // Display AI response
                    if (msg.response) {
                        addMessageToChat(msg.response, false, msg.created_at);
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

function clearChat() {
    const chatMessages = document.getElementById('chat-messages');
    chatMessages.innerHTML = `
        <div class="text-center text-gray-500">
            <i class="fas fa-star text-2xl mb-2"></i>
            <p>Welcome to your personalized astrology chat! Ask me anything about your birth chart, zodiac sign, or astrology in general.</p>
        </div>
    `;
}

// Logout function
function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    currentUser = null;
    showLogin();
    
    // Clear any messages
    document.getElementById('login-message').innerHTML = '';
    document.getElementById('register-message').innerHTML = '';
    document.getElementById('update-message').innerHTML = '';
}

// Utility function to show messages
function showMessage(elementId, message, isError = false) {
    const element = document.getElementById(elementId);
    const className = isError ? 'text-red-600' : 'text-green-600';
    element.innerHTML = `<p class="${className}">${message}</p>`;
}

// Add active class styling
document.addEventListener('DOMContentLoaded', function() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            navButtons.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
        });
    });
});
