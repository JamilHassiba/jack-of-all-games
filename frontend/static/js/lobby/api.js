// Shared helper for posting form data to the Flask backend.

// @Author Thomas McPhee
// This is very bad, it is copied from utils.js
// Ideally we should be importing frmo utils.js, but given this js is in <script> - we can't do that
export async function SendData(route, data) {
    const formData = new FormData();

    for (const [key, value] of Object.entries(data)) {
        formData.append(key, value);
    }

    let response = await fetch(route, { method: "POST", body: formData })
    response = await response.text()

    try {
        return await JSON.parse(response)
    } catch (error) {

        return await response
    }
}
