// index.js (Your main bot file)

// ... (your other requires like Client, GatewayIntentBits)
const { Client, GatewayIntentBits, Partials } = require('discord.js');
require('dotenv').config();


const {
    joinVoiceChannel,
    createAudioPlayer,
    createAudioResource,
    AudioPlayerStatus,
    getVoiceConnection
} = require('@discordjs/voice');
const path = require('path')

const nodeRed = require('./nodeRedClient.js');

const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.MessageContent,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.GuildMembers,
    ],
    partials: [Partials.Channel]
});

client.once('ready', () => {
    nodeRed.setValue("botStatus", true);
    console.log(`Ready! Logged in as ${client.user.tag}`);
});

client.on('messageCreate', async message => {
    console.log(`[DEBUG] Received message from ${message.author.tag}: "${message.content}"`);
    if (message.author.bot) return;

    const prefix = '!';
    if (!message.content.startsWith(prefix)) return;

    // Remove the prefix and split the command into args
    const args = message.content.slice(prefix.length).trim().split(/ +/);
    const command = args.shift().toLowerCase();

    // --- !set command ---
    // Usage: !set <key> <value>
    if (command === 'set') {
        if (args.length < 2) {
            return message.reply('Please provide a key and a value. Usage: `!set mykey myvalue`');
        }
        const key = args[0];
        const value = args.slice(1).join(' '); // Re-join the rest as the value

        const response = await nodeRed.setValue(key, value);

        if (response.status === 'success') {
            message.reply(`✅ Successfully set the value for \`${key}\`.`);
        } else {
            message.reply(`❌ Failed to set value. Node-RED said: ${response.message}`);
        }
    }

    // --- !get command ---
    // Usage: !get <key>
    if (command === 'get') {
        if (args.length < 1) {
            return message.reply('Please provide a key. Usage: `!get mykey`');
        }
        const key = args[0];

        const response = await nodeRed.getValue(key);

        if (response.status === 'success') {
            // The value can be an object, so we stringify it for display
            const valueStr = JSON.stringify(response.value);
            message.reply(`🔍 The value for \`${response.key}\` is: \`${valueStr}\``);
        } else {
            message.reply(`❌ Could not get value. Node-RED said: ${response.message}`);
        }
    }

    if (command === 'hello') {
        // 1. Check if the user is in a voice channel
        const voiceChannel = message.member.voice.channel;
        if (!voiceChannel) {
            return message.reply('You need to be in a voice channel before use this command!');
        }

        // 2. Check for permissions to join and speak
        const permissions = voiceChannel.permissionsFor(message.client.user);
        if (!permissions.has('CONNECT') || !permissions.has('SPEAK')) {
            return message.reply('I need permissions to join and speak in your voice channel!');
        }

        try {
            // 3. Join the voice channel
            const connection = joinVoiceChannel({
                channelId: voiceChannel.id,
                guildId: voiceChannel.guild.id,
                adapterCreator: voiceChannel.guild.voiceAdapterCreator,
            });

            // 4. Create an audio player and resource
            const player = createAudioPlayer();
            const resource = createAudioResource(path.join(__dirname, 'audio/hello.mp3'));

            // 5. Play the audio
            player.play(resource);
            connection.subscribe(player);
            const freshMember = await voiceChannel.guild.members.fetch(message.member.id);
            message.reply(`Saying hello to ${freshMember.displayName} at **${voiceChannel.name}**!`);

            // 6. Set up an event listener for when the audio finishes
            player.on(AudioPlayerStatus.Idle, () => {
                console.log('Audio has finished playing, disconnecting.');
                connection.destroy(); // Disconnect from the channel
            });

            // (Optional) Add an error handler
            player.on('error', error => {
                console.error(`Error playing audio: ${error.message}`);
                connection.destroy(); // Disconnect on error
            });

        } catch (error) {
            console.error(error);
            message.reply('There was an error trying to play the sound!');
        }
    }
});

// --- Dynamic Voice Channel Handler (with Auto-Delete) ---
client.on('voiceStateUpdate', async (oldState, newState) => {
    // --- Define Configuration ---
    const generatorChannelName = '➕ Create Channel';
    const tempVoiceCategoryName = '═══════ temp voice ═══════';
    const targetVoiceCategoryName = '════════ VOICE ════════';

    //================================================================================
    // DELETION LOGIC: Check if a user left a channel
    //================================================================================
    if (oldState.channel) {
        const channelLeft = oldState.channel;
        const category = channelLeft.parent;

        // Check if the channel left is a temporary one and is now empty
        if (
            category &&
            category.name === targetVoiceCategoryName && // Is it in the target voice category?
            channelLeft.members.size === 0 &&             // Is it empty?
            channelLeft.name.endsWith("'s Room")          // Does it match our naming convention?
        ) {
            console.log(`[DELETE_CHECK] Empty temp channel found: "${channelLeft.name}". Deleting...`);
            try {
                const channelName = channelLeft.name; // Store name for logging after deletion
                await channelLeft.delete();
                console.log(`[SUCCESS] Deleted empty channel: "${channelName}".`);
            } catch (error) {
                console.error(`[ERROR] Failed to delete channel "${channelLeft.name}":`, error);
            }
        }
    }

    //================================================================================
    // CREATION LOGIC: Check if a user joined the generator channel
    //================================================================================
    const channelJoined = newState.channel;
    if (channelJoined) {
        const category = channelJoined.parent;
        // Check if the channel joined is the generator
        if (channelJoined.name === generatorChannelName && category && category.name === tempVoiceCategoryName) {
            
            console.log(`[CREATE_CHECK] User ${newState.member.user.tag} joined the generator channel.`);
            
            try {
                // Fetch fresh member data for the most up-to-date nickname
                const freshMember = await newState.guild.members.fetch(newState.member.id);

                const targetCategory = newState.guild.channels.cache.find(
                    c => c.name === targetVoiceCategoryName && c.type === 4 // GuildCategory
                );

                if (!targetCategory) {
                    console.error(`[ERROR] Creation failed: Could not find target category "${targetVoiceCategoryName}"`);
                    return;
                }

                const displayName = freshMember.displayName;
                
                const newChannel = await newState.guild.channels.create({
                    name: `${displayName}'s Room`,
                    type: 2, // GuildVoice
                    parent: targetCategory.id,
                    bitrate: channelJoined.bitrate,
                    userLimit: 4,
                    permissionOverwrites: channelJoined.permissionOverwrites.cache.map(overwrite => ({
                        id: overwrite.id,
                        allow: overwrite.allow.toArray(),
                        deny: overwrite.deny.toArray()
                    }))
                });

                console.log(`[SUCCESS] Created channel "${newChannel.name}".`);
                await freshMember.voice.setChannel(newChannel);
                console.log(`[SUCCESS] Moved ${freshMember.user.tag}.`);

            } catch (error) {
                console.error('[FATAL_ERROR] An error occurred during channel creation:', error);
            }
        }
    }
});

client.login(process.env.DISCORD_TOKEN);