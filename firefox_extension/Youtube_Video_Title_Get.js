
(function() {
    'use strict';

    console.log("AYYYY");

    // /* user modifable items */
    let sendUrl = "http://127.0.0.1:8000/api/send_song";
    let signingKeyB64 = "zphbG1sXK5Ebndyq5ey+IdYfM1CAQSGUR0WCBI52EKL6EBCdNcTmBpn+NFYS6qXDIeEBh8sBFUiLPCpZjgzhVY94SQStRYHJ7Y8pGtzGUdJFZpSuPA0GL87VKWM4YhgncC4hBY8+gIOq6KWQMAAlvUZBWg6sdo0qmsBxCPr0J0w="
    
    let cryptoKey = null;
    const encoder = new TextEncoder();
    async function makeCryptoKey(b64Key) {
        const arrBuff = Base64Binary.base64ToArrayBuffer(b64Key);
        console.log(arrBuff);
        cryptoKey = await crypto.subtle.importKey("raw", arrBuff, {"name": "HMAC", hash: "SHA-512"}, true, ["sign", "verify"]);
    }

    let permission = false;
    let mutObserver = null;
    const videoIdRegex = new RegExp("v=([a-zA-Z0-9]*?)($|&)");

    /** Send message to Background Script  */
    let myPort = browser.runtime.connect({name:"port-from-cs"});

    myPort.onMessage.addListener(function(m) {
        if (typeof m === 'object' && m.hasOwnProperty("permission")) {
            console.log(m);
            permission = m.permission;
            console.log("Got permission: " + permission);
            if (permission) {
                setInterval(() => {
                    console.log("Sending update to server...");
                    reload(false);
                    send();
                }, 10 * 1000);
                mutObserver = new MutationObserver(function(mutations) {
                    reload(true);
                }).observe(
                    document.querySelector('title'),
                    { subtree: true, characterData: true, childList: true }
                );
            }
        }
        else {
            console.log("got wrong data:");
            console.log(m);
        }
    });

 
    // Your code here...
    let title = document.title;
    let vid = null;
    let reloaded_at = 0;
    let vidId = null;
    let sendObj = null;
    /** Keep track of if our last udpate was a Paused update. If we have two pauses in a row, we don't have to send data  */
    let lastSendWasPlaying = true;

    function getVideoId() {
        const matches = videoIdRegex.exec(window.location);
        if (matches.length > 1) {
            return matches[1];
        }
        return null;
    }

    function getSendObj() {
        vidId = getVideoId();
        let sendObj = {
            data: {
                item: {
                    id: vidId,
                    name: document.title,
                    main_link: window.location.toString(),
                    main_image: vidId ? `https://img.youtube.com/vi/${vidId}/0.jpg` : "",
                    duration_ms: Math.ceil(vid.duration*1000), /* duration is in ms to match with Spotify's `duration_ms` field */
                    album: null,
                    artists: null,
                    is_local: false,
                    preview_url: false,
                    href: window.location.toString(),
                },
                kind: "youtube",
                timestamp: reloaded_at,
                is_playing: isPlaying(),
                progress_ms:  Math.ceil(vid.currentTime * 1000), /* ms to match with Spotify's `progress_ms` */
            },
            signature: "",
        };
        return sendObj;
    }

    function reload(refresh_time) {
        if (refresh_time) {
            reloaded_at = Math.ceil(Date.now() / 1000);
        }
        const vids = document.getElementsByTagName("video");
        vid = null;
        if (vids && vids.length > 0) {
            vid = vids[0];
        }

        vidId = getVideoId();
        sendObj = getSendObj();

        console.log("Is playing?: " + sendObj.data.is_playing);

        if (vid) {
            vid.onplay = onPlay;
            vid.onpause = onPause;
            vid.onended = onEnd;
            send();
        }
    }

    function onPlay() {
        sendObj.data.isPlaying = true;
        console.log("ON PLAYING");
        send();
    }

    function onPause() {
        sendObj.data.isPlaying = false;
        console.log("ON PAUSING");
        send();
    }

    function onEnd() {
        sendObj.data.isPlaying = false;
        console.log("ON END");
        send();
    }

    function isPlaying() {
        if (vid && vid.readyState >= vid.HAVE_FUTURE_DATA) {
            return !vid.paused;
        }
        return false;
    }

    async function send() {
        if (permission) {
            if (!lastSendWasPlaying && !sendObj.data.is_playing) {
                /* don't send data if this send is paused, and last send was paused */
                console.log("skipping sending data because last one and this one were paused");
                return;
            }
            lastSendWasPlaying = sendObj.data.isPlaying;

            const signature_object = await crypto.subtle.sign("HMAC", cryptoKey, encoder.encode(sendObj.data));
            console.log(signature_object);
            sendObj.signature = await Base64Binary.arrayBufferToBase64(signature_object);
            console.log(sendObj);
            const response = await fetch(sendUrl, {
                method: 'POST',
                mode: 'no-cors', // no-cors, *cors, same-origin
                cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
                credentials: 'omit', // include, *same-origin, omit
                headers: {
                    'Content-Type': 'application/json'
                },
                redirect: 'follow', // manual, *follow, error
                referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
                body: JSON.stringify(sendObj) // body data type must match "Content-Type" header
            });
            console.log(response);
        }
    }


    async function main() {
        reload(true);
        console.log("making crypto key");
        await makeCryptoKey(signingKeyB64); /* needed for signing our requests */
        /* post the message, all other functions flow from the receive message function */
        console.log("checking tab permission");
        myPort.postMessage({function: "checkPermission"});
    }

    main();


})();
