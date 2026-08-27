const API_BASE_URL = "http://127.0.0.1:8000";


/*
=========================================================
GET REQUEST
=========================================================
*/

async function apiGet(endpoint) {

    try {

        const response = await fetch(
            `${API_BASE_URL}${endpoint}`
        );


        if (!response.ok) {

            throw new Error(
                `API Error: ${response.status}`
            );

        }


        return await response.json();

    }

    catch (error) {

        console.error(
            "API request failed:",
            error
        );

        throw error;

    }

}


/*
=========================================================
BACKEND STATUS
=========================================================
*/

async function checkBackend() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/`
            );

        return response.ok;

    }

    catch {

        return false;

    }

}