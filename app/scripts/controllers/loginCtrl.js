import HttpStatus from '../helpers/HttpStatus';
import md5 from 'md5'

export default function ($scope, $mdDialog) {

    $scope.user = {
        username: '',
        password: ''
    }

    $scope.valid = ($errors) => {
        return Object.keys($errors).length === 0
    }

    $scope.login = () => {
        fetch(`/api/v1/users/${$scope.user.username}`).then((response) => {
            if (response.status == HttpStatus.OK) {
                response.json().then((user) => {
                    if (user.password == md5($scope.user.password)) {
                        window.location.href = "/feed";
                    } else {
                        $mdDialog.show(
                            $mdDialog.alert()
                                .clickOutsideToClose(true)
                                .title('Error')
                                .textContent('Wrong password')
                                .ok('Got it!')
                        );
                    }
                });
            } else {
                response.json().then((json) => {
                    $mdDialog.show(
                        $mdDialog.alert()
                            .clickOutsideToClose(true)
                            .title('Error')
                            .textContent(json.message)
                            .ok('Got it!')
                    );
                })
            }
        })
    }
}