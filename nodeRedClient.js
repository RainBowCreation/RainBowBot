// nodeRedClient.js

require('dotenv').config();
const axios = require('axios'); // Use the standard axios import

// Ensure you have NODE_RED_URL in your .env file
const NODE_RED_URL = process.env.NODE_RED_URL || 'http://127.0.0.1:1880';

/**
 * Sets a value in Node-RED by sending a POST request.
 * @param {string} key - The key under which to store the value.
 * @param {any} value - The value to store (can be a string, number, object, etc.).
 * @returns {Promise<object>} A promise that resolves to the response data from Node-RED.
 */
async function setValue(key, value) {
    try {
        const endpoint = `${NODE_RED_URL}/set`;
        console.log(`Sending POST to ${endpoint} with key: ${key}`);

        // The response will contain the data sent back by the Node-RED flow
        const response = await axios.post(endpoint, {
            key: key,
            value: value
        });

        return response.data; // e.g., { status: 'success', key: 'mykey' }
    } catch (error) {
        console.error(`Error in setValue for key "${key}":`, error.message);
        // Return an error object for the bot to handle
        return { status: 'error', message: error.message };
    }
}

/**
 * Gets a value from Node-RED by sending a GET request.
 * @param {string} key - The key of the value to retrieve.
 * @returns {Promise<object>} A promise that resolves to the response data from Node-RED.
 */
async function getValue(key) {
    try {
        // We append the key to the URL path, which is a common REST practice
        const endpoint = `${NODE_RED_URL}/get/${key}`;
        console.log(`Sending GET to ${endpoint}`);

        const response = await axios.get(endpoint);

        return response.data; // e.g., { status: 'success', key: 'mykey', value: 'someValue' }
    } catch (error) {
        console.error(`Error in getValue for key "${key}":`, error.message);
        // Return an error object for the bot to handle
        return { status: 'error', message: error.message };
    }
}

// Export the functions using CommonJS so they can be used with require()
module.exports = { setValue, getValue };