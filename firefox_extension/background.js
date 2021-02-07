console.log("background init");
/** user modifable items */
const ContainerTabName = "Music Youtube2";
const ContainerId = "firefox-container-6";
let portFromCS;


function connected(p) {
    portFromCS = p;
    portFromCS.onMessage.addListener(async function(m) {
        console.log(m);
        if (typeof m === 'object' && m.function === "checkPermission") {
            const tab = (await browser.tabs.query({currentWindow: true, active: true}))[0];
            const cookieStoreId = tab.cookieStoreId;
            console.log("getting for cookiestoreid of " + cookieStoreId);
            const permission = await checkPermission(cookieStoreId);
            console.log("got permission? " + permission);
            portFromCS.postMessage({"permission": permission});
        } else {
            portFromCS.postMessage({greeting: "In background script, received message from content script:" + m});
        }
    });
}

async function checkPermission(cookieId) {
    try{
        const identities = await browser.contextualIdentities.query({name: ContainerTabName});
        if(!identities || identities.length === 0) {
            console.error(`No identity could be found by the name ${ContainerTabName}`);
            return false;
        }
        const identity = identities[0];
        console.log("found identity.");
        console.log(identity.cookieStoreId);
        return cookieId === identity.cookieStoreId; /* given id vs white-listed identity id */
    }
    catch (err) {
        console.error("Failed to check container permission:")
        console.log(err);
        return false;
    }
}

console.log("functions generated");

browser.runtime.onConnect.addListener(connected);
console.log("browser runtime connection added");





