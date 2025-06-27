# RainBowBot

## features
### simple discord !set and !get command that stored in node-red flow.<key>
### create temporary voice channel

## required

 ``node``, ``npm``

simple ``node-red`` server

## setup

### on node-red server
import
```
[
    {
        "id": "e8d9c2a7.d2f8f",
        "type": "http in",
        "z": "f7e5b5e7.c1d688",
        "name": "POST /set",
        "url": "/set",
        "method": "post",
        "upload": false,
        "swaggerDoc": "",
        "x": 160,
        "y": 660,
        "wires": [
            [
                "a1b2c3d4.e5f6g7"
            ]
        ]
    },
    {
        "id": "a1b2c3d4.e5f6g7",
        "type": "function",
        "z": "f7e5b5e7.c1d688",
        "name": "Set value in context",
        "func": "// Get key and value from the request body (msg.payload)\nconst key = msg.payload.key;\nconst value = msg.payload.value;\n\n// Basic validation\nif (!key) {\n    msg.statusCode = 400; // Bad Request\n    msg.payload = { status: 'error', message: 'Key is missing.' };\n    return msg;\n}\n\n// Store the value in flow context\nflow.set(key, value);\n\n// Prepare success response\nmsg.statusCode = 200;\nmsg.payload = { status: 'success', message: `Value for key '${key}' has been set.` };\n\nreturn msg;",
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 370,
        "y": 660,
        "wires": [
            [
                "b5c6d7e8.f9a0b1",
                "c9d0e1f2.a3b4c5"
            ]
        ]
    },
    {
        "id": "b5c6d7e8.f9a0b1",
        "type": "http response",
        "z": "f7e5b5e7.c1d688",
        "name": "Send Response",
        "statusCode": "",
        "headers": {},
        "x": 590,
        "y": 700,
        "wires": []
    },
    {
        "id": "c9d0e1f2.a3b4c5",
        "type": "debug",
        "z": "f7e5b5e7.c1d688",
        "name": "Log",
        "active": true,
        "tosidebar": true,
        "console": false,
        "tostatus": true,
        "complete": "payload.message",
        "targetType": "msg",
        "statusVal": "payload.message",
        "statusType": "msg",
        "x": 550,
        "y": 620,
        "wires": []
    },
    {
        "id": "d7e8f9a0.b1c2d3",
        "type": "http in",
        "z": "f7e5b5e7.c1d688",
        "name": "GET /get/:key",
        "url": "/get/:key",
        "method": "get",
        "upload": false,
        "swaggerDoc": "",
        "x": 170,
        "y": 740,
        "wires": [
            [
                "f1g2h3i4.j5k6l7"
            ]
        ]
    },
    {
        "id": "f1g2h3i4.j5k6l7",
        "type": "function",
        "z": "f7e5b5e7.c1d688",
        "name": "Get value from context",
        "func": "// The key is part of the URL, available in msg.req.params\nconst key = msg.req.params.key;\n\n// Retrieve the value from flow context\nconst value = flow.get(key);\n\nif (value === undefined) {\n    msg.statusCode = 404; // Not Found\n    msg.payload = { status: 'error', key: key, message: 'Key not found.' };\n} else {\n    msg.statusCode = 200;\n    msg.payload = { status: 'success', key: key, value: value };\n}\n\nreturn msg;",
        "outputs": 1,
        "noerr": 0,
        "initialize": "",
        "finalize": "",
        "libs": [],
        "x": 380,
        "y": 740,
        "wires": [
            [
                "b5c6d7e8.f9a0b1",
                "c9d0e1f2.a3b4c5"
            ]
        ]
    }
]
```
and simply ``Deploy``

## on npm server

``git clone https://github.com/RainBowCreation/RainBowBot.git``

``cd RainBowBot``

``npm install -y``

create a simple .env with 2 keys
```
DISCORD_TOKEN=YOURDISCORD_TOKEN
NODE_RED_URL=YOURNODE_RED_URL
```

the discord server need 2 category 1 must named.
``═══════ temp voice ═══════``

with a channel that set the user limit to ``1`` named `➕ Create Channel`.

you also need 1 empty category named ``════════ VOICE ════════`` that the new vc will be created to.

to start run ``node ./index.js``

## discord usages
``!set <key> <value>`` to set value to node-red flow
``!get <key>`` return value of provided key with http status code