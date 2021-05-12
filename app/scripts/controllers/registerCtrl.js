import HttpStatus from '../helpers/HttpStatus';

export default function ($scope, $mdDialog) {
    $scope.user = {
        username: '',
        password: '',
        confirm_password: ''
    };

    $scope.valid = ($errors) => {
        return !$scope.creating && Object.keys($errors).length === 0
    }
    $scope.creating = false;
    $scope.create = () => {
        $scope.creating = true;
        const objUser = JSON.parse(JSON.stringify($scope.user))
        delete objUser.confirm_password;
        fetch('/api/v1/users', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(objUser)
        }).then(response => {
            if (response.status == HttpStatus.OK) {
                window.location.href = "/login?message=User created";
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
};