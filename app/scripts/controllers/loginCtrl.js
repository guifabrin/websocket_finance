import HttpStatus from '../helpers/HttpStatus';

export default function ($scope, $mdDialog) {

    $scope.user = {
        username: '',
        password: ''
    }

    $scope.valid = ($errors) => {
        return Object.keys($errors).length === 0
    }

    $scope.login = () => {
        fetch('/api/v1/auth', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify($scope.user)
        }).then(response => {
            if (response.status == HttpStatus.OK) {
                response.json().then(uuid => {
                    localStorage.setItem('auth', btoa(`${$scope.user.username}:${uuid}`))
                    window.location.href = "/feed";
                })
            } else {
                response.json().then(json => {
                    $mdDialog.show(
                        $mdDialog.alert()
                            .clickOutsideToClose(true)
                            .title('Error')
                            .textContent(json.message)
                            .ok('Got it!')
                    );
                    $scope.creating = false;
                    $scope.$apply();
                })
            }
        })
    }
}