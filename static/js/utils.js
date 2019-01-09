var utils = utils || {};

/**
 * Get data form server, similar to jQuery but is with cache
 */
utils.get = function (url) {
    // find items in cached data
    var cachedResponse = sessionStorage.getItem(url);
    if (cachedResponse !== undefined && cachedResponse) {
        var response = JSON.parse(cachedResponse);
        if (typeof callback === 'function') {
            callback(response);
        }
        return;
    }

    // query from server
    return $.get(url, function (data) {
        if (!data) {
            console.log('Receive empty response from ' + url);
            return;
        }

        // store to cache
        var stringifiedResponse = JSON.stringify(data);
        sessionStorage.setItem(url, stringifiedResponse)
    });

};
