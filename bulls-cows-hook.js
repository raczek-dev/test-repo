// Bulls & Cows Game Hook for OpenClaw
// Intercepts game commands and responds instantly without waking the agent

const GAME_API_URL = "http://localhost:8765";
const CHAT_ID = "73182477"; // Lukasz's chat ID

// Game commands that should be handled by this hook
const GAME_COMMANDS = ['/startgame', '/hint', '/status', '/help'];
const GUESS_PATTERN = /^\d{4}$/;

export default async function transform(payload) {
  try {
    // Only handle Telegram messages
    if (payload?.channel !== 'telegram') {
      return null;
    }
    
    const messageText = payload?.text?.trim() || '';
    const chatId = String(payload?.chat?.id || payload?.from?.id || '');
    
    // Only handle messages from Lukasz's chat
    if (chatId !== CHAT_ID) {
      return null;
    }
    
    // Check if it's a game command or guess
    const isGameCommand = GAME_COMMANDS.includes(messageText.toLowerCase());
    const isGuess = GUESS_PATTERN.test(messageText);
    
    if (!isGameCommand && !isGuess) {
      return null; // Let agent handle non-game messages
    }
    
    console.log(`[bulls-cows] Handling: ${messageText}`);
    
    // Call the game API
    let response;
    
    if (messageText.toLowerCase() === '/startgame') {
      response = await callApi('/game/start', { chat_id: chatId });
    } else if (messageText.toLowerCase() === '/status') {
      response = await fetch(`${GAME_API_URL}/game/status/${chatId}`).then(r => r.json());
    } else if (isGuess) {
      response = await callApi('/game/guess', { chat_id: chatId, guess: messageText });
    } else {
      // For other commands, show help
      response = {
        message: "🎮 *BULLS & COWS*\n\nCommands:\n• /startgame - New game\n• /hint - Get hint\n• /status - Show status\n• Send 4 digits to guess"
      };
    }
    
    return {
      action: "reply",
      text: response.message,
      deliver: true,
      channel: "telegram",
      to: chatId
    };
    
  } catch (e) {
    console.log(`[bulls-cows] error: ${e?.message || String(e)}`);
    return null; // Fall back to agent on error
  }
}

async function callApi(endpoint, body) {
  const response = await fetch(`${GAME_API_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return response.json();
}
