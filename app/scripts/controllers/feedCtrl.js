
import HttpStatus from '../helpers/HttpStatus';

export default function ($scope) {
    $scope.posts = [];
    $scope.update = () => {
        fetch('/api/v1/posts', {
            headers: { Authorization: localStorage.getItem('auth') }
        }).then((response) => {

            if (response.status == HttpStatus.OK) {
                response.json().then((arrPosts) => {
                    $scope.posts = arrPosts;
                    $scope.$apply();
                });
            } else {
                localStorage.removeItem('auth')
                window.location.href = "/login";
            }
        })
    }
    $scope.update();
}