// Shared helper for posting form data to the Flask backend.

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
