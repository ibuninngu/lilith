function post(DATA, HEADERS, TARGET, METHOD) {
    const data = DATA;
    const headers = HEADERS;
    return fetch(TARGET, { method: METHOD, body: data, headers: headers }).then(response => { return response.text(); });
}