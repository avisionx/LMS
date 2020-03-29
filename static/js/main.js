function fetchData(url, callback) {
    $.ajax({
        type: 'get',
        url: url,
        success: (data) => {
            callback(data);
        },
        error: (response, error) => {
            console.log(error);
        }
    });
}