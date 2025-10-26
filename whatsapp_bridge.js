#!/usr/bin/env node
/**
 * WhatsApp Bridge - Node.js bridge dla Python bota
 * Używa whatsapp-web.js do komunikacji z WhatsApp
 */

const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

// Create WhatsApp client
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

// QR Code handler
client.on('qr', (qr) => {
    console.log(JSON.stringify({
        type: 'qr',
        qr: qr
    }));
    
    // Also display QR code in terminal
    qrcode.generate(qr, { small: true });
});

// Ready handler
client.on('ready', () => {
    console.log(JSON.stringify({
        type: 'ready',
        message: 'WhatsApp Bot is ready!'
    }));
});

// Message handler
client.on('message', async (message) => {
    try {
        // Skip messages from groups and status messages
        if (message.from.includes('@g.us') || message.from.includes('status@broadcast')) {
            return;
        }
        
        // Skip messages from the bot itself
        if (message.fromMe) {
            return;
        }
        
        // Send message data to Python bot
        console.log(JSON.stringify({
            type: 'message',
            message: message.body,
            sender: message.from,
            chatId: message.from,
            timestamp: message.timestamp
        }));
        
    } catch (error) {
        console.error('Error handling message:', error);
    }
});

// Error handler
client.on('error', (error) => {
    console.error('WhatsApp Client Error:', error);
});

// Listen for messages from Python bot
process.stdin.on('data', async (data) => {
    try {
        const command = JSON.parse(data.toString().trim());
        
        if (command.type === 'send') {
            await client.sendMessage(command.chatId, command.message);
        }
        
    } catch (error) {
        console.error('Error processing command:', error);
    }
});

// Initialize client
client.initialize();

// Handle process termination
process.on('SIGINT', async () => {
    console.log('Shutting down WhatsApp client...');
    await client.destroy();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('Shutting down WhatsApp client...');
    await client.destroy();
    process.exit(0);
});
