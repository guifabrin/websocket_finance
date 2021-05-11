module.exports = function ($scope) {
    $scope.user = {
        username: '',
        password: '',
        confirm_password: ''
    };

    $scope.create = () => {
        if ($scope.password != $scope.confirm_password) {
            alert('Password and confirm password must be the same.');
            return;
        }
    }
};