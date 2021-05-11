export default function ($q) {
    return {
        require: 'ngModel',
        link: function ({ }, { }, { }, control) {
            control.$asyncValidators.unique_username = function (username) {
                if (username.length < 5) {
                    return $q.resolve();
                }
                var def = $q.defer();
                fetch('/api/v1/users').then((response) => response.json()).then((arrUsers) => {
                    if (arrUsers.map(user => user.username).includes(username)) {
                        def.reject();
                    } else {
                        def.resolve();
                    }
                });
                return def.promise;
            };
        }
    };
}