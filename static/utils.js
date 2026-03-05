export async function SendData(route, data) {
	const formData = new FormData();

	for (const [key, value] of Object.entries(data)) {
	  formData.append(key, value);
	}

	let response = await fetch(route, {method: "POST", body: formData})
	response = await response.text()

	try {
		return await JSON.parse(response)
	} catch (error) {

		return await response
	}
}

// calls the /game_state route on the server
// returns the data
export async function GetGameState() {
    const res = await fetch("/game_state");
    const data = await res.json();
    console.log(data);

    return data
}
